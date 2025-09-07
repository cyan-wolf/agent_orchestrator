from pydantic import BaseModel, field_validator
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str | None = None
    full_name: str | None = None


class UserWithPass(User):
    hashed_password: str


class CreateNewUser(User):
    password: str

    @field_validator('password')
    def valdiate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password is too weak; must be at least 8 characters.")
        return value


class AuthCheck(BaseModel):
    is_auth: bool
    user: User | None