from datetime import datetime, timezone
from ai.tracing import trace
from ai.agent_context import AgentContext
from user_settings import user_settings

def prepare_get_current_date_tool(agent_manager: AgentContext):
    @trace(agent_manager)
    def get_current_date():
        """
        Returns the current (UTC) date and time in the ISO 8601 format: YYYY-MM-DD HH:MM:SS.mmmmmm
        """
        return str(datetime.now(tz=timezone.utc))
    
    return get_current_date


def prepare_get_user_timezone_tool(agent_manager: AgentContext):
    @trace(agent_manager)
    def get_user_timezone() -> tuple[str, float]:
        """
        Returns a tuple of timezone data. The first element contains the 
        user's provided timezone as an IANA string. The second element contains the 
        computed UTC offset as a floating point number. For example, if the offset is 4.0
        then the user's timezone is UTC+4. If the offset is -4.0, then the offset is UTC-4. 
        """
        username = agent_manager.get_owner_username()
        timezone_string = user_settings.get_timezone_string(username)
        timezone_offset = user_settings.get_timezone_offset(username)

        return (timezone_string, timezone_offset)
    
    return get_user_timezone


def prepare_get_user_location_tool(agent_manager: AgentContext):
    @trace(agent_manager)
    def get_user_provided_location() -> tuple[str, str]:
        """
        Returns the user's provided location as a tuple of strings. The first element 
        is the user-provided city and the second element is the user-provided country.
        """
        username = agent_manager.get_owner_username()
        city = user_settings.get_city(username)
        country = user_settings.get_country(username)

        return (city, country)
    
    return get_user_provided_location
