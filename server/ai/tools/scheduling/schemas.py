from typing import Literal
from pydantic import BaseModel
from datetime import datetime
import uuid

Importance = Literal["not important", "semi-important", "important", "very important"]
"""
A union type representing he importance that an event can have.
"""

class EventBase(BaseModel):
    """
    The base-class for events.
    """
    name: str
    start_time: datetime
    end_time: datetime
    importance: Importance


class CreateEvent(EventBase): 
    """
    Used for creating an event with the provided attributes.
    """
    pass


class Event(EventBase):
    """
    An event with an ID. Corresponds to how events are stored in the DB.
    """
    id: uuid.UUID


class EventModification(BaseModel):
    """
    Used for fine-grained modification of the attributes of an existing event. 
    An attribure being `None` signifies that the attribute should not be modified.
    """
    event_id: uuid.UUID
    new_name: str | None
    new_start_time: datetime | None
    new_end_time: datetime | None
    new_importance: Importance | None
