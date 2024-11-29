from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import logging
from src import database as db
from src.api import auth
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
    dependencies=[Depends(auth.get_api_key)],
)

class StoreLocation(BaseModel):
    longitude: float = Field(le=180, ge=-180)
    latitude: float = Field(le=90, ge=-90)

class Hours(BaseModel):
    open_time: int
    close_time: int

class Store(BaseModel):
    store_id: int
    name: str = Field(pattern=r"^[a-zA-Z0-9_]+$", min_length=1, max_length=82)
    hours: Hours  # (open_time, close_time)
    location: StoreLocation

@router.get("/")
def get_stores():
    """
    Retrieves all stores with their locations and hours.
    """
    with db.engine.begin() as conn:
        
        try:
            result = conn.execute(sqlalchemy.text(
                """
                SELECT store_id, name, latitude, longitude,
                       open_time, close_time
                FROM store
                """))
        except Exception as e:
            logger.exception(f"Error fetching stores: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch stores"
            )
        
            
    stores = [    
        {
        "store_id": str(row.store_id),
        "name": row.name,
        "hours": {
            "open": row.open_time.strftime("%I:%M %p"),
            "close": row.close_time.strftime("%I:%M %p")
                },
        "location": {
            "latitude": row.latitude,
            "longitude": row.longitude
                }
        }
        for row in result
    ]
    return stores
            
    

@router.get("/{store_id}/catalog")
def get_catalog(store_id: int):
    """
    Retrieves the list of items that the store has in its catalog, including item_sku, name, price, and quantity.
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
            db_catalog = conn.execute(fetch_catalog, id_data).mappings().all()
        except Exception as e:
            logger.exception(f"Error fetching catalog: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch catalog for store"
            )

    if not db_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store ID not found in database"
        )

    return db_catalog


@router.post("/compare-prices")
def compare_prices(food_id: int, 
            max_stores: int = Query(3, description="How many stores would you like to see", gt=0)
                   ):
    """
    Find the stores with the best prices
    """
    find_stores = sqlalchemy.text("""
        SELECT store.store_id AS id, store.name AS store, food_item.name, price,
                RANK() OVER (PARTITION BY catalog_item.food_id ORDER BY price) AS rank
        FROM store
        JOIN catalog ON catalog.store_id = store.store_id
        JOIN catalog_item ON catalog_item.catalog_id = catalog.catalog_id
        JOIN food_item ON food_item.food_id = catalog_item.food_id
        WHERE catalog_item.food_id = :food_id
        ORDER BY price ASC
        LIMIT :max_stores
    """)
    
    
    print(type(food_id), type(max_stores))
    query_params = [{
        "food_id": food_id,
        "max_stores": max_stores
    }]

    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            try:
                conn.execute(sqlalchemy.text("""
                     SELECT 1 FROM food_item
                     WHERE food_id = :food_id"""
                     ),{"food_id": food_id}).one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Food_id does not exist.")
                                    
            stores = conn.execute(find_stores, query_params)


    return_object = [
        {
            "store_id": store.id,
            "store_name": store.name,
            "item": store.store,
            "price": f"${store.price / 100:.2f}",
            "rank": store.rank
        }
        for store in stores
    ]

    return return_object
