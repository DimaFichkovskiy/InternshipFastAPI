import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname("../"))
load_dotenv(dotenv_path=f"{basedir}/.env")


DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@" \
               f"database:5432/{os.getenv('POSTGRES_DB')}"

print(DATABASE_URL)