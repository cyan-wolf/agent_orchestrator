from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

import os

from auth.models import AuthCheck, TokenData, User, UserInDB
from db.models import UserTempDB
from db.placeholder_db import TempDB, get_db

class MissingEnvVarException(Exception): pass

def get_env_raise_if_none(var_name: str) -> str:
    value = os.getenv(var_name)

    if value is None:
        raise MissingEnvVarException(f"missing environment variable '{var_name}'")
    else:
        return value

SECRET_KEY = get_env_raise_if_none("AUTH_SECRET_KEY")
ALGORITHM = get_env_raise_if_none("AUTH_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

oauth2_scheme = OAuth2PasswordBearerFromCookies(tokenUrl="/api/token/", auto_error=False)



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: UserTempDB, username: str) -> UserInDB | None:
    if username in db.users:
        user = db.users[username]
        return user
    else:
        return None
        

def authenticate_user(db: UserTempDB, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def _get_curr_user_impl(token: Annotated[str, Depends(oauth2_scheme)], db: UserTempDB, should_raise_credentials_exception: bool = True):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            if should_raise_credentials_exception:
                raise credentials_exception
            else:
                return None
            
        token_data = TokenData(username=username)
        user = get_user(db, username=username)

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


async def check_user_auth(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[TempDB, Depends(get_db)]) -> AuthCheck:
    user = await _get_curr_user_impl(token, db.user_db, should_raise_credentials_exception=False)
    
    return AuthCheck(
        is_auth=user is not None, 
        user=user,
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[TempDB, Depends(get_db)]) -> User:
    user = await _get_curr_user_impl(token, db.user_db)
    assert user is not None
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


