from pydantic import BaseModel, Field, field_validator
from typing import Literal
import zoneinfo

SupportedLanguage = Literal["English", "Spanish", "French", "German", "Russian", "Chinese", "Arabic"]

class UserSettings(BaseModel):
    timezone: str = Field(default='Etc/UTC')
    language: SupportedLanguage = Field(default='English')
    city: str = Field(default='Unknown')
    country: str = Field(default='Unknown')

    @field_validator('timezone')
    def validate_timezone(cls, value: str) -> str:
        if value not in zoneinfo.available_timezones():
            raise ValueError(f"'{value}' is not a valid IANA timezone.")
        return value
