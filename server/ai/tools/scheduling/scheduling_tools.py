from datetime import datetime, timezone
from ai.tracing import trace
from ai.tools.scheduling.models import Event, Importance, EventModification
from db.placeholder_db import get_db  


def _add_utc_timezone_to_event(event: Event):
    """
    Modifies the given event such that its start and end times are 
    proper datetimes (i.e. not naive) by adding UTC as their timezone.
    """
    event.start_time = event.start_time.replace(tzinfo=timezone.utc)
    event.end_time = event.end_time.replace(tzinfo=timezone.utc)


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
            start_time=start_time, 
            end_time=end_time, 
            importance=importance)
        _add_utc_timezone_to_event(event)

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
    def modify_event(event_modification: EventModification):
        """
        Modifies an existing event on the schedule. Uses the given EventModification object to 
        edit the event. Modifies the existing event with the same event ID as 
        the modification object. The rest of the fields of the modification object are used to modify the event.
        If a field is None, then that field is not modified. If a field is not None, the value it has is used to 
        modify the corresponding field on the existing event.
        """

        schedule = get_or_init_schedule_from_user(agent_manager.owner_username)
        
        if len(schedule) == 0:
            return "no events to modify"
        
        for i in range(len(schedule)):
            if schedule[i].id == event_modification.event_id:
                
                if event_modification.new_name is not None:
                    schedule[i].name = event_modification.new_name

                if event_modification.new_start_time is not None:
                    schedule[i].start_time = event_modification.new_start_time

                if event_modification.new_end_time is not None:
                    schedule[i].end_time = event_modification.new_end_time

                if event_modification.new_importance is not None:
                    schedule[i].importance = event_modification.new_importance

                _add_utc_timezone_to_event(schedule[i])

                get_db().store_schedules_db()
                return f"successfully modified event"
        
        return f"event with id {event_modification.event_id} was not present"
    
    return modify_event