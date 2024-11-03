from fastapi import APIRouter, Depends
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
    try:
        with db.engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO "Users" (name, location)
                    VALUES (:name, :location)
                    RETURNING user_id
                    """
                ),
                {"name": new_user.name, "location": new_user.location}
            )
            user_id = result.scalar_one()
            
            return {"user_id": user_id}
            
    except Exception as e:
        # Log the error and return a generic message
        logger.exception(f"Error creating user: {e}")
        raise Exception("Failed to create user")
    
@router.post("/users/{user_id}/preferences")
def add_preferences(user_id: int, budget: int):
    """
    Adds user preference onto user account (only budget for now)
    """

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
            raise Exception("Failed to change preferences")
        
    return "OK"
            
    
@router.get("/users/{user_id}/preferences")
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

    with db.engine.begin() as conn:
            
        try:
            budget = conn.execute(get_pref, user_data).scalar()
            return budget
            
        except Exception as e:
            logger.exception(f"Error getting preferences: {e}")
            raise Exception("Failed to get preferences")



@router.post("/users/{user_id}/lists")
def create_list(user_id: int, name: str):
    """
    Make a new shopping list for customer
    """
    user_data = {"user_id": user_id, "name": name}
    
    with db.engine.begin() as conn:
        try:
            list_id = conn.execute(sqlalchemy.text("""
                INSERT INTO shopping_list (name, user_id)
                VALUES (:name, :user_id)
                RETURNING list_id
                """), user_data).scalar()
            
            return {"name": name, "list_id": list_id}

        except Exception as e:
            logger.exception(f"Error creating list: {e}")
            raise Exception("Failed to create list")

class item(BaseModel):
    food_id: int
    quantity: int

@router.post("/users/{user_id}/lists/{list_id}")
def add_item_to_list(list_id: int, items: list[item]):
    """
    Add items to specified list, and specified user
    """
    try:
        item_dicts = [{"list_id": list_id, "food_id": item.food_id, "quantity": item.quantity} for item in items]
        with db.engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO shopping_list_item (list_id, food_id, quantity)
                    VALUES (:list_id, :food_id, :quantity)
                    """
                ),
                item_dicts
            )
            
            return "OK"

    except Exception as e:
        # Log the error and return a generic message
        logger.exception(f"Error adding to list: {e}")
        raise Exception("Failed to add to list")
    
@router.delete("/users/{user_id}/lists/{list_id}}")
def delete_item_from_list(list_id: int, food_id: int):
    """
    Delete item from specified list, and specified user
    """
    try:
        with db.engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM shopping_list_item
                    WHERE list_id = :list_id AND food_id = :food_id
                    """
                ),
                {"list_id": list_id, "food_id": food_id}
            )
            
            return "OK"

    except Exception as e:
        # Log the error and return a generic message
        logger.exception(f"Error deleting from list: {e}")
        raise Exception("Failed to delete from list")
    
@router.get("/users/{user_id}/lists/}")
def get_list_history(user_id: int):
    """
    Get the history of added lists from a user
    """
    try:
        with db.engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text(
                    """
                    SELECT list_id, name
                    FROM shopping_list
                    WHERE user_id = :user_id
                    """
                ),
                {"user_id": user_id}
            )
            rows = result.mappings().all()
            # This is kinda funny
            list_list = []
            list_list = [
                {"list_id": row['list_id'], "name": row['name']}
                for row in rows
            ]

            return list_list

    except Exception as e:
        # Log the error and return a generic message
        logger.exception(f"Error getting history from user: {e}")
        raise Exception("Failed to get history from user")