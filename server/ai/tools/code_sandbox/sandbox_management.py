"""
This module manages the sandbox environment used by the coding tools.
"""

from daytona import Daytona, DaytonaConfig, Sandbox, DaytonaError, CreateSandboxFromSnapshotParams
from daytona.common.charts import Chart
from daytona_api_client.models.sandbox_state import SandboxState
import shlex
import uuid

# Define the configuration.
config = DaytonaConfig()

# Initialize the Daytona client.
daytona = Daytona(config)

def create_sandbox(chat_id: uuid.UUID) -> Sandbox | None:
    try:
        params = CreateSandboxFromSnapshotParams(
            name=f"chat-{chat_id}"
        )
        return daytona.create(params)
    
    except DaytonaError as ex:
        print(f"Error: {ex}")
        return None


def get_sandbox(chat_id: uuid.UUID) -> Sandbox | None:
    """
    Gets the sandbox for the given chat. Creates one if one didn't exist.
    Returns `None` if a sandbox could not be fetched and could not be created.
    """
    try:
        sandbox = daytona.get(f"chat-{chat_id}")

        # Start the sandbox if it stopped.
        if sandbox.state == SandboxState.STOPPED:
            sandbox.start()

        return sandbox
    
    except DaytonaError as ex:
        print(f"Log: {ex}")
        return create_sandbox(chat_id)


def clean_up_sandbox_for_chat(chat_id: uuid.UUID):
    """
    Cleans up the sandbox associated with the chat with the given ID.
    """
    sandbox = get_sandbox(chat_id)
    
    if sandbox is None:
        return
    
    try: 
        daytona.delete(sandbox)

    except DaytonaError as ex:
        print(f"Error: {ex}")


def exec_command_on_sandbox(sandbox: Sandbox, command: str, workdir='/') -> tuple[int, str]:
    """
    Executes the given command on the given sandbox in the provided working directory.
    """
    shell_safe_command = shlex.quote(command)

    response = sandbox.process.exec(f"sh -c {shell_safe_command}", cwd=workdir) 

    return int(response.exit_code), response.result


def add_file_to_sandbox(
    sandbox: Sandbox, 
    file_path: str, 
    content: str, 
):   
    sandbox.fs.upload_file(content.encode(), file_path)


def exec_code_on_sandbox(sandbox: Sandbox, code: str) -> tuple[int, str, list[Chart]]:
    """
    Executes the given command on the given sandbox in the provided working directory.
    """
    response = sandbox.process.code_run(code)

    charts = []
    if response.artifacts is not None and response.artifacts.charts is not None:
        for chart in response.artifacts.charts:
            charts.append(chart)

    return int(response.exit_code), response.result, charts