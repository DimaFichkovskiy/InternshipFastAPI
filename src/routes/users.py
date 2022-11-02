from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate

from src import schemas
from src.crud import UserCRUD
from src.database import AsyncSession, get_db_session
from src.routes.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/", response_model=Page[schemas.User])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session),
        current_user: schemas.User = Depends(get_current_user)
):
    users = await UserCRUD.get_users(db=db, skip=skip, limit=limit)
    return paginate(users)


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
        user_id: int,
        db: AsyncSession = Depends(get_db_session),
        current_user: schemas.User = Depends(get_current_user)
):
    user = await UserCRUD.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@router.patch("/update_user_info", response_model=schemas.User)
async def update_user_info(
        update_data: schemas.UserInfoUpdate,
        db: AsyncSession = Depends(get_db_session),
        current_user: schemas.User = Depends(get_current_user)
) -> schemas.User:
    if (update_data.first_name and update_data.last_name) is None:
        raise HTTPException(status_code=400, detail="There is not enough data to update")

    return await UserCRUD.update_user_info(db=db, user_id=current_user.id, update_data=update_data)


@router.patch("/update_user_password", response_model=schemas.UpdatePasswordResponse, status_code=201)
async def update_user_password(
        update_data: schemas.UserPasswordUpdate,
        db: AsyncSession = Depends(get_db_session),
        current_user: schemas.User = Depends(get_current_user)
) -> schemas.UpdatePasswordResponse:
    if update_data.password is None:
        raise HTTPException(status_code=400, detail="The password field must not be empty")

    user = await UserCRUD.update_user_password(db=db, user_id=current_user.id, update_data=update_data)
    if not user:
        raise HTTPException(status_code=400, detail="The new password matches the old one")

    response = schemas.UpdatePasswordResponse
    response.status_code = status.HTTP_201_CREATED
    response.body = "Password successfully updated"
    return response


@router.delete("/delete_me", response_model=schemas.DeleteUserResponse, status_code=200)
async def delete_user(
        db: AsyncSession = Depends(get_db_session), current_user: schemas.User = Depends(get_current_user)
) -> schemas.DeleteUserResponse:
    await UserCRUD.delete_user(db=db, user_id=current_user.id)

    response = schemas.DeleteUserResponse
    response.status_code = status.HTTP_200_OK
    response.body = "Success delete user"
    return response
