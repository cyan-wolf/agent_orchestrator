"""
This module defines coding-related tools for the coding agent.
"""

from ai.tracing.schemas import ImageCreationTrace
from ai.tracing.trace_decorator import trace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.code_sandbox.sandbox_management import get_sandbox, exec_command_on_sandbox, add_file_to_sandbox, exec_code_on_sandbox

from ai.tools.code_sandbox.models import RunCommandSchema, RunCodeSnippetSchema

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


def prepare_run_code_snippet_tool(ctx: AgentCtx):
    """
    Prepares a tool that runs the given code snippet in a Linux environment.
    Note: When using this tool, code snippets may use numpy and matplotlib. Any 
    charts created in the snippet are automatically shown to the user.
    """

    @trace(ctx)
    def run_code_snippet_tool(run_schema: RunCodeSnippetSchema) -> str:
        """
        Runs the given code snippet in a Linux environment.
        """
        sandbox = get_sandbox(ctx.manager.get_chat_id())
        if sandbox is None:
            return "Error: could not fetch sandbox environment, try again later"
        
        exit_code, output, charts = exec_code_on_sandbox(sandbox, run_schema.source_code)

        for chart in charts:
            # The `png` attribute is nullable.
            if chart.png is None:
                continue
            _add_image_to_trace_history(ctx, chart.png, chart.title)

        return str((exit_code, output))
    
    return run_code_snippet_tool


def _add_image_to_trace_history(ctx: AgentCtx, image_base64: str, caption: str):
    # Used for showing the image to the user.
    ctx.manager.get_tracer().add(ctx.db, ImageCreationTrace(base64_encoded_image=image_base64, caption=caption))