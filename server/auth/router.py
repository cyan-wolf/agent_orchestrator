from typing import Annotated

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.routing import APIRouter

from auth.auth import *

from auth.models import CreateNewUser, Token, User

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
    # TODO: Improve registration validation.
    
    if get_user_by_username(db, new_user.username.strip()) is not None:
        raise HTTPException(status_code=400, detail=f"User '{new_user.username}' already exists.")
    
    # Add a new user record to the DB.
    hashed_password = get_password_hash(new_user.password)
    user = UserTable(
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()

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

