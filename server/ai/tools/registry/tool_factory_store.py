from typing import Callable
from ai.agent_manager.agent_context import AgentCtx

ToolFactory = Callable[[AgentCtx], Callable]

class ToolFactoryInMememoryStore:
    def __init__(self):
        # tool ID -> tool factory
        self._in_memory_store: dict[str, ToolFactory] = {}


    def get(self, tool_id: str) -> ToolFactory | None:
        return self._in_memory_store.get(tool_id)
    

    def register_factory(self, tool_id: str, factory: ToolFactory):
        self._in_memory_store[tool_id] = factory


_SINGLETON_MEM_STORE = ToolFactoryInMememoryStore()

def get_tool_factory_in_mem_store() -> ToolFactoryInMememoryStore:
    return _SINGLETON_MEM_STORE