from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from auth.auth import *

from fastapi.routing import APIRouter

router = APIRouter()

@router.post("/api/token/", tags=["auth"])
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Set HTTP-only cookie!
    response.set_cookie("access_token", f"Bearer {access_token}", httponly=True)

    # TODO: try to remove this, 
    # the client doesn't need the JWT token since it is set on a cookie
    return Token(access_token=access_token, token_type="bearer")


@router.get("/api/auth-check/", tags=["auth"])
async def auth_check(
    auth_check: Annotated[AuthCheck, Depends(check_user_auth)],
) -> AuthCheck:
    return auth_check


@router.get("/api/logout", tags=["auth"])
async def logout(response: Response):
    response.delete_cookie("access_token")
    return { "message": "Successful logout" }


@router.get("/api/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/api/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]