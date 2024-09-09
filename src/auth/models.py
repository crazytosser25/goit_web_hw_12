"""Data models for DB"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import DateTime
from src.database import Base


class User(Base):
    """Represents a user in the application.

    This model defines the structure of the 'users' table in the database and contains fields
    relevant to the user's information and authentication details.

    Args:
        Base (SQLAlchemy Base): The base class for SQLAlchemy models, used to define
            the database table.

    Attributes:
        id (int): The primary key identifier for the user.
        username (str): The username of the user. Cannot be null.
        email (str): The email address of the user. Must be unique and cannot be null.
        password (str): The hashed password of the user. Cannot be null.
        created_at (datetime): The date and time when the user was created.
        refresh_token (str, optional): The refresh token associated with the user,
            used for authentication.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime)
    refresh_token = Column(String(255), nullable=True)
