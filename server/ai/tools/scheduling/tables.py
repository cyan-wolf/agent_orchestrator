from sqlalchemy import Integer, Text, UUID, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.database import Base
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from auth.tables import UserTable

class EventTable(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text)
    start_time: Mapped[int] = mapped_column(Integer)
    end_time: Mapped[int] = mapped_column(Integer)
    importance: Mapped[str] = mapped_column(Text)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserTable"] = relationship(back_populates="events")