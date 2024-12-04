from xmlrpc.client import MAXINT
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
import sqlalchemy
from sqlalchemy.exc import NoResultFound
import logging
from src import database as db
from src.api import auth
import math
from geopy.distance import geodesic

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/shopping",
    tags=["shopping"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/route_optimize", status_code=status.HTTP_200_OK)
def optimize_shopping_route(
    user_id: int,
    food_id: int,
    budget: int = Query(0, ge=0, description="Budget in cents, must be greater than or equal to 0")
):

    """
    Finds nearby stores with a given food_id.
    If a budget is specified (greater than 0), only stores offering the food item within the budget are considered.
    Otherwise, the closest store to the user with the valid food item is selected.
    """
    get_user_info_query = sqlalchemy.text("""
        SELECT longitude, latitude
        FROM users
        WHERE user_id = :user_id
    """)

    find_matching_store_ids_query = sqlalchemy.text(f"""
        SELECT longitude, latitude,
               store.name as store_name, store.store_id as store_id,
               catalog_item.price as price
        FROM store
        JOIN catalog ON catalog.store_id = store.store_id
        JOIN catalog_item ON catalog.catalog_id = catalog_item.catalog_id
        JOIN food_item ON food_item.food_id = catalog_item.food_id
        WHERE food_item.food_id = :food_id
        {"AND catalog_item.price <= :budget" if budget > 0 else ""}
    """)

    food_data = {"food_id": food_id, "budget": budget} if budget > 0 else {"food_id": food_id}

    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            try:
                user_info = conn.execute(get_user_info_query, {"user_id": user_id}).one()
            except NoResultFound as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User does not exist, {e}"
                )

            result = conn.execute(find_matching_store_ids_query, food_data)

    valid_stores = [
        {
            "name": row.store_name,
            "store_id": row.store_id,
            "price": row.price,
            "distance": geodesic((user_info.latitude, user_info.longitude), (row.latitude, row.longitude)).km
        }
        for row in result
    ]

    if not valid_stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stores found with the requested item"
        )

    # Get closest and best value stores
    valid_stores_by_distance = sorted(valid_stores, key=lambda store: store["distance"])
    closest_store = valid_stores_by_distance[0]

    valid_stores_by_price = sorted(valid_stores, key=lambda store: store["price"])
    best_value_store = valid_stores_by_price[0]

    return {
        "Closest Store": {
            "Name": closest_store["name"],
            "Store ID": closest_store["store_id"],
            "Distance Away": f"{closest_store['distance']:.2f} km",
            "Price of Item": f"${closest_store['price']/100:,.2f}"
        },
        "Best Value Store": {
            "Name": best_value_store["name"],
            "Store ID": best_value_store["store_id"],
            "Distance Away": f"{best_value_store['distance']:.2f} km",
            "Price of Item": f"${best_value_store['price']/100:,.2f}"
        }
    }


