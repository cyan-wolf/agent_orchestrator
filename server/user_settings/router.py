from typing import Annotated
from fastapi import APIRouter, Depends

from auth.auth import get_current_user
from auth.tables import UserTable
from sqlalchemy.orm import Session
from database.database import get_database
from db.placeholder_db import TempDB, get_temp_db
from user_settings.schemas import UserSettings
from user_settings.user_settings import get_settings_table_with_username, settings_to_schema

router = APIRouter()

@router.get("/api/settings/all/", tags=["user_settings"])
def view_all_settings(
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
) -> UserSettings:
    return settings_to_schema(get_settings_table_with_username(db, current_user.username))


@router.post("/api/settings/modify-all/", tags=["user_settings"])
def set_settings(
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    temp_db: Annotated[TempDB, Depends(get_temp_db)],
    new_settings: UserSettings,
):
    settings = get_settings_table_with_username(db, current_user.username)
    settings.timezone = new_settings.timezone
    settings.language = new_settings.language
    settings.city = new_settings.city
    settings.country = new_settings.country
    db.commit()

    # Resets the agents in the chat so that they can properly adapt to the new settings.
    temp_db.reset_runtime_agent_managers_for_user(current_user.username)

    return { "result": "Successfully modified settings." }
