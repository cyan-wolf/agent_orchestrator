
from pydantic import BaseModel
from auth.models import UserInDB
from chat.models import Chat


class UserTempDB(BaseModel):
    # username -> user
    users: dict[str, UserInDB]


class ChatTempDB(BaseModel):
    # chat ID -> chat
    chats: dict[str, Chat]