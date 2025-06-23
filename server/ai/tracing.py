import inspect
from functools import wraps
from datetime import datetime
import json

class Trace:
    def __init__(self):
        self.time = datetime.now()
        self.type = self.get_trace_type()

    def get_trace_type(self) -> str:
        return "unknown"
    
    def as_json(self) -> str:
        return json.dumps({ **self.__dict__ }, default=str)

class AIMessageTrace(Trace):
    def __init__(self, by: str, content: str, as_main_agent: bool = False):
        super().__init__()
        self.by = by
        self.content = content
        self.as_main_agent = as_main_agent

    def __repr__(self) -> str:
        return f"{self.time} (message): {self.content} by {self.by}, is_main_agent: {self.as_main_agent}"
    
    def get_trace_type(self) -> str:
        return "ai_message"


class HumanMessageTrace(Trace):
    def __init__(self, username: str, content: str):
        super().__init__()
        self.username = username
        self.content = content

    def __repr__(self) -> str:
        return f"{self.time} (human_message): {self.username} prompted '{self.content}'"
    
    def get_trace_type(self) -> str:
        return "human_message"


class ToolTrace(Trace):
    def __init__(self, name: str, bound_arguments: dict, ret_val):
        super().__init__()
        self.name = name
        self.bound_arguments = bound_arguments
        self.ret_val = ret_val

    def __repr__(self) -> str:
        return f"{self.time} (tool): `{self.name}` `{self.bound_arguments}` -> `{self.ret_val}`"
    
    def get_trace_type(self) -> str:
        return "tool"
    

class SideEffectTrace(Trace):
    def __init__(self):
        super().__init__()
        self.side_effect_type = self.get_side_effect_type()

    def get_trace_type(self) -> str:
        return "side_effect"
    
    def get_side_effect_type(self) -> str:
        return "unknown"


class ImageSideEffectTrace(SideEffectTrace):
    def __init__(self, base64_encoded_image: str):
        super().__init__()
        self.base64_encoded_image = base64_encoded_image
    
    def get_side_effect_type(self) -> str:
        return "image_generation"


class ProgramRunningSideEffectTrace(SideEffectTrace):
    def __init__(self, source_code: str, language: str, output: str):
        super().__init__()
        self.source_code = source_code
        self.langauge = language
        self.output = output

    def get_side_effect_type(self) -> str:
        return "program_running"


class Tracer:
    def __init__(self):
        self.trace_list: list[Trace] = []

    def add(self, trace: Trace):
        self.trace_list.append(trace)

    def get_history(self) -> list[Trace]:
        return self.trace_list.copy()


def trace(tracer: Tracer):
    def trace_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            ret = func(*args, **kwargs)
            tracer.add(ToolTrace(func.__name__, bound_args.arguments, ret))
            return ret
        
        return wrapper
    return trace_decorator
