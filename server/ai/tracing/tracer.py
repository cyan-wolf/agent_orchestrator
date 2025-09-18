from typing import Sequence
import uuid

from sqlalchemy import select
from ai.tracing.schemas import Trace, AIMessageTrace, HumanMessageTrace, ToolTrace, ImageCreationTrace
from ai.tracing.tables import TraceTable, AIMessageTraceTable, HumanMessageTraceTable, ToolTraceTable, ImageCreationTraceTable
from sqlalchemy.orm import Session
import json
from pydantic import BaseModel
from datetime import datetime

def custom_json_fallback_serializer(obj: object) -> object:
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    
    elif isinstance(obj, datetime):
        return obj.isoformat()

    else:
        # Unkwown object, serialize as the string representation.
        return str(obj)


def trace_table_to_schema(trace_table: TraceTable) -> Trace:
    if trace_table.kind == 'ai_message':
        return AIMessageTrace(
            id=trace_table.id,
            timestamp=trace_table.timestamp,

            agent_name=trace_table.agent_name,
            content=trace_table.content,
            is_main_agent=trace_table.is_main_agent,
        )

    elif trace_table.kind == 'human_message':
        return HumanMessageTrace(
            id=trace_table.id,
            timestamp=trace_table.timestamp,

            username=trace_table.username,
            content=trace_table.content,
        )

    elif trace_table.kind == 'tool':
        return ToolTrace(
            id=trace_table.id,
            timestamp=trace_table.timestamp,

            called_by=trace_table.called_by,
            bound_arguments=json.loads(trace_table.bound_arguments),
            name=trace_table.name,
            return_value=trace_table.return_value,
        )

    elif trace_table.kind == 'image':
        return ImageCreationTrace(
            id=trace_table.id,
            timestamp=trace_table.timestamp,

            base64_encoded_image=trace_table.base64_encoded_image,
            caption=trace_table.caption,
        )

    else:
        err_msg = f"unknown trace kind '{trace_table.kind}'"
        raise ValueError(err_msg)


def trace_schema_to_table(trace_schema: Trace) -> TraceTable:
    if trace_schema.kind == 'ai_message':
        return AIMessageTraceTable(
            id=trace_schema.id,
            timestamp=trace_schema.timestamp,

            agent_name=trace_schema.agent_name,
            content=trace_schema.content,
            is_main_agent=trace_schema.is_main_agent,
        )

    elif trace_schema.kind == 'human_message':
        return HumanMessageTraceTable(
            id=trace_schema.id,
            timestamp=trace_schema.timestamp,

            username=trace_schema.username,
            content=trace_schema.content,
        )

    elif trace_schema.kind == 'tool':
        return ToolTraceTable(
            id=trace_schema.id,
            timestamp=trace_schema.timestamp,

            called_by=trace_schema.called_by,
            bound_arguments=json.dumps(trace_schema.bound_arguments, default=custom_json_fallback_serializer),
            name=trace_schema.name,
            return_value=trace_schema.return_value,
        )

    elif trace_schema.kind == 'image':
        return ImageCreationTraceTable(
            id=trace_schema.id,
            timestamp=trace_schema.timestamp,

            base64_encoded_image=trace_schema.base64_encoded_image,
            caption=trace_schema.caption,
        )

    else:
        err_msg = f"unknown trace kind '{trace_schema.kind}'"
        raise ValueError(err_msg)


class Tracer:
    def __init__(self, chat_id: uuid.UUID):
        self.chat_id = chat_id


    def add(self, db: Session, trace: Trace):
        trace_for_db = trace_schema_to_table(trace)
        trace_for_db.chat_id = self.chat_id

        db.add(trace_for_db)
        db.commit()


    def get_history(self, db: Session) -> Sequence[Trace]:
        stmt = select(TraceTable).filter(TraceTable.chat_id == self.chat_id).order_by(TraceTable.timestamp)
        results = db.execute(stmt).scalars().all()
        schemas = [trace_table_to_schema(tr) for tr in results]

        return schemas
    

    def get_traces_after_timestamp(self, db: Session, timestamp: float) -> Sequence[Trace]:
        stmt = select(TraceTable).filter(TraceTable.chat_id == self.chat_id, TraceTable.timestamp > timestamp).order_by(TraceTable.timestamp)
        results = db.execute(stmt).scalars().all()
        schemas = [trace_table_to_schema(tr) for tr in results]

        return schemas