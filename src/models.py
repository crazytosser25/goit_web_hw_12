"""Data models for DB"""
from sqlalchemy import Column, Integer, String, Date
from src.database import Base

class Contact(Base):
    """Represents a contact in the database.

    This class maps to the `contacts` table in the database and defines the schema
    for storing contact information. Each contact includes personal details such as
    names, email, phone number, birthday, and additional information.

    Args:
        Base (DeclarativeMeta): The base class for all SQLAlchemy models, which provides
            the necessary functionality for ORM mapping.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    birthday = Column(Date)
    other_info = Column(String, nullable=True)
