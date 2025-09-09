from pydantic import BaseModel
from ai.tools.scheduling.schemas import Event
from user_settings.schemas import UserSettings

class UserSettingsTempDB(BaseModel):
    # username -> user settings
    user_settings: dict[str, UserSettings]

