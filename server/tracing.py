import inspect
from functools import wraps
from datetime import datetime
from langchain_core.messages import BaseMessage

class Trace:
    def __init__(self):
        self.time = datetime.now()

class MessageTrace(Trace):
    def __init__(self, message: BaseMessage):
        super().__init__()
        self.message = message

    def __repr__(self) -> str:
        return f"{self.time} (message): {self.message.content}"

class ToolTrace(Trace):
    def __init__(self, name: str, bound_arguments: dict, ret_val):
        super().__init__()
        self.name = name
        self.bound_arguments = bound_arguments
        self.ret_val = ret_val

    def __repr__(self) -> str:
        return f"{self.time} (tool): `{self.name}` `{self.bound_arguments}` -> `{self.ret_val}`"

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
