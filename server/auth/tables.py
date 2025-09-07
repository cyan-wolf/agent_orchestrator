from sqlalchemy import Column, Text, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.database import Base
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ai.tools.scheduling.tables import EventTable

class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(Text)
    hashed_password: Mapped[str] = mapped_column(Text)

    events: Mapped[list["EventTable"]] = relationship(back_populates="user")