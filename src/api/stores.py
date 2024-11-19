from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import sqlalchemy
from sqlalchemy.exc import IntegrityError
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stores"
            )
    

@router.get("/{store_id}/catalog")
def get_catalog(store_id: int):
    """
    Retrieves the list of items that the store has in its catalog, item_sku, name, price, quantity
    """
    id_data = {"store_id": store_id}
    fetch_catalog = sqlalchemy.text("""
            SELECT catalog_item_id as item_sku, name, quantity, price
            FROM catalog_item
            JOIN catalog ON catalog_item.catalog_id = catalog.catalog_id
            JOIN food_item fi ON catalog_item.food_id = fi.food_id
            WHERE catalog.store_id = :store_id
                                    """)
    
    with db.engine.begin() as conn:
            
        try:
            db_catalog = conn.execute(fetch_catalog,id_data)
        
        except Exception as e:
            logger.exception(f"Error fetching catalog: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch catalog for store"
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store ID not found in database"
            )
        return catalog


class PricesRequest(BaseModel):
    food_id: int = Field(ge=0)
    max_price: Optional[int] = Field(default=0, ge=0)
    max_stores: Optional[int] = Field(default=3, ge=1)

@router.post("/compare-prices")
def compare_prices(request: PricesRequest):
    """
    Find the stores with the best prices"""

    query = """
    SELECT store.store_id AS id, store.name AS name, price
    FROM store
    JOIN catalog ON catalog.store_id = store.store_id
    JOIN catalog_item ON catalog_item.catalog_id = catalog.catalog_id
    WHERE catalog_item.food_id = :food_id
    """
    if request.max_price > 0:
        query += "AND catalog_item.price <= :max_price"

    query += """
    ORDER BY price ASC
    LIMIT :max_stores
    """
        
    query_params = [{
        "food_id": request.food_id,
        "max_price": request.max_price,
        "max_stores": request.max_stores
    }]

    try:
        with db.engine.begin() as conn:
            result = conn.execute(sqlalchemy.text(query), query_params)
    except sqlalchemy.exc.IntegrityError as e:
        return e

    result = result.fetchall()

    if len(result) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching results"
        )

    return_object = []
    place = 1
    for line in result:
        return_object.append({
            "store_id": line.id,
            "store_name": line.name,
            "price": line.price,
            "rank": place
        })
        place += 1

    return return_object
