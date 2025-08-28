from typing import Annotated
from fastapi import APIRouter, Depends

from auth.auth import get_current_user
from auth.models import User
from db.placeholder_db import TempDB, get_db
from user_settings.models import UserSettings
from user_settings.user_settings import get_or_init_default

router = APIRouter()

@router.get("/api/settings/all/", tags=["user_settings"])
def view_all_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[TempDB, Depends(get_db)],
) -> UserSettings:
    return get_or_init_default(current_user.username)


@router.post("/api/settings/modify-all/", tags=["user_settings"])
def set_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[TempDB, Depends(get_db)],
    new_settings: UserSettings,
):
    db.user_settings_db.user_settings[current_user.username] = new_settings
    db.store_user_settings_db()

    return {"response": "successfully modified settings"}
