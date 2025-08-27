from datetime import datetime, timezone
from ai.tracing import trace
from ai.tools.scheduling.models import Event, Importance
from db.placeholder_db import get_db  


def get_or_init_schedule_from_user(username: str) -> list[Event]:
    db = get_db().schedules_db.schedules

    schedule = db.get(username)

    if schedule is None:
        schedule = []
        db[username] = schedule
        get_db().store_schedules_db()

    return schedule


def prepare_view_schedule_tool(agent_manager):
    @trace(agent_manager)
    def view_schedule() -> list[Event]:
        """
        Returns a list of events on the schedule.
        """
        return get_or_init_schedule_from_user(agent_manager.owner_username)

    return view_schedule


def prepare_add_new_event_tool(agent_manager):
    @trace(agent_manager)
    def add_new_event(event_name: str, start_time: datetime, end_time: datetime, importance: Importance):
        """
        Adds a new event to the schedule. Note that the start_time and end_time parameters are 
        Python datetime objects. Please convert from the user's timezone to UTC and work with start and endtimes in UTC. 
        Of course, refer to them in the user's timezone when communicating with them as to not confuse them, but the tool works with UTC only.
        """
        event = Event(
            name=event_name, 
            start_time=start_time.replace(tzinfo=timezone.utc), 
            end_time=end_time.replace(tzinfo=timezone.utc), 
            importance=importance)

        schedule = get_or_init_schedule_from_user(agent_manager.owner_username)
        schedule.append(event)
        get_db().store_schedules_db()

        return "successfully added event"
    
    return add_new_event

def prepare_delete_event_tool(agent_manager):
    @trace(agent_manager)
    def remove_event_with_id(event_id: str) -> str:
        """
        Removes the event with the given ID from the schedule.
        """
        schedule = get_or_init_schedule_from_user(agent_manager.owner_username)
        
        if len(schedule) == 0:
            return "no events to delete"
        
        for i in range(len(schedule)):
            if schedule[i].id == event_id:
                del schedule[i]
                get_db().store_schedules_db()
                return f"successfully deleted event"
            
        return f"event with id {event_id} was not present"
    
    return remove_event_with_id

def prepare_modify_event_tool(agent_manager):
    @trace(agent_manager)
    def modify_event(event_id: str):
        """
        Modifies an event on the schedule.
        """
        return "TODO: not implemented yet"
    
    return modify_event