@router.get("/{user_id}/fulfill_list/{list_id}", status_code=status.HTTP_200_OK)
def fulfill_list(user_id: int, list_id: int,
                 budget: int = Query(MAXINT, 
                    description="Most willing you're to spend on an item in cents", gt=0),
                 max_dist: int = Query(10, description="Range in km", gt=0),
                 order_by: int = Query(1, 
                    description="Order by option: 1=price,distance; 2=price; 3=distance")):
    """
    Generate a list of the closest_stores to fufil a list
    currently there is a user input max price per budget
    """
    
    options = {
        1 : "price, distance",
        2 : "price",
        3 : "distance"
    }
    
    try:
        option = options[order_by]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order_by option"
        )
    
    find_items = sqlalchemy.text(f"""
        WITH they_got_it AS (
            SELECT 
                food_item.name AS item,
                store.name AS store_name, 
                store.store_id AS store_id,
                catalog_item.price AS price,
                ROUND((earth_distance(
                    ll_to_earth(store.latitude, store.longitude), 
                    ll_to_earth((SELECT latitude FROM users WHERE users.user_id = :user_id), 
                                (SELECT longitude FROM users WHERE users.user_id = :user_id))
                ) / 1000)::NUMERIC, 1)::FLOAT AS distance
            FROM store
            JOIN catalog ON catalog.store_id = store.store_id
            JOIN catalog_item ON catalog.catalog_id = catalog_item.catalog_id
            JOIN food_item ON food_item.food_id = catalog_item.food_id
            WHERE food_item.food_id IN (
                SELECT food_id
                FROM shopping_list_item
                WHERE list_id = :list_id
                )
                AND price < :budget
            ORDER BY item, {option}
        ),
        ranked_stores AS (
            SELECT  item, store_name, store_id, price, distance, 
                    RANK() OVER (PARTITION BY item ORDER BY {option}) AS ranks
            FROM they_got_it
            WHERE distance < :range
        )
        SELECT item, store_name, store_id, price, distance, ranks
        FROM ranked_stores
        WHERE ranks = 1
    """)
    
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            # block of checks before executing the big sql statement to catch errors
            try:
                conn.execute(sqlalchemy.text("""
                    SELECT 1 FROM users 
                    WHERE user_id = :user_id
                    """), {"user_id": user_id}).one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist.")

            try:
                conn.execute(sqlalchemy.text("""
                    SELECT 1 FROM shopping_list 
                    WHERE list_id = :list_id
                    """), {"list_id": list_id}).one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="List does not exist.")

            try:
                conn.execute(
                    sqlalchemy.text("""
                    SELECT 1 FROM shopping_list 
                    WHERE list_id = :list_id AND user_id = :user_id
                    """),{"user_id": user_id, "list_id": list_id}).one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="User is not associated with this list.")
            
            shopping_list = conn.execute(find_items, 
                                        {"user_id": user_id,
                                        "list_id": list_id,
                                        "budget": budget,
                                        "range": max_dist})

    
    return_list = []
    for item in shopping_list:
        return_list.append({
            "Name": item.store_name,
            "Store ID": item.store_id,
            "Distance Away": f"{item.distance} km",
            "Item": item.item,
            "Price of Item": f"${item.price / 100:.2f}"
            
        })
    if not return_list:  # Check if the list is empty
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No stores found with given parameters.")
    return return_list


@router.get("{user_id}/find_snack/{food_id}", status_code=status.HTTP_200_OK)
def find_snack(user_id: int, food_id: int,
                max_dist: int = Query(10, description="Range in km", gt=0),
                order_by: int = Query(3, description="Order by option: 1=price,distance; 2=price; 3=distance")):
    """
    Lookin for a quick snack, just put in your food_id.
    We'll find you the closet place thats got what you want.
    Optional: find the cheapest place thats got what you want. 
    """
    options = {
        1 : "price, distance",
        2 : "price",
        3 : "distance"
    }
    
    try:
        option = options[order_by]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order_by option"
        )
    
    find_item = sqlalchemy.text(f"""
        WITH they_got_it AS (
            SELECT 
                food_item.name AS item,
                store.name AS store_name, 
                store.store_id AS store_id,
                catalog_item.price AS price,
                ROUND((earth_distance(
                    ll_to_earth(store.latitude, store.longitude), 
                    ll_to_earth((SELECT latitude FROM users WHERE users.user_id = :user_id), 
                                (SELECT longitude FROM users WHERE users.user_id = :user_id))
                ) / 1000)::NUMERIC, 1)::FLOAT AS distance
            FROM store
            JOIN catalog ON catalog.store_id = store.store_id
            JOIN catalog_item ON catalog.catalog_id = catalog_item.catalog_id
            JOIN food_item ON food_item.food_id = catalog_item.food_id
            WHERE food_item.food_id = :food_id
            ORDER BY item, {option}
        ),
        ranked_stores AS (
            SELECT  item, store_name, store_id, price, distance, 
                    RANK() OVER (PARTITION BY item ORDER BY {option}) AS ranks
            FROM they_got_it
            WHERE distance < :range
        )
        SELECT item, store_name, store_id, price, distance, ranks
        FROM ranked_stores
        WHERE ranks = 1
        LIMIT 1
    """)
    
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            try:
                store = conn.execute(find_item, 
                                             {"user_id": user_id,
                                              "food_id": food_id,
                                              "range": max_dist}).one()
            except NoResultFound:
                try:
                    conn.execute(sqlalchemy.text("SELECT 1 FROM users WHERE user_id = :user_id"),
                                 {"user_id": user_id}).one()
                except NoResultFound:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="User does not exist.")
                try:
                    conn.execute(sqlalchemy.text("SELECT 1 FROM food_item WHERE food_id = :food_id"),
                                 {"food_id": food_id}).one()
                except NoResultFound:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="Food_id does not exist.")

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No stores in range.")

    return_item = {
        "Name": store.store_name,
        "Store ID": store.store_id,
        "Distance Away": f"{store.distance} km",
        "Item": store.item,
        "Price of Item": f"${store.price / 100:.2f}"   
    }
    
    return return_item
