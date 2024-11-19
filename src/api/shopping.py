from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import sqlalchemy
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

class UserLocation(BaseModel):
    latitude: float
    longitude: float

class StoreLocation(BaseModel):
    latitude: float
    longitude: float

class Store(BaseModel):
    store_id: str
    name: str
    hours: tuple[str, str]  # (open_time, close_time)
    location: StoreLocation

@router.post("/route-optimize", status_code=status.HTTP_200_OK)
def optimize_shopping_route(user_id: int, food_id: int, use_preferences: bool):
    """
    Finds nearby stores with given food_id. If use_preferences is toggled to True, then a user's budget will be accounted when a store is selected. Otherwise, the closest store to the user with the valid food item is selected.
    """

    check_food_query = sqlalchemy.text("""
        SELECT 1 FROM food_item WHERE food_id = :food_id
    """)

    if use_preferences:
        get_user_info_query = sqlalchemy.text("""
            SELECT users.longitude, users.latitude, preference.budget
            FROM users
            LEFT JOIN preference ON users.user_id = preference.user_id                    
            WHERE users.user_id = :user_id
        """)
    else:
        get_user_info_query = sqlalchemy.text("""
            SELECT longitude, latitude
            FROM users                 
            WHERE users.user_id = :user_id
        """)

    find_matching_store_ids_query = sqlalchemy.text("""
        SELECT
        longitude,
        latitude,
        store.name as store_name,
        store.store_id as store_id,
        catalog_item.price as price

        FROM store

        JOIN catalog ON catalog.store_id = store.store_id
        JOIN catalog_item ON catalog.catalog_id = catalog_item.catalog_id
        JOIN food_item ON food_item.food_id = catalog_item.food_id
        WHERE food_item.food_id = :food_id
    """)

    food_data = {"food_id": food_id}
    user_data = {"user_id": user_id}
    
    with db.engine.begin() as conn:
        try:
            food_exists = conn.execute(check_food_query, food_data).scalar_one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item does not exist"
            )
        
        try:
            user_info = conn.execute(get_user_info_query, user_data).one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )

        # If using preferences, check if preferences exist
        if use_preferences and user_info[2] is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User preferences not set"
            )
        
        result = conn.execute(find_matching_store_ids_query, food_data)

    valid_stores = []
    user_long = user_info[0]
    user_lat = user_info[1]
    user_budget = user_info[2] if use_preferences else None
    user_location = (user_lat, user_long)

    for row in result:
        store_location = (row[1], row[0])
        store = {
            "longitude": row[0],
            "latitude": row[1],
            "name": row[2],
            "store_id": row[3],
            "price": row[4],
            "distance": geodesic(user_location, store_location).km
        }
        valid_stores.append(store)
        print(store)

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
        valid_stores = [store for store in valid_stores if store["price"] <= user_budget]
        
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