import http.client

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer

from src.utils import VerifyToken
from src import crud
from src.database import AsyncSession, get_db_session
from .schemas import SignUp, SignIn
from src.users.schemas import User
from src.config import Config

token_auth_scheme = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/login", status_code=200, response_model=User)
async def sign_in(user_login_data: SignIn, db: AsyncSession = Depends(get_db_session)):
    user = await crud.UserCRUD.authenticate(db=db, login_data=user_login_data)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return user


@router.get("/login/me", response_model=User)
async def get_me(
    response: Response,
    token: str = Depends(token_auth_scheme),
    db: AsyncSession = Depends(get_db_session)
):

    result = VerifyToken(token.credentials).verify()

    if result.get("status"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result

    user_email = result.get("email")
    user = await crud.UserCRUD.get_user_by_email(db=db, email=user_email)

    return user


@router.post("/register", status_code=201, response_model=User)
async def sign_up(new_user: SignUp, db: AsyncSession = Depends(get_db_session)):
    email_exist = await crud.UserCRUD.get_user_by_email(db, email=new_user.email)
    if email_exist:
        raise HTTPException(status_code=400, detail="Email already registered")

    config = Config.set_up_auth0()

    conn = http.client.HTTPSConnection(config["DOMAIN"])
    pyload = "{" \
             f"\"client_id\":\"{config['CLIENT_ID']}\"," \
             f"\"client_secret\":\"{config['CLIENT_SECRET']}\"," \
             f"\"audience\":\"{config['API_AUDIENCE']}\"," \
             f"\"email\":\"{new_user.email}\"," \
             f"\"password\":\"{new_user.password}\"," \
             f"\"connection\":\"{config['CONNECTION']}\"," \
             f"\"grant_type\":\"client_credentials\"" \
             "}"

    headers = {"content-type": "application/json"}

    conn.request("POST", "/dbconnections/signup", pyload, headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    return await crud.UserCRUD.create_user(db=db, user=new_user)
