from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
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

# Why is this here??
# 
# class UserLocation(BaseModel):
#     latitude: float = Field(..., ge=-90, le=90, description="Latitude of the user's location.")
#     longitude: float = Field(..., ge=-180, le=180, description="Longitude of the user's location.")

# class StoreLocation(BaseModel):
#     latitude: float = Field(..., ge=-90, le=90, description="Latitude of the stores's location.")
#     longitude: float = Field(..., ge=-180, le=180, description="Longitude of the stores's location.")

# class Store(BaseModel):
#     store_id: int
#     name: str
#     hours: tuple[str, str]  # (open_time, close_time)
#     location: StoreLocation

@router.post("/route-optimize", status_code=status.HTTP_200_OK)
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
                    "longitude": row.longitude,
                    "latitude": row.latitude,
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