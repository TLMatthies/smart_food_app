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
                    FROM store
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
    

@router.get("/stores/{store_id}/catalog")
def get_catalog(store_id: int):
    """
    Retrieves the list of items that the store has in its catalog, item_sku, name, price, quantity
    """
    try:
        with db.engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text(
                    """
                    SELECT food_item.name, catalog_item.quantity, catalog_item.price
                    FROM catalog_item

                    JOIN food_item ON food_item.food_id = catalog_item.food_id
                    JOIN store ON catalog_item.catalog_id = store.catalog_id
                    WHERE store.store_id = :store_id
                    """
                ),
                {"store_id": store_id}
            )
        
            catalog_list = []
            for row in result:
                catalog_list.append({
                    "name": row.name,
                    "quantity": (row.quantity),
                    "price": (row.price)
                })
            
            return catalog_list
            
    except Exception as e:
        logger.exception(f"Error fetching catalog: {e}")
        raise Exception("Failed to fetch catalogue")

