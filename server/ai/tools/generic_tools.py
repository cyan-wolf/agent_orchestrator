from datetime import datetime
from ai.tracing import trace

def prepare_get_current_date_tool(agent_manager):
    @trace(agent_manager)
    def get_current_date():
        """Returns the current date and time in the ISO 8601 format: YYYY-MM-DD HH:MM:SS.mmmmmm"""
        return str(datetime.now())
    
    return get_current_date
