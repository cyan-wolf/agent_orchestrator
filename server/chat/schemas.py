from pydantic import BaseModel, field_validator
import uuid


class ChatBase(BaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, value: str) -> str:
        if len(value) == 0 or len(value) > 20:
            raise ValueError("Chat name length must be greater than 0 and less than 20")
        return value


class CreateNewChat(ChatBase):
    pass


class Chat(ChatBase):
    id: uuid.UUID


class UserTextRequest(BaseModel):
    user_message: str
