
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from auth.schemas import CreateNewUser
from auth.auth import authenticate_user, create_and_set_access_token, try_create_user_with_default_settings


def try_login_user(db: Session, response: Response, username: str, password: str) -> None:
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Logs in the user.
    create_and_set_access_token(response, user)


def try_register_and_login_user(db: Session, response: Response, new_user_schema: CreateNewUser) -> None:
    user = try_create_user_with_default_settings(db, new_user_schema)

    # Logs in the user.
    create_and_set_access_token(response, user)


def logout_user(response: Response) -> None:
    response.delete_cookie("access_token")