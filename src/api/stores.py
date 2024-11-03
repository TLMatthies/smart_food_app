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
    id_data = {"store_id": store_id}
    fetch_catalog = sqlalchemy.text("""
            SELECT catalog_item_id as item_sku, name, quantity, price
            FROM catalog_item
            JOIN catalog ON catalog_item.catalog_id = catalog.catalog_id
            JOIN food_item fi ON catalog_item.food_id = food_item.food_id
            WHERE catalog.store_id = :store_id
                                    """)
    
    with db.engine.begin() as conn:
            
        try:
            db_catalog = conn.execute(fetch_catalog,id_data)
        
        except Exception as e:
            logger.exception(f"Error fetching catalog: {e}")
            raise Exception(f"Failed to fetch catalog for store {store_id}")  
        
        catalog = []
        for item in db_catalog:
            catalog.append({
                "item_sku": str(item.item_sku),
                "name": item.name,
                "quantity": item.quantity,
                "price": item.price
            })
            
        return catalog
