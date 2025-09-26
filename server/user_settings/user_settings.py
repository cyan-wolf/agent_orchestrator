from auth.auth import get_user_by_username
from user_settings.schemas import UserSettings
from user_settings.tables import UserSettingsTable
from sqlalchemy.orm import Session

def get_settings_table_with_username(db: Session, username: str) -> UserSettingsTable:
    user = get_user_by_username(db, username)
    assert user
    return user.settings


def settings_to_schema(settings_from_db: UserSettingsTable) -> UserSettings:
    return UserSettings(
        timezone=settings_from_db.timezone,
        language=settings_from_db.language, # type: ignore # assume that the settings from the DB are valid
        city=settings_from_db.city,
        country=settings_from_db.country,
    )

