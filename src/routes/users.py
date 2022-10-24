from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate

from src import crud, models
from src.database import AsyncSession, get_db_session
from src.schemas.user import User, UserUpdate
from src.routes.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/", response_model=Page[User])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    users = await crud.UserCRUD.get_users(db, skip=skip, limit=limit)
    return paginate(users)


@router.get("/{user_id}", response_model=User)
async def read_user(
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    user = await crud.UserCRUD.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=User)
async def update_user(
        user_update_data: UserUpdate,
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    user_exist = await crud.UserCRUD.get_user(db, user_id=user_id)
    if not user_exist:
        raise HTTPException(status_code=400, detail="The user does not exist")

    return await crud.UserCRUD.update_user(db=db, user_id=user_id, update_data=user_update_data)


@router.delete("/{user_id}", status_code=200)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: models.User = Depends(get_current_user)
):
    user_exist = await crud.UserCRUD.get_user(db, user_id=user_id)
    if not user_exist:
        raise HTTPException(status_code=400, detail="The user does not exist")

    await crud.UserCRUD.delete_user(db=db, user_id=user_id)
    return {"status": "OK", "code": "200", "message": "Success delete data"}
