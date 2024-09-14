"""CRUD operations"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.auth.models import User
from src.auth.schemas import UserScema


async def get_user_by_email(email: str, db: Session) -> User:
    """Retrieve a user from the database by their email address.

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The database session used for querying the user.

    Returns:
        User: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserScema, db: Session) -> User:
    """Create a new user in the database.

    Args:
        body (UserScema): The schema containing user information such as email, password, etc.
        db (Session): The database session used to add the new user.

    Returns:
        User: The newly created user object.
    """
    new_user = User(**body.model_dump())
    new_user.created_at = datetime.now(timezone.utc)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """Update the refresh token of a user in the database.

    Args:
        user (User): The user object whose refresh token needs to be updated.
        token (str | None): The new refresh token to set for the user. Pass None to clear the token.
        db (Session): The database session used to update the user's token.
    """
    user.refresh_token = token
    db.commit()

async def confirmed_check_toggle(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
