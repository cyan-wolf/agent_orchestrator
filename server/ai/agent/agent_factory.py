from ai.agent.runtime.agent_interface import IAgent
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.registry.tool_factory_store import get_tool_factory_in_mem_store, ToolFactoryInMememoryStore, ToolFactory
from ai.agent.templates.schemas import AgentTemplateSchema
from ai.agent.runtime.runtime_agent import RuntimeAgent
from ai.agent.templates.agent_templates import get_all_agent_template_schemas_for_user
from ai.agent.runtime.agent_tool_callback_logger import AgentToolCallbackLogger
from ai.tracing.tracer import Tracer
from auth.tables import UserTable
from langgraph.checkpoint.memory import InMemorySaver
from typing import Callable

# Side effect imports to register the tools.
import ai.tools.control_flow as _
import ai.tools.generic_tools as _
import ai.tools.image_generator as _
import ai.tools.web_searching as _
import ai.tools.code_sandbox.coding_tools as _
import ai.tools.math.math_tools as _
import ai.tools.scheduling.scheduling_tools as _

def assert_tool_factory_exists(tool_factory_store: ToolFactoryInMememoryStore, tool_id: str) -> ToolFactory:
    """
    Asserts that the tool factory associated with the given tool ID was registered to the tool factory in-memory store.
    """
    tool_factory = tool_factory_store.get(tool_id)

    if tool_factory is None:
        raise ValueError(f"Fatal error: tool with ID `{tool_id}` was not registered")
    
    return tool_factory


def extract_tool_from_factory(tool_factory_store: ToolFactoryInMememoryStore, ctx: AgentCtx, tool_id: str) -> Callable:
    """
    Extracts the Python callable (usable by the runtime agents) from the tool factory associated with the given tool ID.
    """
    tool_factory = assert_tool_factory_exists(tool_factory_store, tool_id)
    return tool_factory(ctx)


def runtime_agent_from_agent_template(
    ctx: AgentCtx, 
    owner: UserTable, 
    tool_factory_store: ToolFactoryInMememoryStore, 
    agent_template: AgentTemplateSchema,
    tracer: Tracer,
) -> RuntimeAgent:
    """
    Loads a runtime agent from an agent template schema.
    """
    
    tools: list[Callable] = [
        extract_tool_from_factory(tool_factory_store, ctx, tool_schema.id) 
        for tool_schema in agent_template.tools
    ]

    return RuntimeAgent(
        name=agent_template.name,
        persona=agent_template.persona,
        purpose=agent_template.purpose,
        user=owner,
        chat_summaries=ctx.manager.get_chat_summary_dict(),
        tools=tools,
        callbacks=[AgentToolCallbackLogger(tracer, agent_template.name)],
        checkpointer=InMemorySaver(),
    )


def get_agents_for_user(ctx: AgentCtx, owner: UserTable, tracer: Tracer) -> list[IAgent]:
    """
    This function converts the agent templates associated with the given user to a list 
    of runtime agents.
    """

    tool_factory_registry = get_tool_factory_in_mem_store()
    agent_templates = get_all_agent_template_schemas_for_user(ctx.db, owner)

    agents: list[IAgent] = [
        runtime_agent_from_agent_template(ctx, owner, tool_factory_registry, template, tracer) 
        for template in agent_templates
    ]

    return agents