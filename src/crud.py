from sqlalchemy import select, update, delete

from .database import AsyncSession
from .users import models
from .users.schemas import UserUpdate
from src.auth.schemas import SignUp


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

    # @classmethod
    # async def create_user(cls, db: AsyncSession, user: SignUp):
    #     fake_hashed_password = user.password + "notreallyhashed"
    #     db_user = await models.User(
    #         first_name=user.first_name,
    #         last_name=user.last_name,
    #         email=user.email,
    #         hashed_password=fake_hashed_password
    #     )
    #     await db.add(db_user)
    #     await db.commit()
    #     await db.refresh(db_user)
    #     return db_user

    @classmethod
    async def update_user(cls, db: AsyncSession, user_id: int, user: UserUpdate):
        updated_user = await db.execute(update(models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email
        )).filter(models.User.id == user_id))
        await db.commit()
        await db.refresh(updated_user)
        return updated_user

    @classmethod
    async def delete_user(cls, db: AsyncSession, user_id: int):
        deleted_user = await db.execute(select(models.User).filter(models.User.id == user_id))
        deleted_user = deleted_user.scalars().first()
        await db.delete(deleted_user)
        await db.commit()
        await db.refresh(deleted_user)
        return deleted_user
