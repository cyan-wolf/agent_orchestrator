from ai.tools.registry.tool_factory_store import ToolFactory, get_tool_factory_in_mem_store
from functools import wraps


def register_tool_factory(tool_id: str):
    
    def tool_factory_register_decorator(factory: ToolFactory):
        get_tool_factory_in_mem_store().register_factory(tool_id, factory)
        return factory

    return tool_factory_register_decorator
