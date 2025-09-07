
from pydantic import BaseModel
from chat.schemas import ChatInDB
from ai.tools.scheduling.schemas import Event
from user_settings.schemas import UserSettings

class ChatTempDB(BaseModel):
    # username -> list of chats
    chats: dict[str, list[ChatInDB]]


class ScheduleTempDB(BaseModel):
    # username -> list of events
    schedules: dict[str, list[Event]]


class UserSettingsTempDB(BaseModel):
    # username -> user settings
    user_settings: dict[str, UserSettings]

