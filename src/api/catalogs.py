from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sqlalchemy
import logging
from src import database as db
from src.api import auth

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stores",
    tags=["catalog"],
    dependencies=[Depends(auth.get_api_key)],
)

class CatalogItem(BaseModel):
    item_sku: str
    name: str
    quantity: int
    price: int

@router.get("/{store_id}/catalog")
def get_store_catalog(store_id: int):
    """
    Retrieves the catalog for a specific store.
    Returns a list of items with their SKUs, names, quantities, and prices.
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
            