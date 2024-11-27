from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
import sqlalchemy
from sqlalchemy.exc import IntegrityError, NoResultFound
import logging
from src import database as db
from src.api import auth

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class User(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z0-9_]+$", min_length=1, max_length=27)
    location: Optional[str] = Field(default="Calpoly SLO")
    longitude: Optional[float] = Field(default=-120.6625, le=180, ge=-180)
    latitude: Optional[float] = Field(default=35.3050, le=90, ge=-90)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(new_user: User):
    """
    Creates a new user in the system.
    Returns the user_id of the created user.
    """
    user_info = {"name": new_user.name, "location": new_user.location,
                 "long": new_user.longitude, "lat": new_user.latitude}
    try:
        with db.engine.begin() as conn:
            user_id = conn.execute(sqlalchemy.text("""
                    INSERT INTO users (name, location, longitude, latitude)
                    VALUES (:name, :location, :long, :lat)
                    RETURNING user_id
                    """
                ), user_info).scalar_one()
            
            return {"user_id": user_id}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Failed to create user.")
            
    
@router.get("/{user_id}/lists/{list_id}/facts", status_code=status.HTTP_200_OK)
def list_facts(user_id: int, list_id: int):
    
    grab_facts = sqlalchemy.text("""
    SELECT
    COALESCE(food_item.name, 'Total') AS name,
    SUM((shopping_list_item.quantity) * (serving_size)) AS total_servings,
    SUM((shopping_list_item.quantity) * (saturated_fat)) AS total_saturated_fat,
    SUM((shopping_list_item.quantity) * (trans_fat)) AS total_trans_fat,
    SUM((shopping_list_item.quantity) * (dietary_fiber)) AS total_dietary_fiber,
    SUM((shopping_list_item.quantity) * (total_carbohydrate)) AS total_carbohydrates,
    SUM((shopping_list_item.quantity) * (total_sugars)) AS total_sugars,
    SUM((shopping_list_item.quantity) * (protein)) AS total_protein
    FROM shopping_list
    JOIN shopping_list_item on shopping_list.list_id = shopping_list_item.list_id
    JOIN food_item on shopping_list_item.food_id = food_item.food_id
    WHERE
    shopping_list.list_id = :list_id
    GROUP BY ROLLUP (food_item.name)
    """)
    
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            # block of checks before executing the big sql statement to catch errors
            try:
                conn.execute(sqlalchemy.text("""
                    SELECT 1 FROM users 
                    WHERE user_id = :user_id
                    """), {"user_id": user_id}).one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist.")

            try:
                conn.execute(sqlalchemy.text("""
                    SELECT 1 FROM shopping_list 
                    WHERE list_id = :list_id
                    """), {"list_id": list_id}).one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="List does not exist.")

            try:
                conn.execute(
                    sqlalchemy.text("""
                    SELECT 1 FROM shopping_list 
                    WHERE list_id = :list_id AND user_id = :user_id
                    """),{"user_id": user_id, "list_id": list_id}).one()
            except NoResultFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="User is not associated with this list.")
            
            
            isEmpty = conn.execute(
                sqlalchemy.text("""
                SELECT 1
                FROM shopping_list
                JOIN shopping_list_item on shopping_list.list_id = shopping_list_item.list_id
                WHERE shopping_list.list_id = :list_id
                """),{"list_id": list_id}).scalar()
            if isEmpty == None:
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                    detail="List is empty, add something to it!")
            
            try:
                nutrition_info = conn.execute(grab_facts, {"list_id": list_id})
            except Exception as e:
                raise HTTPException(status_code=500, 
                    detail=f"Something went wrong {e}")
    
    nutrition_dict = {}
    for item in nutrition_info:
        nutrition_dict[item.name] = {
            "total_servings": item.total_servings,
            "total_saturated_fat": item.total_saturated_fat,
            "total_trans_fat": item.total_trans_fat,
            "total_dietary_fiber": item.total_dietary_fiber,
            "total_carbohydrates": item.total_carbohydrates,
            "total_sugars": item.total_sugars,
            "total_protein": item.total_protein
        }
    return nutrition_dict


