"""Connecting to Postgres"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    url=DATABASE_URL,
    echo=False
)
DBSession = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    """Provides a database session to be used within a request context.

    This function is designed to be used as a dependency in FastAPI endpoints.
    It yields a SQLAlchemy session that is used for the duration of the request
    and ensures that the session is properly closed after the request is
    completed, even if an exception occurs.

    Yields:
        Session: An instance of SQLAlchemy session (DBSession)
        which can be used to interact with the database.
    """
    base = DBSession()
    try:
        yield base
    finally:
        base.close()
