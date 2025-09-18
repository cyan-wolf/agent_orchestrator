from typing import Literal
from pydantic import BaseModel
from datetime import datetime
import uuid

Importance = Literal["not important", "semi-important", "important", "very important"]


class EventBase(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    importance: Importance


class CreateEvent(EventBase): pass


class Event(EventBase):
    id: uuid.UUID


class EventModification(BaseModel):
    event_id: uuid.UUID
    new_name: str | None
    new_start_time: datetime | None
    new_end_time: datetime | None
    new_importance: Importance | None
