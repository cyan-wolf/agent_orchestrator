from database.database import Base
from sqlalchemy import Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from auth.tables import UserTable

class UserSettingsTable(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    timezone: Mapped[str] = mapped_column(Text, default="Etc/UTC")
    language: Mapped[str] = mapped_column(Text, default="English")
    city: Mapped[str] = mapped_column(Text, default="Unknown")
    country: Mapped[str] = mapped_column(Text, default="Unknown")

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), unique=True, nullable=False)

    user: Mapped["UserTable"] = relationship(back_populates="settings")
    