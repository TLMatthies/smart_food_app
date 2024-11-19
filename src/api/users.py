from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import sqlalchemy
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
    name: str
    location: str | None = None

@router.post("/")
def create_user(new_user: User):
    """
    Creates a new user in the system.
    Returns the user_id of the created user.
    """
    user_info = {"name": new_user.name, "location": new_user.location}
    with db.engine.begin() as conn:
        try:
            user_id = conn.execute(sqlalchemy.text("""
                    INSERT INTO users (name, location)
                    VALUES (:name, :location)
                    RETURNING user_id
                    """
                ), user_info).scalar_one()
            
            return {"user_id": user_id}
            
        except Exception as e:
            logger.exception(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
@router.post("/{user_id}/preferences", status_code=status.HTTP_201_CREATED)
def add_preferences(user_id: int, budget: int):
    """
    Adds user preference onto user account (only budget for now)
    """
    if budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be greater than 0"
        )
    # Either adds preferences, or if already exists then change the budget value
    manage_preferences = sqlalchemy.text("""
                    INSERT INTO preference (user_id, budget)
                    VALUES (:user_id, :budget)
                    ON CONFLICT (user_id) DO UPDATE 
                    SET budget = :budget
                                         """)
    
    preference_data = {"user_id": user_id, "budget": budget}
    
    
    with db.engine.begin() as conn:
        
        try:
            conn.execute(manage_preferences, preference_data)
        
        except Exception as e:
            logger.exception(f"Error changing preferences: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User ID not found in database"
            )
    return {"message": "Preference successfully updated"}
            
    
@router.get("/{user_id}/preferences")
def get_preferences(user_id: int):
    """
    Gets user preference (only budget for now)
    """
    user_data = {"user_id": user_id}
    get_pref = sqlalchemy.text("""
            SELECT budget
            FROM preference
            WHERE user_id = :user_id
            """)
    check_user_query = sqlalchemy.text("""
        SELECT 1 FROM preference WHERE user_id = :user_id
    """)

    with db.engine.begin() as conn:
        try:
            user_exists = conn.execute(check_user_query, user_data).scalar_one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist or preferences have not been set"
            )
        try:
            budget = conn.execute(get_pref, user_data).scalar_one()
            return "Budget " + str(budget)
            
        except Exception as e:
            logger.exception(f"Error getting preferences: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exist or user has not set preferences yet"
            )



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
    with db.engine.begin() as conn:
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