
from pydantic import BaseModel
from auth.models import UserInDB
from chat.models import ChatInDB


class UserTempDB(BaseModel):
    # username -> user
    users: dict[str, UserInDB]


class ChatTempDB(BaseModel):
    # username -> list of chats
    chats: dict[str, list[ChatInDB]]