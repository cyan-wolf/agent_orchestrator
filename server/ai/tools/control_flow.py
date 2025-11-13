"""
This module defines tools mainly used by the supervisor agent 
to switch the identity of the current agent.
"""

from typing import Literal
from ai.agent_manager.agent_context import AgentCtx
import json
from ai.tools.registry.tool_register_decorator import register_tool_factory
from ai.agent.templates.agent_templates import get_all_switchable_agent_names
from auth.auth import get_user_by_username

@register_tool_factory(tool_id='switch_to_more_qualified_agent')
def prepare_switch_to_more_qualified_agent_tool(ctx: AgentCtx):
    # Dynamically build the doc-comment for this tool since we don't know what the 
    # valid switchable agents are at build time.
    owner = get_user_by_username(ctx.db, ctx.manager.get_owner_username())

    valid_switchable_agents = get_all_switchable_agent_names(ctx.db, owner)
    switch_tool_doc_for_agent = f"""
        Switches to the given agent. A reason for the switch can optionally be passed to this tool. 
        The reason is passed on to the new agent so that it has context on what it's supposed to do.
        The agents that you can switch to are: {valid_switchable_agents}

        Note that you cannot switch into yourself.
        """

    def switch_to_more_qualified_agent(agent_name: str, reason: str | None) -> str:
        
        if agent_name in valid_switchable_agents:
            ctx.manager.queue_agent_handoff(
                agent_name_prev=ctx.manager.get_agent_dict()["main_agent"].get_name(), 
                agent_name_new=agent_name, 
                handoff_reason=str(reason),
            )
            return f"switched to {agent_name}!"
        
        else:
            return f"unknown agent name '{agent_name}'"
        
    # Modify the doc-comment for the tool, this is important for the agent so that it knows 
    # how to call the tool.
    switch_to_more_qualified_agent.__doc__ = switch_tool_doc_for_agent
        
    return switch_to_more_qualified_agent


@register_tool_factory(tool_id='check_helper_agent_chat_summaries')
def prepare_check_helper_agent_summaries_tool(ctx: AgentCtx):
    def check_helper_agent_chat_summaries():
        """
        Used for checking what the helper agents have talked about with the user.
        """
        return json.dumps(ctx.manager.get_chat_summary_dict())
    
    return check_helper_agent_chat_summaries


@register_tool_factory(tool_id='summarize_chat')
def prepare_summarization_tool(ctx: AgentCtx):
    """
    Prepares a tool that stores a summary of the current current agent's chat with the user.
    """

    def summarize_chat(chat_summary: str):
        """
        Stores a summary of the current chat.
        """
        ctx.manager.set_chat_summary_for_current(ctx.db, chat_summary)

        return "Successfully summarized chat."

    return summarize_chat


@register_tool_factory(tool_id='switch_back_to_supervisor')
def prepare_switch_back_to_supervisor_tool(ctx: AgentCtx):
    """
    Prepares a tool that switches the current agent back to the supervisor.
    """

    def switch_back_to_supervisor(reason: str | None):
        """
        Switches back to the supervisor agent. 
        The reason is passed on to the supervisor agent so that it has context on why the switch happened.
        """
        _run_agent_specific_cleanup(ctx)

        ctx.manager.queue_agent_handoff(
            agent_name_prev=ctx.manager.get_agent_dict()["main_agent"].get_name(),
            agent_name_new="supervisor_agent",
            handoff_reason=str(reason),
        )
        return "switched back to supervisor"
    
    return switch_back_to_supervisor


def _run_agent_specific_cleanup(ctx: AgentCtx):
    from ai.tools.code_sandbox.sandbox_management import clean_up_sandbox_for_chat

    if ctx.manager.get_agent_dict()["main_agent"].get_name() == "coding_agent":
        # Clean up container for current chat when the coding agent runs cleanup.
        clean_up_sandbox_for_chat(ctx.manager.get_chat_id())