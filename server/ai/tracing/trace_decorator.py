import inspect
from functools import wraps

from ai.tracing.schemas import ToolTrace
from ai.agent_manager.agent_context import AgentCtx

from ai.tracing.tracer import Tracer

def trace(ctx: AgentCtx):
    """
    This function acts as a decorator that takes an agent context `ctx` object. 
    This decorator logs the arguments and return value of the function that it decorates onto 
    the `Tracer` associated with the agent manager in the context object.
    """
    def trace_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            ret = func(*args, **kwargs)
            tracer: Tracer = ctx.manager.get_tracer()
            tracer.add(ctx.db, ToolTrace(
                # "current_agent" is the agent currently in control
                called_by=ctx.manager.get_agent_dict()["current_agent"].name,
                name=func.__name__, 
                bound_arguments=bound_args.arguments, 
                return_value=str(ret),
            ))
            return ret
        
        return wrapper
    return trace_decorator
