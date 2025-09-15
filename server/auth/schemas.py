from pydantic import BaseModel, field_validator
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: str 
    full_name: str


class CreateNewUser(UserBase):
    password: str

    @field_validator('username')
    def validate_username(cls, value: str) -> str:
        if len(value) <= 5:
            raise ValueError("Username must be at least 5 characters in length")
        return value

    @field_validator('password')
    def valdiate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password is too weak; must be at least 8 characters.")
        return value


class User(UserBase):
    id: uuid.UUID


class UserWithPass(User):
    hashed_password: str


class AuthCheck(BaseModel):
    is_auth: bool
    user: User | None