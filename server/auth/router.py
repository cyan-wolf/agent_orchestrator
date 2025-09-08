from typing import Annotated

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.routing import APIRouter

from auth.auth import *

from auth.schemas import CreateNewUser, Token, User

from sqlalchemy.orm import Session
from database.database import get_database

router = APIRouter()

@router.post("/api/token/", tags=["auth"])
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_database)],
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_and_set_access_token(response, user)

    # TODO: try to remove this, 
    # the client doesn't need the JWT token since it is set on a cookie
    return Token(access_token=access_token, token_type="bearer")


@router.get("/api/auth-check/", tags=["auth"])
async def auth_check(
    auth_check: Annotated[AuthCheck, Depends(check_user_auth)],
) -> AuthCheck:
    return auth_check


@router.post("/api/register/")
async def register(
    response: Response,
    new_user: CreateNewUser,
    db: Annotated[Session, Depends(get_database)],
):    
    user = create_user_with_default_settings(db, new_user)

    # Logs in the user.
    create_and_set_access_token(response, user)

    return { "message": "Successfully registered." }


@router.get("/api/logout/", tags=["auth"])
async def logout(response: Response):
    response.delete_cookie("access_token")
    return { "message": "Successful logout" }


@router.get("/api/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[UserTable, Depends(get_current_user)],
) -> User:
    return user_from_db_to_dto(current_user)

