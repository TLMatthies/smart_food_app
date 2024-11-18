from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import sqlalchemy
import logging
from src import database as db
from src.api import auth

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
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

@router.get("/post/route-optimize", status_code=status.HTTP_200_OK)
def optimize_shopping_route(location: UserLocation, food_id: int):
    """
    Finds nearby stores with given food_id
    """


# Response:
# {
# "closest_store": (either store_id or store_name)
# "distance": 3.0,
# }
# `
        