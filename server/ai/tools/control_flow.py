from ai.tracing.trace_decorator import trace
from typing import Literal
from ai.agent_manager.agent_context import AgentCtx

SwitchableAgent = Literal["coding_agent", "creator_agent", "planner_agent", "math_agent"]
VALID_SWITCHABLE_AGENT = {"coding_agent", "creator_agent", "planner_agent", "math_agent"}

def prepare_supervisor_agent_tools(ctx: AgentCtx, extra_tools: list):
    @trace(ctx)
    def switch_to_more_qualified_agent(agent_name: SwitchableAgent, reason: str | None) -> str:
        """
        Switches to the given agent. A reason for the switch can optionally be passed to this tool. 
        The reason is passed on to the new agent so that it has context on what it's supposed to do.
        """
        if agent_name in VALID_SWITCHABLE_AGENT:
            # Switch the 'main_agent' (i.e. the agent actually in control).
            ctx.manager.get_agent_dict()["main_agent"] = ctx.manager.get_agent_dict()[agent_name]

            # Tell the new 'main_agent' what it's supposed to do.
            ctx.manager.invoke_agent(
                ctx.manager.get_agent_dict()["main_agent"], 
                f"The supervisor agent handed off the user to you! Do your best. This was its reason: {reason}",
                ctx.db,
            )

            return f"switched to {agent_name}!"
        
        else:
            return f"unknown agent name '{agent_name}'"
        
    @trace(ctx)
    def check_helper_agent_chat_summaries():
        """
        Used for checking what the helper agents have talked about with the user.
        """
        return str(ctx.manager.get_chat_summary_dict())

    
    
    return [
        switch_to_more_qualified_agent, 
        check_helper_agent_chat_summaries,
        prepare_summarization_tool(ctx),
    ] + extra_tools


def run_agent_specific_cleanup(ctx: AgentCtx):
    from ai.tools.code_sandbox.sandbox_management import clean_up_container_for_chat

    if ctx.manager.get_agent_dict()["main_agent"].name == "coding_agent":
        # Clean up container for current chat when the coding agent runs cleanup.
        clean_up_container_for_chat(str(ctx.manager.get_chat_id()))


def prepare_summarization_tool(ctx: AgentCtx):
    @trace(ctx)
    def summarize_chat(chat_summary: str):
        """
        Stores a summary of the current chat.
        """
        ctx.manager.set_chat_summary_for_current(ctx.db, chat_summary)

        return "Successfully summarized chat."

    return summarize_chat


def prepare_switch_back_to_supervisor_tool(ctx: AgentCtx):
    @trace(ctx)
    def switch_back_to_supervisor():
        """
        Switches back to the supervisor. 
        """
        run_agent_specific_cleanup(ctx)

        ctx.manager.get_agent_dict()["main_agent"] = ctx.manager.get_agent_dict()["supervisor_agent"]
        return "switched back to supervisor"
    
    return switch_back_to_supervisor
