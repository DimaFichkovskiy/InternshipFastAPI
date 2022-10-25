from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, default=None)
    last_name = Column(String, default=None)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, default=None)
    date_created = Column(DateTime(timezone=True), default=func.now())
