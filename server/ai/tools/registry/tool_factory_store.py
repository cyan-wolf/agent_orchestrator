from typing import Callable
from ai.agent_manager.agent_context import AgentCtx

ToolFactory = Callable[[AgentCtx], Callable]
"""
A tool factory is a function that injects agent context into a callable 
which is the tool used by the runtime agents.
"""

class ToolFactoryInMememoryStore:
    """
    In-memory registry for tool factories. Runtime agents get their tools (which are callables) 
    from these tool factories. It is done this way so that the factories can inject the necessary context to 
    the tool callables.
    """

    def __init__(self):
        # tool ID -> tool factory
        self._in_memory_store: dict[str, ToolFactory] = {}


    def get(self, tool_id: str) -> ToolFactory | None:
        return self._in_memory_store.get(tool_id)
    

    def register_factory(self, tool_id: str, factory: ToolFactory):
        self._in_memory_store[tool_id] = factory


_SINGLETON_MEM_STORE = ToolFactoryInMememoryStore()

def get_tool_factory_in_mem_store() -> ToolFactoryInMememoryStore:
    """
    Returns the singleton in-memory tool factory store.
    """
    return _SINGLETON_MEM_STORE