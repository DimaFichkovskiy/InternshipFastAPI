from sqlalchemy import select
from passlib.context import CryptContext

from .database import AsyncSession
from .users import models
from .users.schemas import UserUpdate
from .auth.schemas import SignUp

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:

    @classmethod
    async def get_users(cls, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(models.User).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def get_user(cls, db: AsyncSession, user_id: int):
        result = await db.execute(select(models.User).filter(models.User.id == user_id))
        return result.scalars().first()

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str):
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()

    @classmethod
    async def create_user(cls, db: AsyncSession, user: SignUp):
        hashed_password = pwd_context.hash(user.password)

        db_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hashed_password
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @classmethod
    async def update_user(cls, db: AsyncSession, user_id: int, update_data: UserUpdate):
        user = await cls.get_user(db=db, user_id=user_id)

        if update_data.first_name is not None:
            user.first_name = update_data.first_name
        if update_data.last_name is not None:
            user.last_name = update_data.last_name

        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def delete_user(cls, db: AsyncSession, user_id: int):
        user = await cls.get_user(db=db, user_id=user_id)
        await db.delete(user)
        await db.commit()
