"""Main file"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.database import engine
from src.contacts import models
from src.contacts.router import contact_router
from src.auth.router import auth_router


load_dotenv()

models.Base.metadata.create_all(bind=engine)
r = None  # pylint: disable=C0103

@asynccontextmanager
async def lifespan(app: FastAPI): # pylint: disable=W0613, W0621
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    global r  # pylint: disable=W0603
    r = await redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=0, encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)

    yield

    r.close()


app = FastAPI(title="ContactBook", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(contact_router)

app.openapi_schema = app.openapi()


@app.get("/api/healthchecker", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
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
