from datetime import datetime
from zoneinfo import ZoneInfo
from db.placeholder_db import get_db
from user_settings.models import UserSettings


def _get_utc_offset(timezone_iana: str) -> float:
    SECS_PER_DAY = 3600

    now = datetime.now(tz=ZoneInfo(timezone_iana))
    offset = now.utcoffset().total_seconds() / SECS_PER_DAY # type: ignore
    return offset


def get_timezone_string(username: str) -> str:
    return get_or_init_default(username).timezone


def get_timezone_offset(username: str) -> float:
    return _get_utc_offset(get_timezone_string(username))


def get_city(username: str) -> str:
    city = get_or_init_default(username).city
    return "unknown" if city is None else city


def get_country(username: str) -> str:
    country = get_or_init_default(username).country
    return "unknown" if country is None else country


def get_or_init_default(username: str) -> UserSettings:
    """
    Gets the settings for the given user. Initalizes the user 
    with some default settings if they do not exist.
    """
    db = get_db()
    settings = db.user_settings_db.user_settings.get(username)

    if settings is None:
        # Initialize the user's settings with default values.
        settings = UserSettings()
        db.user_settings_db.user_settings[username] = settings
        db.store_user_settings_db()

    return settings



