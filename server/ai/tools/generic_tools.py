"""
This module is for defining tools that are equally applicable to 
all agents.
"""

from datetime import datetime, timezone
from ai.tracing.trace_decorator import trace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.registry.tool_register_decorator import register_tool_factory

@register_tool_factory(tool_id='get_current_date')
def prepare_get_current_date_tool(ctx: AgentCtx):
    """
    Prepares a tool that returns the current date in ISO format.
    """

    @trace(ctx)
    def get_current_date():
        """
        Returns the current (UTC) date and time in the ISO 8601 format: YYYY-MM-DD HH:MM:SS.mmmmmm
        """
        return str(datetime.now(tz=timezone.utc))
    
    return get_current_date

