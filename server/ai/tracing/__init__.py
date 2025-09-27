"""
This package defines the different traces along with the :py:func:`ai.tracing.trace_decorator.trace` decorator which is 
central to the tool logging aspect of the application. In the application, there are four types of traces: 

- AI Messages: :py:class:`ai.tracing.schemas.AIMessageTrace`
- Human Messages: :py:class:`ai.tracing.schemas.HumanMessageTrace`
- Tool Call Logs: :py:class:`ai.tracing.schemas.ToolTrace`
- Image Creation Logs: :py:class:`ai.tracing.schemas.ImageCreationTrace`

This package defines the schemas for the different traces for interopability with the client, along with 
ORM tables for storing them in the database. 

All traces are logged to the :py:class:`ai.tracing.tracer.Tracer` tracer object. This object accepts trace schemas and 
translates them into the ORM table format to store them in the DB. Agent managers hold a reference to the tracer object 
and can be acquired through the use of the :py:meth:`ai.agent_manager.agent_manager_interface.IAgentManager.get_tracer` method. 
Tracer objects represent the chat / log history of a chat and hence provide methods for accessing the history as a sequence of 
trace schemas through the :py:meth:`ai.tracing.tracer.Tracer.get_history` and :py:meth:`ai.tracing.tracer.Tracer.get_traces_after_timestamp` methods.
"""