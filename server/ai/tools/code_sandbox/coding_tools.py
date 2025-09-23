from ai.tracing.trace_decorator import trace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.code_sandbox.sandbox_management import get_container, exec_command_on_container, add_file_to_container

def prepare_run_command_tool(ctx: AgentCtx):
    @trace(ctx)
    def run_command(command: str) -> tuple[int, str]:
        """
        Runs the given command in a secure environment.

        Args:
            command: The Linux command to run.

        Retuns:
            A tuple where the first element represents the exit code and the second element the output of the command.
        """

        container = get_container(str(ctx.manager.get_chat_id()))
        exit_code, output = exec_command_on_container(container, command)
        return exit_code, output
    
    return run_command


def prepare_create_file_tool(ctx: AgentCtx):
    @trace(ctx)
    def create_file(file_path: str, file_content: str) -> bool:
        """
        Creates a file inside of the secure Linux environment.

        Args:
            file_path: The file path of the file.
            file_content: The content of the newly created file as a string.

        Returns:
            bool: True if the operation succeeded.
        """
        container = get_container(str(ctx.manager.get_chat_id()))
        succeeded = add_file_to_container(container, file_path, file_content)
        return succeeded
    
    return create_file


