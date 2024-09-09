"""Main file"""
from fastapi import FastAPI
from src.database import engine

import src.contacts.models as models
from src.contacts.router import contact_router
from src.auth.router import auth_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ContactBook")


app.include_router(auth_router)
app.include_router(contact_router)

app.openapi_schema = app.openapi()


@app.get("/api/healthchecker")
def root() -> dict:
    """Health check endpoint to verify that the server is running.

    This endpoint can be used to confirm that the server is alive and
    responding to requests. It returns a simple message indicating the server
    status.

    Returns:
        dict: A dictionary containing a message indicating that
            the server is alive.
    """
    result = {"message": "Server alive."}
    return result