@router.post("/{user_id}/lists", status_code=status.HTTP_201_CREATED)
def create_list(user_id: int, name: str):
    """
    Make a new shopping list for customer
    """
    user_data = {"user_id": user_id, "name": name}
    check_user_query = sqlalchemy.text("""
        SELECT 1 FROM preference WHERE user_id = :user_id
    """)
    with db.engine.begin() as conn:
        try:
            user_exists = conn.execute(check_user_query, user_data).scalar_one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )
        try:
            list_id = conn.execute(sqlalchemy.text("""
                INSERT INTO shopping_list (name, user_id)
                VALUES (:name, :user_id)
                RETURNING list_id
                """), user_data).scalar_one()
        
            return {"name": name, "list_id": list_id}

        except Exception as e:
            logger.exception(f"Error creating list: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed create shopping list"
            )

class item(BaseModel):
    food_id: int
    quantity: int

@router.post("/{user_id}/lists/{list_id}", status_code=status.HTTP_201_CREATED)
def add_item_to_list(list_id: int, user_id: int, items: list[item]):
    """
    Add items to specified list, and specified user
    """
    user_data = {"user_id": user_id}
    check_user_query = sqlalchemy.text("""
        SELECT 1 FROM users WHERE user_id = :user_id
    """)
    for item in items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )
    item_dicts = [{"list_id": list_id, "user_id": user_id, "food_id": item.food_id, "quantity": item.quantity} for item in items]
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            try:
                user_exists = conn.execute(check_user_query, user_data).scalar_one()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist"
                )
            #Check for valid food ids
            food_ids = [item.food_id for item in items]
            existing_food_ids = conn.execute(sqlalchemy.text("""
                                    SELECT food_id FROM food_item WHERE food_id IN :food_ids"""),
                {"food_ids": tuple(food_ids)}
            ).fetchall()
            existing_food_ids = {row[0] for row in existing_food_ids}

            # Filter out items with invalid food_id
            invalid_items = [item for item in items if item.food_id not in existing_food_ids]
            if invalid_items:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Food ID not recognized"
                )
        
            try:
                conn.execute(sqlalchemy.text("""
                    INSERT INTO shopping_list_item (list_id, user_id, food_id, quantity)
                    VALUES (:list_id, :user_id, :food_id, :quantity)
                    """
                ), item_dicts)
                
                return "Foods successfully added to list"

            except Exception as e:
                logger.exception(f"Error adding to list: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add to list"
                )
    
@router.delete("/{user_id}/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_from_list(list_id: int, food_id: int):
    """
    Delete item from specified list, and specified user
    """
    user_data = {"list_id": list_id, "food_id": food_id}
    check_query = sqlalchemy.text("""
        SELECT 1 FROM shopping_list_item WHERE food_id = :food_id AND list_id = :list_id
    """)

    with db.engine.begin() as conn:
        try:
            check_exists = conn.execute(check_query, user_data).scalar_one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="List id or food id is invalid/does not exist"
            )

        try:
            conn.execute(sqlalchemy.text("""
                    DELETE FROM shopping_list_item
                    WHERE list_id = :list_id AND food_id = :food_id
                    """
                ), user_data)
            return "Successfully deleted"
        
        except Exception as e:
            logger.exception(f"Error deleting from list: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete from list"
            )
    
@router.get("/{user_id}/lists/", status_code=status.HTTP_200_OK)
def get_list_history(user_id: int):
    """
    Get the history of added lists from a user
    """
    user_info = {"user_id": user_id}
    check_user_query = sqlalchemy.text("""
        SELECT 1 FROM users WHERE user_id = :user_id
    """)
    with db.engine.begin() as conn:
        try:
            user_exists = conn.execute(check_user_query, user_info).scalar_one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )   
        try:    
            shopping_lists = conn.execute(sqlalchemy.text("""
                    SELECT list_id, name
                    FROM shopping_list
                    WHERE user_id = :user_id
                    """
                ), user_info).mappings().all()
            
            return_list = [
                {"list_id": item['list_id'], "name": item['name']}
                for item in shopping_lists
            ]

            return return_list

        except Exception as e:
            logger.exception(f"Error getting history from user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user history"
            )