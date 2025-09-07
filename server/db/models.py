
from pydantic import BaseModel
from auth.models import UserWithPass
from chat.models import ChatInDB
from ai.tools.scheduling.models import Event
from user_settings.models import UserSettings

class UserTempDB(BaseModel):
    # username -> user
    users: dict[str, UserWithPass]


class ChatTempDB(BaseModel):
    # username -> list of chats
    chats: dict[str, list[ChatInDB]]


class ScheduleTempDB(BaseModel):
    # username -> list of events
    schedules: dict[str, list[Event]]


class UserSettingsTempDB(BaseModel):
    # username -> user settings
    user_settings: dict[str, UserSettings]

