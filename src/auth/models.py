"""Data models for DB"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import DateTime
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime)
    refresh_token = Column(String(255), nullable=True)
