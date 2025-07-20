
from pydantic import BaseModel
from auth.models import UserInDB
from chat.models import Chat


class UserTempDB(BaseModel):
    # username -> user
    users: dict[str, UserInDB]


class ChatTempDB(BaseModel):
    # username -> list of chats
    chats: dict[str, list[Chat]]