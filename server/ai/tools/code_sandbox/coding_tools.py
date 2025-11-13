"""
This module defines coding-related tools for the coding agent.
"""

from ai.tracing.schemas import ImageCreationTrace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.code_sandbox.sandbox_management import get_sandbox, exec_command_on_sandbox, add_file_to_sandbox, exec_code_on_sandbox

from ai.tools.code_sandbox.models import RunCommandSchema, RunCodeSnippetSchema

from ai.tools.registry.tool_register_decorator import register_tool_factory


@register_tool_factory(tool_id='run_command')
def prepare_run_command_tool(ctx: AgentCtx):
    """
    Prepares a tool that runs a given command in a secure environment.
    """

    def run_command(command_schema: RunCommandSchema) -> str:
        """
        Runs the given command in a Linux environment. 

        Note: The Linux environment has a few caveats to consider:

        - You have access to a user with `sudo` permissions. 
        You can run privileged commands by prepending them with sudo, no password needed.
        
        -The environment's package lists may be outdated. Running `sudo apt update` helps. 
        
        -The user cannot interact with the environment directly. if you run a command that needs STDIN you should 
        write a file and pipe it in to the command since the user cannot directly input to the environment's STDIN. 
        For installation/setup commands for `apt`, you can pass the -y flag to avoid the issue of the user not being 
        able to access STDIN. 
        
        -The environment doesn't have open network access it only allows it for a few things such as the `apt` manager. 
        
        -You can install additional tools as long as they're in the environment's package manager. For example, you 
        can install Rust with `sudo apt install cargo -y` and COBOL with `sudo apt install gnucobol -y`. 
        """
        sandbox = get_sandbox(ctx.manager.get_chat_id())
        if sandbox is None:
            return "Error: could not fetch sandbox environment, try again later"

        result = exec_command_on_sandbox(sandbox, command_schema.command)
        return str(result)
    
    return run_command


@register_tool_factory(tool_id='create_file')
def prepare_create_file_tool(ctx: AgentCtx):
    """
    Prepares a tool that creates a file inside of the secure Linux environment.
    """

    def create_file(file_path: str, file_content: str) -> str:
        """
        Creates a file inside of the secure Linux environment.

        Note: 
        - If you cannot find the file after creating it, don't hesitate to use the 
        ls command to look for the file.

        - Files can only be created under the `/tmp/` directory.
        """
        sandbox = get_sandbox(ctx.manager.get_chat_id())
        if sandbox is None:
            return "Error: could not fetch sandbox environment, try again later"

        add_file_to_sandbox(sandbox, file_path, file_content)
        return "Added file to sandbox"
    
    return create_file


@register_tool_factory(tool_id='run_code_snippet_tool')
def prepare_run_code_snippet_tool(ctx: AgentCtx):
    """
    Prepares a tool that runs the given code snippet in a Linux environment.
    Note: When using this tool, code snippets may use numpy and matplotlib. Any 
    charts created in the snippet are automatically shown to the user.
    """

    def run_code_snippet_tool(run_schema: RunCodeSnippetSchema) -> str:
        """
        Runs the given Python code snippet in a Linux environment.

        Note: When using this tool, code snippets may use numpy and matplotlib. Any 
        charts 'shown' (i.e. with plt.show()) in the snippet are automatically shown to the user.
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