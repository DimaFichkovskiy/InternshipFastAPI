import databases
import aioredis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import POSTGRES_URL, REDIS_URL

db = databases.Database(POSTGRES_URL)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.connect()
    app.state.redis = await aioredis.from_url(REDIS_URL)


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    await app.state.redis.close()


@app.get('/')
def health_check():
    return {"status": "Working"}
