from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

from src.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    is_owner = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # user = relationship("User", backref=backref("order_products", cascade="all, delete-orphan"), lazy='selectin')
    # company = relationship("Company", backref=backref("order_products", cascade="all, delete-orphan"), lazy='selectin')
    user = relationship("User", back_populates="workers", lazy='selectin')
    company = relationship("Company", back_populates="workers", lazy='selectin')

