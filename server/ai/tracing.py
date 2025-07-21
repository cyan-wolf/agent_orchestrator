import inspect
from functools import wraps
from typing import Sequence

from ai.models import Trace, ToolTrace

class Tracer:
    def __init__(self, history: Sequence[Trace] | None = None):
        if history is None:
            self.trace_list: list[Trace] = []
        else:
            self.trace_list = list(history)

    def add(self, trace: Trace):
        self.trace_list.append(trace)

    def get_history(self) -> Sequence[Trace]:
        return self.trace_list.copy()


def trace(agent_manager):
    def trace_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            ret = func(*args, **kwargs)
            tracer: Tracer = agent_manager.tracer
            tracer.add(ToolTrace(
                # "current_agent" is the agent currently in control
                called_by=agent_manager.agents["current_agent"].name,
                name=func.__name__, 
                bound_arguments=bound_args.arguments, 
                return_value=ret,
            ))
            return ret
        
        return wrapper
    return trace_decorator
