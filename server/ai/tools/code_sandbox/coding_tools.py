"""
This module defines coding-related tools for the coding agent.
"""

from ai.tracing.trace_decorator import trace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.code_sandbox.sandbox_management import get_sandbox, exec_command_on_sandbox, add_file_to_sandbox

from ai.tools.code_sandbox.models import RunCommandSchema

def prepare_run_command_tool(ctx: AgentCtx):
    """
    Prepares a tool that runs a given command in a secure environment.
    """

    @trace(ctx)
    def run_command(command_schema: RunCommandSchema) -> str:
        """
        Runs the given command in a Linux environment. 
        """
        sandbox = get_sandbox(ctx.manager.get_chat_id())
        if sandbox is None:
            return "Error: could not fetch sandbox environment, try again later"

        result = exec_command_on_sandbox(sandbox, command_schema.command)
        return str(result)
    
    return run_command


def prepare_create_file_tool(ctx: AgentCtx):
    """
    Prepares a tool that creates a file inside of the secure Linux environment.
    """

    @trace(ctx)
    def create_file(file_path: str, file_content: str) -> str:
        """
        Creates a file inside of the secure Linux environment.

        Note: If you cannot find the file after creating it, don't hesitate to use the 
        ls command to look for the file.
        """
        sandbox = get_sandbox(ctx.manager.get_chat_id())
        if sandbox is None:
            return "Error: could not fetch sandbox environment, try again later"

        add_file_to_sandbox(sandbox, file_path, file_content)
        return "Added file to sandbox"
    
    return create_file


