"""
This package and its subpackages define all the tools used by the agents. In the codebase, tools 
are created by factory functions with the `prepare_name_of_tool` naming scheme. These factory functions 
take an :py:class:`ai.agent_manager.agent_context.AgentCtx` agent context object. This object holds references 
to the currently executing agent manager and the :py:class:`sqlalchemy.orm.Session` DB session. 

The tools returned by the tool factory must have a documentation comment that explains that it does. This is so that 
the agent calling the tool can read to know how and when to call the tool. Code inside the tool has access to the agent 
manager and the DB session through :py:attr:`ctx.manager` and :py:attr:`ctx.db` respectively. Tools also need to be decorated 
with the :py:func:`ai.tracing.trace_decorator.trace` decorator, which is used for logging tool activity by agents. The agent context 
object must be passed to the trace decorator.

This is an example of a tool factory definition:

.. code-block:: python

    def prepare_get_current_date_tool(ctx: AgentCtx):
        \"\"\"
        Prepares a tool that returns the current date.
        \"\"\"

        @trace(ctx)
        def get_current_date():
            \"\"\"
            Returns the current (UTC) date and time in the ISO 8601 format: YYYY-MM-DD HH:MM:SS.mmmmmm.
            \"\"\"
            return str(datetime.now(tz=timezone.utc))
        
        return get_current_date

Then, the above tool factory can be used to obtain a :py:attr:`get_current_date` tool by calling the factory 
with an agent context object.

"""