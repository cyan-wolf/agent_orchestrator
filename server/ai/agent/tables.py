from database.database import Base
from sqlalchemy import Text, ForeignKey, UUID, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

class AgentTemplateTable(Base):
    __tablename__ = "agent_template"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(Text)
    persona: Mapped[str] = mapped_column(Text)
    purpose: Mapped[str] = mapped_column(Text)
    is_switchable_into: Mapped[bool] = mapped_column(Boolean)

    # If this FK is null, then the template is global and immutable.
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), nullable=True)

    agent_tool_associations: Mapped[list["AgentToolAssociationTable"]] = relationship(back_populates="agent_template", cascade="all, delete-orphan")

    tools: Mapped[list["ToolTable"]] = relationship(secondary="agent_tool", back_populates="agent_templates", overlaps="agent_tool_associations")
    

class ToolTable(Base):
    __tablename__ = "tool"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)

    agent_tool_associations: Mapped[list["AgentToolAssociationTable"]] = relationship(back_populates="tool", cascade="all, delete-orphan")

    agent_templates: Mapped[list["AgentTemplateTable"]] = relationship(secondary="agent_tool", back_populates="tools", overlaps="agent_tool_associations")


class AgentToolAssociationTable(Base):
    __tablename__ = "agent_tool"

    # Composite primary key.
    agent_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_template.id", ondelete='CASCADE'), primary_key=True)
    tool_id: Mapped[str] = mapped_column(ForeignKey("tool.id", ondelete='CASCADE'), primary_key=True)

    agent_template: Mapped["AgentTemplateTable"] = relationship(back_populates="agent_tool_associations", overlaps="agent_templates,tools")
    tool: Mapped["ToolTable"] = relationship(back_populates="agent_tool_associations", overlaps="agent_templates,tools")