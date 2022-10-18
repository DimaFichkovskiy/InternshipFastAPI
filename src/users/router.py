from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate

from src import crud
from src.database import AsyncSession, get_db_session
from .schemas import User, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/", response_model=Page[User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session)):
    users = await crud.UserCRUD.get_users(db, skip=skip, limit=limit)
    return paginate(users)


@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    user = await crud.UserCRUD.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@router.patch("/{user_id}", status_code=200)
async def update_user(user_update_data: UserUpdate, user_id: int, db: AsyncSession = Depends(get_db_session)):
    user_exist = await crud.UserCRUD.get_user(db, user_id=user_id)
    if not user_exist:
        raise HTTPException(status_code=400, detail="The user does not exist")

    await crud.UserCRUD.update_user(db=db, user_id=user_id, update_data=user_update_data)
    raise HTTPException(status_code=200, detail="Successfully update")


@router.delete("/{user_id}", status_code=200)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    user_exist = await crud.UserCRUD.get_user(db, user_id=user_id)
    if not user_exist:
        raise HTTPException(status_code=400, detail="The user does not exist")

    await crud.UserCRUD.delete_user(db=db, user_id=user_id)
    raise HTTPException(status_code=200, detail="Successfully deleted")