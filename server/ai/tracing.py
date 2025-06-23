import inspect
from functools import wraps
from datetime import datetime
from typing import Sequence

from pydantic import BaseModel, Field

class Trace(BaseModel):
    time: datetime = Field(default_factory=datetime.now)


class AIMessageTrace(Trace):
    agent_name: str
    content: str
    is_main_agent: bool = Field(default=False)


class HumanMessageTrace(Trace):
    username: str
    content: str

class ToolTrace(Trace):
    name: str
    bound_arguments: dict
    return_value: str


class SideEffectTrace(Trace):
    pass

class ImageSideEffectTrace(SideEffectTrace):
    base64_encoded_image: str


class ProgramRunningSideEffectTrace(SideEffectTrace):
    source_code: str 
    language: str
    output: str


TraceUnion = AIMessageTrace | HumanMessageTrace | ToolTrace | SideEffectTrace

class Tracer:
    def __init__(self):
        self.trace_list: list[TraceUnion] = []

    def add(self, trace: TraceUnion):
        self.trace_list.append(trace)

    def get_history(self) -> Sequence[TraceUnion]:
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
