import os
import logging.config
import databases
import aioredis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from src.config import Config
from src.auth import router as auth_router
from src.users import router as user_router

db = databases.Database(Config.POSTGRES_URL)

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)

add_pagination(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logging.config.fileConfig("logging.ini")
# logger = logging.getLogger()


@app.on_event("startup")
async def startup():
    # logger.info("START")
    await db.connect()
    app.state.redis = await aioredis.from_url(Config.REDIS_URL)


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    await app.state.redis.close()


@app.get('/')
def health_check():
    return {"status": "Working"}
