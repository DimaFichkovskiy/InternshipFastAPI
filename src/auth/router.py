import email

from fastapi import APIRouter, Depends, HTTPException

from src import crud
from src.database import AsyncSession, get_db_session
from .schemas import SignUp, SignIn
from src.users.schemas import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/login")
def sign_in():
    pass


@router.post("/register", status_code=201, response_model=User)
async def sign_up(new_user: SignUp, db: AsyncSession = Depends(get_db_session)):
    email_exist = await crud.UserCRUD.get_user_by_email(db, email=new_user.email)
    if email_exist:
        raise HTTPException(status_code=400, detail="Email already registered")

    elif new_user.password != new_user.confirm_password:
        raise HTTPException(status_code=400, detail="Сonfirm password does not match password")

    await crud.UserCRUD.create_user(db=db, user=new_user)
    return new_user
