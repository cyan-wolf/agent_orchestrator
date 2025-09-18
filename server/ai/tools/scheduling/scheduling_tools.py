from datetime import datetime, timezone
from ai.tracing.trace_decorator import trace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.scheduling.tables import EventTable
from ai.tools.scheduling.schemas import CreateEvent, EventBase, Event, EventModification
import uuid
from sqlalchemy.orm import Session
from auth.auth import get_user_by_username

def _add_utc_timezone_to_event(event: EventBase):
    """
    Modifies the given event such that its start and end times are 
    proper datetimes (i.e. not naive) by adding UTC as their timezone.
    """
    event.start_time = event.start_time.replace(tzinfo=timezone.utc)
    event.end_time = event.end_time.replace(tzinfo=timezone.utc)


def _event_from_db_to_schema(event: EventTable) -> Event:
    return Event(
        id=event.id,
        name=event.name,
        start_time=datetime.fromtimestamp(event.start_time),
        end_time=datetime.fromtimestamp(event.end_time),
        importance=event.importance, # type: ignore # assume that the importance from the DB is valid
    )


# NOTE: Creates an event without an ID. The ID is auto-generated.
def _event_from_schema_to_db(event: EventBase, user_id: uuid.UUID) -> EventTable:
    return EventTable(
        name=event.name,
        start_time=int(event.start_time.timestamp()),
        end_time=int(event.end_time.timestamp()),
        importance=event.importance,
        user_id=user_id,
    )


def get_all_user_events(db: Session, username: str) -> list[EventTable]:
    user = get_user_by_username(db, username)
    assert user
    return user.events


def add_new_event_in_db(db: Session, user_id: uuid.UUID, create_event: CreateEvent):
    event = _event_from_schema_to_db(create_event, user_id)
    db.add(event)
    db.commit()


def prepare_view_schedule_tool(ctx: AgentCtx):
    @trace(ctx)
    def view_schedule() -> list[Event]:
        """
        Returns a list of events on the schedule.
        """
        return list(map(_event_from_db_to_schema, get_all_user_events(ctx.db, ctx.manager.get_owner_username())))
    
    return view_schedule


def prepare_add_new_event_tool(ctx: AgentCtx):
    @trace(ctx)
    def add_new_event(event_creation: CreateEvent):
        """
        Adds a new event to the schedule. Note that the start_time and end_time parameters are 
        Python datetime objects. Please convert from the user's timezone to UTC and work with start and endtimes in UTC. 
        Of course, refer to them in the user's timezone when communicating with them as to not confuse them, but the tool works with UTC only.
        """
        _add_utc_timezone_to_event(event_creation)

        add_new_event_in_db(ctx.db, ctx.manager.get_owner_user_id(), event_creation)

        return "successfully added event"
    
    return add_new_event


def prepare_delete_event_tool(ctx: AgentCtx):
    @trace(ctx)
    def remove_event_with_id(event_id: uuid.UUID) -> str:
        """
        Removes the event with the given ID from the schedule.
        """
        event = ctx.db.get(EventTable, event_id)

        if event is not None:
            ctx.db.delete(event)
            ctx.db.commit()
            return f"successfully deleted event"

        else:
            return f"event with id {event_id} was not present"

    
    return remove_event_with_id


def prepare_modify_event_tool(ctx: AgentCtx):
    @trace(ctx)
    def modify_event(event_modification: EventModification):
        """
        Modifies an existing event on the schedule. Uses the given EventModification object to 
        edit the event. Modifies the existing event with the same event ID as 
        the modification object. The rest of the fields of the modification object are used to modify the event.
        If a field is None, then that field is not modified. If a field is not None, the value it has is used to 
        modify the corresponding field on the existing event.
        """

        event = ctx.db.get(EventTable, event_modification.event_id)

        if event is not None:

            if event_modification.new_name is not None:
                event.name = event_modification.new_name

            if event_modification.new_start_time is not None:
                event.start_time = int(event_modification.new_start_time.replace(tzinfo=timezone.utc).timestamp())

            if event_modification.new_end_time is not None:
                event.end_time = int(event_modification.new_end_time.replace(tzinfo=timezone.utc).timestamp())

            if event_modification.new_importance is not None:
                event.importance = event_modification.new_importance

            # Save the changes.
            ctx.db.commit()

            return "Successfully modified the event"
        
        else:
            return f"event with id {event_modification.event_id} was not present"
        
    
    return modify_event