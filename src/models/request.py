from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref

from src.database import Base


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    accepted = Column(Boolean, default=False)
    rejected = Column(Boolean, default=False)

    user = relationship("User", back_populates="requests", lazy='selectin')
    company = relationship("Company", back_populates="requests", lazy='selectin')
