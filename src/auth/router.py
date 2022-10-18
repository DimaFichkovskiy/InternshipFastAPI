from fastapi import APIRouter, Depends, HTTPException

from src.crud import UserCRUD
from src.database import AsyncSession, get_db_session
from .schemas import SignUp, SignIn

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/login")
def sign_in():
    pass


@router.post("/register", response_model=SignUp)
def sign_up(user: SignUp, db: AsyncSession = Depends(get_db_session)):
    db_user = UserCRUD.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return UserCRUD.create_user(db=db, user=user)
