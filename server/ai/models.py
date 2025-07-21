from typing import Sequence
from pydantic import BaseModel

from datetime import datetime
from typing import Sequence, Literal

from pydantic import BaseModel, Field

class TraceBase(BaseModel):
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


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


class SideEffectTraceBase(TraceBase):
    kind: Literal["side_effect"] = "side_effect"


class ImageSideEffectTrace(SideEffectTraceBase):
    side_effect_kind: Literal["image_generation"] = "image_generation"
    base64_encoded_image: str


class ProgramExecutionSideEffectTrace(SideEffectTraceBase):
    side_effect_kind: Literal["program_execution"] = "program_execution"
    source_code: str 
    language: str
    output: str


SideEffectTrace = ImageSideEffectTrace | ProgramExecutionSideEffectTrace
Trace = AIMessageTrace | HumanMessageTrace | ToolTrace | SideEffectTrace


class SerializedAgentManager(BaseModel):
    history: Sequence[Trace]
    chat_summary: str
