from xmlrpc.client import MAXINT
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
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


@router.post("/route_optimize", status_code=status.HTTP_200_OK)
def optimize_shopping_route(user_id: int, food_id: int, use_preferences: bool):
    """
    Finds nearby stores with given food_id. 
    If use_preferences is toggled to True, 
    then a user's budget will be accounted
    when a store is selected. 
    Otherwise, the closest store to the user with
    the valid food item is selected.
    """

    get_user_info_query = sqlalchemy.text("""
        SELECT longitude, latitude, budget
        FROM users
        LEFT JOIN preference ON users.user_id = preference.user_id                    
        WHERE users.user_id = :user_id
    """)

    find_matching_store_ids_query = sqlalchemy.text("""
        SELECT longitude, latitude,
        store.name as store_name, store.store_id as store_id,
        catalog_item.price as price

        FROM store

        JOIN catalog ON catalog.store_id = store.store_id
        JOIN catalog_item ON catalog.catalog_id = catalog_item.catalog_id
        JOIN food_item ON food_item.food_id = catalog_item.food_id
        WHERE food_item.food_id = :food_id
    """)

    food_data = {"food_id": food_id}
    
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            
            try:
                user_info = conn.execute(get_user_info_query, {"user_id": user_id}).one()
            except NoResultFound as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User does not exist, {e}"
                )

            # If using preferences, check if preferences exist
            if use_preferences and user_info.budget is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User preferences not set"
                )
                
            try:
                result = conn.execute(find_matching_store_ids_query, food_data)
            except NoResultFound as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Food item does not exist, {e}"
                )

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

    if not use_preferences:
        # Sort by distance and get closest store
        valid_stores.sort(key=lambda store: store["distance"])
        closest_store = valid_stores[0]
        return {
            "Closest Store": {
                "Name": closest_store["name"],
                "Store ID": closest_store["store_id"],
                "Distance Away": f"{closest_store['distance']:.2f} km",
                "Price of Item": f"${closest_store['price'] / 100:.2f}"
            }
        }
    else:
        # Filter stores by budget
        valid_stores = [store for store in valid_stores if store["price"] <= user_info.budget]
        
        if not valid_stores:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid items within budget exist. Try increasing your budget, or not using user preferences."
            )
        
        # Get closest and best value stores
        valid_stores_by_distance = sorted(valid_stores, key=lambda store: store["distance"])
        valid_stores_by_price = sorted(valid_stores, key=lambda store: store["price"])
        
        closest_store = valid_stores_by_distance[0]
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


class fugality_index(BaseModel):
    budget: Optional[int] = Field(default=MAXINT,
                                  ge=0,
                                  description="Budget in cents")


@router.post("/{user_id}/fulfill_list/{list_id}", status_code=status.HTTP_200_OK)
def fulfill_list(user_id: int, list_id: int, willing_to_spend: fugality_index):
    """
    Generate a list of the closest_stores to fufil a list
    currently there is a user input max price per budget
    """
    
    find_items = sqlalchemy.text("""
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
            ORDER BY item, price
        ),
        ranked_stores AS (
            SELECT  item, store_name, store_id, price, distance, 
                    RANK() OVER (PARTITION BY item ORDER BY price) AS ranks
            FROM they_got_it
        )
        SELECT item, store_name, store_id, price, distance, ranks
        FROM ranked_stores
        WHERE ranks = 1
    """)
    
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            try:
                shopping_list = conn.execute(find_items, 
                                             {"user_id": user_id,
                                              "list_id": list_id,
                                              "budget": willing_to_spend.budget})
            except NoResultFound as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User or List does not exist, {e}"
                )
    
    return_list = []
    for item in shopping_list:
        return_list.append({
            "Name": item.store_name,
            "Store ID": item.store_id,
            "Distance Away": f"{item.distance} km",
            "Item": item.item,
            "Price of Item": f"${item.price / 100:.2f}"
            
        })
    return return_list


@router.post("{user_id}/find_snack/{food_id}", status_code=status.HTTP_200_OK)
def find_store(user_id: int, food_id: int, params: fugality_index):
    """
    Finds closest store with given food_id. 
    """
    budget = params.budget

    get_user_info_query = sqlalchemy.text(
        """
        SELECT longitude, latitude
        FROM users
        WHERE users.user_id = :user_id
        """
    )

    find_matching_store_ids_query = sqlalchemy.text(
        """
        SELECT longitude, latitude, food_item.name,
        store.name as store_name, store.store_id as store_id,
        catalog_item.price as price

        FROM store

        JOIN catalog ON catalog.store_id = store.store_id
        JOIN catalog_item ON catalog.catalog_id = catalog_item.catalog_id
        JOIN food_item ON food_item.food_id = catalog_item.food_id
        WHERE food_item.food_id = :food_id
    """)

    food_data = {"food_id": food_id}
    
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            
            try:
                user_info = conn.execute(get_user_info_query, {"user_id": user_id}).one()
            except NoResultFound as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User does not exist, {e}"
                )
                
            try:
                result = conn.execute(find_matching_store_ids_query, food_data)
            except NoResultFound as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"food_id: {food_id} does not exist, {e}"
                )

            valid_stores = [
                {
                    "name": row.store_name,
                    "store_id": row.store_id,
                    "item_name" : row.name,
                    "price": row.price,
                    "distance": geodesic((user_info.latitude, user_info.longitude), (row.latitude, row.longitude)).km
                }
                for row in result if row.price <= budget
            ]

    if not valid_stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No stores found with the requested item, food_id {food_id} and budget {budget}"
        )

    # Sort by distance and get closest store
    valid_stores.sort(key=lambda store: store["distance"])
    closest_store = valid_stores[0]
    return {
        "Name": closest_store["name"],
        "Store ID": closest_store["store_id"],
        "Distance Away": f"{closest_store['distance']:.2f} km",
        "Item": closest_store["item_name"],
        "Price of Item": f"${closest_store['price'] / 100:.2f}"
    }
