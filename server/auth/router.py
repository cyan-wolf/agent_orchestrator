from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.routing import APIRouter

from auth.auth import *

from auth.models import CreateNewUser, Token
from db.placeholder_db import TempDB, get_db

router = APIRouter()

@router.post("/api/token/", tags=["auth"])
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[TempDB, Depends(get_db)]
) -> Token:
    user = authenticate_user(db.user_db, form_data.username, form_data.password)
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
    db: Annotated[TempDB, Depends(get_db)]
):
    # TODO: Improve registration validation.
    
    if new_user.username.strip() in db.user_db.users:
        raise HTTPException(status_code=400, detail=f"User '{new_user.username}' already exists.")
    
    if len(new_user.password) < 8:
        raise HTTPException(status_code=400, detail="Password is too weak; must be at least 8 characters.")
    
    hashed_password = get_password_hash(new_user.password)

    user = UserInDB(**new_user.__dict__, hashed_password=hashed_password)

    db.user_db.users[new_user.username] = user
    db.store_users_db()

    # Logs in the user.
    create_and_set_access_token(response, user)

    return { "message": "Successfully registered." }


@router.get("/api/logout/", tags=["auth"])
async def logout(response: Response):
    response.delete_cookie("access_token")
    return { "message": "Successful logout" }


@router.get("/api/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/api/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]