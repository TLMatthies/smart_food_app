from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sqlalchemy
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
    try:
        with db.engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text(
                    """
                    SELECT 
                        ci.catalog_item_id as item_sku,
                        fi.name,
                        ci.quantity,
                        ci.price
                    FROM catalog_items ci
                    JOIN food_items fi ON ci.food_id = fi.food_id
                    WHERE ci.store_id = :store_id
                    """
                ),
                {"store_id": store_id}
            )
            
            catalog = []
            for row in result:
                catalog.append({
                    "item_sku": str(row.item_sku),
                    "name": row.name,
                    "quantity": row.quantity,
                    "price": row.price
                })
            
            return catalog
            
    except Exception as e:
        logger.exception(f"Error fetching catalog: {e}")
        raise Exception(f"Failed to fetch catalog for store {store_id}")