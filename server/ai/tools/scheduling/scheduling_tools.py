from ai.tracing import trace
from ai.tools.scheduling.models import Event, Importance  
from datetime import datetime

class Schedule:
    def __init__(self):
        # event ID -> Event
        self.events: dict[str, Event] = {}

    def get_all_events(self) -> list[Event]:
        return list(self.events.values())
    
    def get_event_by_id(self, event_id: str) -> Event | None:
        return self.events.get(event_id)
    
    def add_event(self, event: Event):
        self.events[event.id] = event

    def remove_event(self, event_id: str):
        if event_id in self.events:
            del self.events[event_id]
            return f"successfully deleted event with ID {event_id}"
        else:
            return f"event with ID {event_id} does not exist"


# chat ID -> schedule
SCHEDULE_TEMP_DB: dict[str, Schedule] = {}

def get_or_init_schedule_from_chat(chat_id: str) -> Schedule:
    schedule = SCHEDULE_TEMP_DB.get(chat_id)

    if schedule is None:
        schedule = Schedule()
        SCHEDULE_TEMP_DB[chat_id] = schedule

    return schedule


def prepare_view_schedule_tool(agent_manager):
    @trace(agent_manager)
    def view_schedule() -> list[Event]:
        """
        Returns a list of events on the schedule.
        """
        schedule = get_or_init_schedule_from_chat(agent_manager.chat_id)
        return schedule.get_all_events()

    return view_schedule

def prepare_add_new_event_tool(agent_manager):
    @trace(agent_manager)
    def add_new_event(event_name: str, start_time: datetime, end_time: datetime, importance: Importance):
        """
        Adds a new event to the schedule. Note that the start_time and end_time parameters are 
        Python datetime objects. Please convert from the user's timezone to UTC and work with start and endtimes in UTC. 
        Of course, refer to them in the user's timezone when communicating with them as to not confuse them, but the tool works with UTC only.
        """
        event = Event(name=event_name, start_time=start_time, end_time=end_time, importance=importance)

        schedule = get_or_init_schedule_from_chat(agent_manager.chat_id)
        schedule.add_event(event)

        return "successfully added event"
    
    return add_new_event

def prepare_delete_event_tool(agent_manager):
    @trace(agent_manager)
    def remove_event_with_id(event_id: str) -> str:
        """
        Removes the event with the given ID from the schedule.
        """
        schedule = get_or_init_schedule_from_chat(agent_manager.chat_id)
        result_message = schedule.remove_event(event_id)
        return result_message
    
    return remove_event_with_id

def prepare_modify_event_tool(agent_manager):
    @trace(agent_manager)
    def modify_event(event_id: str):
        """
        Modifies an event on the schedule.
        """
        return "TODO: not implemented yet"
    
    return modify_event