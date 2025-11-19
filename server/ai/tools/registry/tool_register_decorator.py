from ai.tools.registry.tool_factory_store import ToolFactory, get_tool_factory_in_mem_store

def register_tool_factory(tool_id: str):
    """
    Registers a tool factory under the given tool ID.
    This is for associating tools (using their tool IDs) with their factory.
    """
    
    def tool_factory_register_decorator(factory: ToolFactory):
        get_tool_factory_in_mem_store().register_factory(tool_id, factory)
        return factory

    return tool_factory_register_decorator
