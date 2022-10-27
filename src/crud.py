from typing import Optional, List, Union
from sqlalchemy import select
from passlib.context import CryptContext

from .database import AsyncSession
from src import models, security, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:

    @classmethod
    async def get_users(cls, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
        result = await db.execute(select(models.User).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def get_user(cls, db: AsyncSession, user_id: int) -> models.User:
        result = await db.execute(select(models.User).filter(models.User.id == user_id))
        return result.scalars().first()

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str) -> models.User:
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()

    @classmethod
    async def create_user(cls, db: AsyncSession, user: schemas.SignUp) -> models.User:
        hashed_password = await security.get_password_hash(user.password)

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
    async def create_user_by_email(cls, db: AsyncSession, email: str) -> models.User:
        db_user = models.User(
            email=email
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @classmethod
    async def update_user_info(cls, db: AsyncSession, user_id: int, update_data: schemas.UserInfoUpdate) -> models.User:
        user = await cls.get_user(db=db, user_id=user_id)

        if update_data.first_name is not None:
            user.first_name = update_data.first_name
        if update_data.last_name is not None:
            user.last_name = update_data.last_name

        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def update_user_password(
            cls, db: AsyncSession, user_id: int, update_data: schemas.UserPasswordUpdate
    ) -> Union[models.User, bool]:
        user = await cls.get_user(db=db, user_id=user_id)

        if await security.verify_password(update_data.password, user.hashed_password):
            return False

        hashed_password = await security.get_password_hash(update_data.password)
        user.hashed_password = hashed_password

        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def delete_user(cls, db: AsyncSession, user_id: int):
        user = await cls.get_user(db=db, user_id=user_id)
        await db.delete(user)
        await db.commit()

    @classmethod
    async def authenticate(cls, db: AsyncSession, login_data: schemas.SignIn) -> Optional[models.User]:
        user = await cls.get_user_by_email(db=db, email=login_data.email)
        if not user:
            return None
        if not await security.verify_password(login_data.password, user.hashed_password):
            return None
        return user
