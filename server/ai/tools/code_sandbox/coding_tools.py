"""
This module defines coding-related tools for the coding agent.
"""

from ai.tracing.trace_decorator import trace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.code_sandbox.sandbox_management import get_sandbox, exec_command_on_sandbox, add_file_to_sandbox

def prepare_run_command_tool(ctx: AgentCtx):
    """
    Prepares a tool that runs a given command in a secure environment.
    """

    @trace(ctx)
    def run_command(command: str) -> tuple[int, str] | str:
        """
        Runs the given command in a secure environment. 
        
        If this tool returns an error, do not 
        re-run it. Instead stop and tell the user of the error.

        Args:
            command: The Linux command to run.

        Retuns:
            A tuple where the first element represents the exit code and the second element the output of the command.
        """

        sandbox = get_sandbox(ctx.manager.get_chat_id())
        if sandbox is None:
            return "Error: could not fetch sandbox environment"

        exit_code, output = exec_command_on_sandbox(sandbox, command)
        return exit_code, output
    
    return run_command


def prepare_create_file_tool(ctx: AgentCtx):
    """
    Prepares a tool that creates a file inside of the secure Linux environment.
    """

    @trace(ctx)
    def create_file(file_path: str, file_content: str) -> bool | str:
        """
        Creates a file inside of the secure Linux environment.

        If this tool returns an error, do not 
        re-run it. Instead stop and tell the user of the error.

        Args:
            file_path: The file path of the file.
            file_content: The content of the newly created file as a string.
        """
        sandbox = get_sandbox(ctx.manager.get_chat_id())
        if sandbox is None:
            return "Error: could not fetch sandbox environment"

        add_file_to_sandbox(sandbox, file_path, file_content)
        return "Added file to sandbox"
    
    return create_file


