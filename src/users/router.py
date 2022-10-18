from fastapi import APIRouter, Depends, HTTPException

from src.crud import UserCRUD
from src.database import AsyncSession, get_db_session
from .schemas import User, Users, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/", response_model=Users)
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session)):
    users = await UserCRUD.get_users(db, skip=skip, limit=limit)
    return {
        "page": 1,
        "users": users
    }


@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    user = await UserCRUD.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@router.put("/{user_id}")
def update_user(user_update: UserUpdate):
    pass
