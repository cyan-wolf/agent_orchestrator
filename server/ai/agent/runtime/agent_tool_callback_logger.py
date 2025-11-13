from typing import Any
from uuid import UUID
from langchain.callbacks.base import BaseCallbackHandler

from ai.tracing.schemas import ToolTrace
from ai.tracing.tracer import Tracer

from dataclasses import dataclass

@dataclass
class AgentToolCallStart:
    name: str
    description: str
    call_args: dict[str, Any]


class AgentToolCallbackLogger(BaseCallbackHandler):
    def __init__(self, tracer: Tracer, agent_name: str):
        self.tracer = tracer
        self.agent_name = agent_name
        self.pending_tool_args: dict[UUID, AgentToolCallStart] = {}


    def on_tool_start(
        self, 
        serialized: dict[str, Any], 
        input_str: str, 
        *, 
        run_id: UUID, 
        parent_run_id: UUID | None = None, 
        tags: list[str] | None = None, 
        metadata: dict[str, Any] | None = None, 
        inputs: dict[str, Any] | None = None, 
        **kwargs: Any,
    ) -> Any:
        self.pending_tool_args[run_id] = AgentToolCallStart(
            name=serialized['name'],
            description=serialized['description'],
            call_args=inputs or {},
        )

        return super().on_tool_start(serialized, input_str, run_id=run_id, parent_run_id=parent_run_id, tags=tags, metadata=metadata, inputs=inputs, **kwargs)

    
    def on_tool_end(self, output: Any, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        if run_id in self.pending_tool_args:
            tool_call_start = self.pending_tool_args.pop(run_id)
            ret = str(output.content)

            # We don't have access to a DB session so we add the tool trace as pending.
            # They are committed to the DB by the agent manager which does have a DB session.
            self.tracer.add_pending(ToolTrace(
                called_by=self.agent_name,
                name=tool_call_start.name,
                bound_arguments=tool_call_start.call_args,
                return_value=ret,
            ))
            
        else:
            print(f"LOG: unknown tool run ID '{run_id}'")

        return super().on_tool_end(output, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
    

    def on_tool_error(self, error: BaseException, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        if run_id in self.pending_tool_args:
            tool_call_start = self.pending_tool_args.pop(run_id)

            # NOTE: do not show the error to the user, it might contain sensitive info like API keys
            print(f"TOOL CALL ERROR: CALLARGS{tool_call_start.call_args}, NAME({tool_call_start.name}), ERROR({error})")
            
        else:
            print(f"LOG: unknown tool run ID '{run_id}'")

        return super().on_tool_error(error, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
