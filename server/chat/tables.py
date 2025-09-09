from sqlalchemy import ForeignKey, Text, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.database import Base
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from auth.tables import UserTable

class ChatTable(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["UserTable"] = relationship(back_populates="chats")