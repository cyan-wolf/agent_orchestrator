"""
This module manages the sandbox environment used by the coding tools.
"""

from daytona import Daytona, DaytonaConfig, Sandbox, DaytonaError, CreateSandboxFromSnapshotParams
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
    Gets the Docker container for the given chat. Creates one if one didn't exist.
    """
    try:
        return daytona.get(f"chat-{chat_id}")
    
    except DaytonaError as ex:
        print(f"Log: {ex}")
        return create_sandbox(chat_id)


def clean_up_container_for_chat(chat_id: uuid.UUID):
    """
    Cleans up the container associated with the chat with the given ID.
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
    Executes the given command on the given container in the provided working directory.
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
