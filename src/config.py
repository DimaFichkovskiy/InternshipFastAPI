import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname("../"))
load_dotenv(dotenv_path=f"{basedir}/.env")


class Config:
    LOCAL_POSTGRES_URL = os.getenv("LOCAL_POSTGRES_URL")
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    REDIS_URL = os.getenv("REDIS_URL")
