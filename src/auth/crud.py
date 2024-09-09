"""CRUD operations"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.auth.models import User
from src.auth.schemas import UserScema


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserScema, db: Session) -> User:
    new_user = User(**body.model_dump())
    new_user.created_at = datetime.now(timezone.utc)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()
