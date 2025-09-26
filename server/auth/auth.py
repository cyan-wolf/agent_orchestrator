from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import os
from auth.schemas import AuthCheck, CreateNewUser, UserWithPass
from auth.tables import UserTable
from user_settings.tables import UserSettingsTable
from database.database import get_database
from sqlalchemy.orm import Session


class MissingEnvVarException(Exception): pass

def _get_env_raise_if_none(var_name: str) -> str:
    value = os.getenv(var_name)

    if value is None:
        raise MissingEnvVarException(f"missing environment variable '{var_name}'")
    else:
        return value

_SECRET_KEY = _get_env_raise_if_none("AUTH_SECRET_KEY")
_ALGORITHM = _get_env_raise_if_none("AUTH_ALGORITHM")
_ACCESS_TOKEN_EXPIRE_MINUTES = 30

_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

class OAuth2PasswordBearerFromCookies(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: str | None = None,
            scopes: dict[str, str] | None = None,
            auto_error: bool = True,
        ):
            if not scopes:
                scopes = {}
            flows = OAuthFlows(password={"tokenUrl": tokenUrl, "scopes": scopes}) # type: ignore
            super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        authorization = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

OAUTH2_SCHEME = OAuth2PasswordBearerFromCookies(tokenUrl="/api/login/", auto_error=False)


def get_user_by_username(db: Session, username: str) -> UserTable | None:
    return db.query(UserTable).filter(UserTable.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not _verify_password(password, user.hashed_password):
        return False
    return user


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return _PWD_CONTEXT.verify(plain_password, hashed_password)


def create_and_set_access_token(response: Response, user: UserTable) -> None:
    """
    Logs in the user by setting the JWT auth token in the response's cookies. 
    """

    access_token_expires = timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = _create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Set HTTP-only cookie!
    response.set_cookie("access_token", f"Bearer {access_token}", httponly=True)


def _create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _SECRET_KEY, algorithm=_ALGORITHM)
    return encoded_jwt


def try_create_user_with_default_settings(db: Session, new_user: CreateNewUser) -> UserTable:
    """
    This method adds a new user to the DB along with some default settings.
    """

    if get_user_by_username(db, new_user.username.strip()) is not None:
        raise HTTPException(status_code=400, detail=f"User '{new_user.username}' already exists.")
    
    hashed_password = _get_password_hash(new_user.password)
    
    user = UserTable(
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        hashed_password=hashed_password,
    )
    db.add(user)
    
    # A flush needs to be done so that SQLAlchemy populates the user.id field.
    db.flush()

    user_settings = UserSettingsTable(user_id=user.id)

    db.add(user_settings)
    db.commit()

    return user


def _get_password_hash(password: str) -> str:
    return _PWD_CONTEXT.hash(password)


# This function is used for dependency injection directly, so the token and 
# database session need to be marked as FastAPI dependencies. 
async def get_current_user(token: Annotated[str, Depends(OAUTH2_SCHEME)], db: Annotated[Session, Depends(get_database)]) -> UserTable:
    user = await _get_curr_user_from_db_impl(token, db)
    assert user is not None
    return user


# This function is used for dependency injection directly, so the token and 
# database session need to be marked as FastAPI dependencies. 
async def check_user_auth(token: Annotated[str, Depends(OAUTH2_SCHEME)], db: Annotated[Session, Depends(get_database)]) -> AuthCheck:
    user_from_db = await _get_curr_user_from_db_impl(token, db, should_raise_credentials_exception=False)
    curr_user_exists = user_from_db is not None

    if curr_user_exists:
        user = user_from_db_to_dto(user_from_db)
    else:
        user = None
    
    return AuthCheck(
        is_auth=curr_user_exists, 
        user=user,
    )


async def _get_curr_user_from_db_impl(
    token: str, 
    db: Session, 
    should_raise_credentials_exception: bool = True,
) -> UserTable | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            if should_raise_credentials_exception:
                raise credentials_exception
            else:
                return None
            
        user = get_user_by_username(db, username)

    except InvalidTokenError:
        if should_raise_credentials_exception:
            raise credentials_exception
        else:
            return None

    if user is None:
        if should_raise_credentials_exception:
            raise credentials_exception
        else:
            return None
    
    return user


def user_from_db_to_dto(user_from_db: UserTable) -> UserWithPass:
    return UserWithPass(
        id=user_from_db.id,
        username=user_from_db.username,
        email=user_from_db.email,
        full_name=user_from_db.full_name,
        hashed_password=user_from_db.hashed_password,
    )

