from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get("/{store_id}/catalogs")
def get_store_catalog(store_id: int):
    """
    Retrieves the catalog for a specific store.
    Returns a list of items with their SKUs, names, quantities, and prices.
    """
    
    id_data = {"store_id": store_id}
    fetch_catalog = sqlalchemy.text("""
            SELECT ci.catalog_item_id AS item_sku, fi.name, ci.quantity, ci.price
            FROM catalog_item ci
            JOIN catalog c ON ci.catalog_id = c.catalog_id
            JOIN food_item fi ON ci.food_id = fi.food_id
            WHERE c.store_id = :store_id
                                    """)
    
    with db.engine.begin() as conn:
            
        try:
            db_catalog = conn.execute(fetch_catalog,id_data)
        
        except Exception as e:
            logger.exception(f"Error fetching catalog: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching the catalog"
            )
        
        catalog = []
        for item in db_catalog:
            catalog.append({
                "item_sku": str(item.item_sku),
                "name": item.name,
                "quantity": item.quantity,
                "price": item.price
            })

        if catalog == []:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch catalog for store"
            )
        return catalog
            