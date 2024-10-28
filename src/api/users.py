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
                    INSERT INTO Users (name, location)
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