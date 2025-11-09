from typing import Annotated

from fastapi import Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.routing import APIRouter

from auth.auth import *

from auth.schemas import CreateNewUser, User
from auth import services

from sqlalchemy.orm import Session
from database.database import get_database

router = APIRouter()

@router.post("/api/login/", tags=["auth"])
async def login_for_authorization_in_cookies(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_database)],
):
    services.try_login_user(db, response, form_data.username, form_data.password)
    return { "message": "Successfully authenticated." }


@router.get("/api/auth-check/", tags=["auth"])
async def auth_check(
    auth_check: Annotated[AuthCheck, Depends(check_user_auth)],
) -> AuthCheck:
    return auth_check


@router.post("/api/register/", tags=["auth"])
async def register(
    response: Response,
    new_user: CreateNewUser,
    db: Annotated[Session, Depends(get_database)],
):    
    services.try_register_and_login_user(db, response, new_user)
    return { "message": "Successfully registered." }


@router.get("/api/logout/", tags=["auth"])
async def logout(response: Response):
    services.logout_user(response)
    return { "message": "Successful logout" }


@router.get("/api/users/me/", response_model=User, tags=["auth"])
async def read_users_me(
    current_user: Annotated[UserTable, Depends(get_current_user)],
) -> User:
    return user_from_db_to_dto(current_user)

