from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.database import Base
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chat.tables import ChatTable

class ChatSummaryTable(Base):
    __tablename__ = "chat_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"))

    chat: Mapped["ChatTable"] = relationship(back_populates="summaries")
