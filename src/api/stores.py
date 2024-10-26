from fastapi import APIRouter, Depends
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

class StoreLocation(BaseModel):
    latitude: float
    longitude: float

class Store(BaseModel):
    store_id: str
    name: str
    hours: tuple[str, str]  # (open_time, close_time)
    location: StoreLocation

@router.get("/")
def get_stores():
    """
    Retrieves all stores with their locations and hours.
    """
    try:
        with db.engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text(
                    """
                    SELECT store_id, name, latitude, longitude,
                           open_time, close_time
                    FROM stores
                    """
                )
            )
            
            stores = []
            for row in result:
                stores.append({
                    "store_id": str(row.store_id),
                    "name": row.name,
                    "hours": (str(row.open_time), str(row.close_time)),
                    "location": {
                        "latitude": row.latitude,
                        "longitude": row.longitude
                    }
                })
            
            return stores
            
    except Exception as e:
        logger.exception(f"Error fetching stores: {e}")
        raise Exception("Failed to fetch stores")