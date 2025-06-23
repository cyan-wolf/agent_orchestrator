from datetime import datetime
from ai.tracing import trace

def prepare_get_current_date_tool(agent_manager):
    @trace(agent_manager.tracer)
    def get_current_date():
        """Returns the current date and time as a Python datetime object."""
        return datetime.now()
    
    return get_current_date
