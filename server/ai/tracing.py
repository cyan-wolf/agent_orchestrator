import inspect
from functools import wraps
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



class Tracer:
    def __init__(self):
        self.trace_list: list[Trace] = []

    def add(self, trace: Trace):
        self.trace_list.append(trace)

    def get_history(self) -> Sequence[Trace]:
        return self.trace_list.copy()


def trace(tracer: Tracer):
    def trace_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            ret = func(*args, **kwargs)
            tracer.add(ToolTrace(name=func.__name__, bound_arguments=bound_args.arguments, return_value=ret))
            return ret
        
        return wrapper
    return trace_decorator
