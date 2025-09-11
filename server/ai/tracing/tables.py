from sqlalchemy import ForeignKey, Text, UUID, Float, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.database import Base
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chat.tables import ChatTable

class TraceTable(Base):
    __tablename__ = "traces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[float] = mapped_column(Float)
    kind: Mapped[str] = mapped_column(Text)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"))

    chat: Mapped["ChatTable"] = relationship(back_populates="trace_history")

    __mapper_args__ = {
        'polymorphic_on': 'kind',
    }


class AIMessageTraceTable(TraceTable):
    __tablename__ = None

    agent_name: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, use_existing_column=True, nullable=True)
    is_main_agent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'ai_message'
    }


class HumanMessageTraceTable(TraceTable):
    __tablename__ = None

    username: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, use_existing_column=True, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'human_message'
    }


class ToolTraceTable(TraceTable):
    __tablename__ = None

    called_by: Mapped[str] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    bound_arguments: Mapped[str] = mapped_column(Text, nullable=True) # JSON
    return_value: Mapped[str] = mapped_column(Text, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'tool'
    }


class ImageCreationTraceTable(TraceTable):
    __tablename__ = None

    base64_encoded_image: Mapped[str] = mapped_column(Text, nullable=True)
    caption: Mapped[str] = mapped_column(Text, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'image'
    }
