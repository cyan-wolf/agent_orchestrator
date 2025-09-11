from datetime import datetime, timezone
from ai.tracing.trace_decorator import trace
from ai.agent_manager.agent_context import AgentCtx
from user_settings import user_settings

def prepare_get_current_date_tool(ctx: AgentCtx):
    @trace(ctx)
    def get_current_date():
        """
        Returns the current (UTC) date and time in the ISO 8601 format: YYYY-MM-DD HH:MM:SS.mmmmmm
        """
        return str(datetime.now(tz=timezone.utc))
    
    return get_current_date

