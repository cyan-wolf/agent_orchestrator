from typing import Sequence
from pydantic import BaseModel

from datetime import datetime, timezone
from typing import Sequence, Literal

from pydantic import BaseModel, Field

import uuid

class TraceBase(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=lambda: datetime.now(tz=timezone.utc).timestamp())


class AIMessageTrace(TraceBase):
    kind: Literal["ai_message"] = "ai_message"
    agent_name: str
    content: str
    is_main_agent: bool = Field(default=False)


class HumanMessageTrace(TraceBase):
    kind: Literal["human_message"] = "human_message"
    username: str
    content: str


class ToolTrace(TraceBase):
    kind: Literal["tool"] = "tool"
    called_by: str
    name: str
    bound_arguments: dict
    return_value: str


class ImageCreationTrace(TraceBase):
    kind: Literal["image"] = "image"
    base64_encoded_image: str
    caption: str


Trace = AIMessageTrace | HumanMessageTrace | ToolTrace | ImageCreationTrace

