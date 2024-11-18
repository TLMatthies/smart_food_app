from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import sqlalchemy
import logging
from src import database as db
from src.api import auth

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
def optimize_shopping_route(location: UserLocation, food_id: int):
    """
    Finds nearby stores with given food_id
    """

    check_food_query = sqlalchemy.text("""
        SELECT 1 FROM food_item WHERE food_id = :food_id
    """)
    with db.engine.begin() as conn:
        try:
            food_exists = conn.execute(check_food_query, food_id).scalar_one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item does not exist"
            )
        
    return "OK"

# Response:
# {
# "closest_store": (either store_id or store_name)
# "distance": 3.0,
# }
# `
        