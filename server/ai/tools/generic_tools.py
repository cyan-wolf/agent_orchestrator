from datetime import datetime, timezone
from ai.tracing import trace

# NOTE: Unused.
def prepare_get_current_date_tool(agent_manager):
    @trace(agent_manager)
    def get_current_date():
        """Returns the current date and time in the ISO 8601 format: YYYY-MM-DD HH:MM:SS.mmmmmm"""
        return str(datetime.now(tz=timezone.utc))
    
    return get_current_date
