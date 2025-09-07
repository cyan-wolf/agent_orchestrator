from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

Importance = Literal["not important", "semi-important", "important", "very important"]

def create_event_id() -> str:
    return str(uuid.uuid4())

class Event(BaseModel):
    id: str = Field(default_factory=lambda: create_event_id())
    name: str
    start_time: datetime
    end_time: datetime
    importance: Importance


class EventModification(BaseModel):
    event_id: str
    new_name: str | None
    new_start_time: datetime | None
    new_end_time: datetime | None
    new_importance: Importance | None