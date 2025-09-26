"""
This module manages the sandbox environment used by the coding tools.
"""

import docker
import docker.errors
from docker.models.containers import Container

import time
import shlex
import io
import tarfile
import os

# chat ID -> Container
# Using a separate global dictionary to keep track of the containers may be 
# unnecessary. The Docker SDK already keeps track of the containers.
SANDBOX_RUNTIME_DB: dict[str, Container] = {}


def get_container(chat_id: str) -> Container:
    """
    Gets the Docker container for the given chat. Creates one if one didn't exist.
    """
    if chat_id in SANDBOX_RUNTIME_DB:
        return SANDBOX_RUNTIME_DB[chat_id]
    else:
        container = _create_simple_python_container(f"agent-orchestrator-chat-python-{chat_id}")

        if container:
            SANDBOX_RUNTIME_DB[chat_id] = container
            return container
        else:
            raise Exception(f"Error: could not create Docker image for chat {chat_id}")


def _create_simple_python_container(container_name: str):
    """
    Creates and runs a Docker container using the python:3.12-slim image.

    Args:
        container_name (str): The desired name for the Docker container.

    Returns:
        docker.models.containers.Container: The Container object if successful, None otherwise.
    """
    try:
        # Connect to the Docker daemon
        # On Windows, this will automatically try to connect via the named pipe.
        docker_image = docker.from_env()
        print("LOG: Successfully connected to Docker daemon.")

        # Define the image to use
        image_name = "python:3.12-slim"

        # Handle existing container with the same name.
        # This makes the function idempotent (running it multiple times
        # won't create multiple containers with the same name).
        try:
            existing_container = docker_image.containers.get(container_name)
            print(f"LOG: Container '{container_name}' already exists. Stopping and removing it...")
            if existing_container.status == 'running':
                existing_container.stop()
            existing_container.remove()
            print(f"LOG: Existing container '{container_name}' removed.")
        except docker.errors.NotFound:
            print(f"LOG: No existing container named '{container_name}' found. Proceeding to create.")
        except Exception as e:
            print(f"LOG: Error handling existing container '{container_name}': {e}")
            # If we can't clean up, we should ideally not proceed to avoid conflicts.
            return None

        print(f"LOG: Creating and starting container '{container_name}' from image '{image_name}'...")

        # Create and run the container
        # - image: The Docker image to use.
        # - name: Assigns a human-readable name to the container.
        # - detach=True: Runs the container in the background (daemon mode).
        # - tty=True: Allocates a pseudo-TTY. This is often crucial for
        #             keeping minimalist containers like python:slim alive
        #             when no specific long-running command is given,
        #             allowing your agent to execute commands into it later.
        container = docker_image.containers.run(
            image=image_name,
            name=container_name,
            detach=True,
            tty=True,
            # No 'command' specified here. The 'python:3.12-slim' image's
            # default CMD (often just 'python' or '/bin/bash') combined with
            # 'tty=True' will keep it running.
        )

        print(f"LOG: Container '{container_name}' (ID: {container.id}) created and started successfully.")
        
        # Give the container a brief moment to fully initialize
        time.sleep(1) 
        
        return container

    except docker.errors.ImageNotFound:
        print(f"LOG: Error: Image '{image_name}' not found locally. Attempting to pull it from Docker Hub...")
        try:
            docker_image.images.pull(image_name)
            print(f"LOG: Image '{image_name}' pulled successfully. Retrying container creation...")
            # Recursively call (may be a bad idea) the function now that the image is pulled.
            return _create_simple_python_container(container_name)
        except Exception as pull_error:
            print(f"LOG: Failed to pull image '{image_name}': {pull_error}")
            return None
    except docker.errors.APIError as e:
        print(f"LOG: Error communicating with Docker daemon (API error): {e}")
        print("LOG: Ensure Docker Desktop is running and configured correctly.")
        return None
    except Exception as e:
        print(f"LOG: An unexpected error occurred: {e}")
        return None


def clean_up_container_for_chat(chat_id: str):
    """
    Cleans up the container associated with the chat with the given ID.
    """
    container = SANDBOX_RUNTIME_DB.get(chat_id)

    if container is None:
        # Do nothing, there was no container.
        return

    # Remove the container from the runtime DB.
    del SANDBOX_RUNTIME_DB[chat_id]

    _clean_up_container(container)
    

def _clean_up_container(container: Container):
    """
    Cleans up the container directly. Using `clean_up_container_for_chat` is preferred.
    """
    print(f"LOG: \n--- Stopping and removing the container '{container.name}' ---")
    try:
        container.stop()
        container.remove()

        print(f"LOG: Container '{container.name}' stopped and removed.")

    except Exception as e:
        print(f"LOG: Error stopping/removing container: {e}")


def exec_command_on_container(container: Container, command: str, workdir='/') -> tuple[int, str]:
    """
    Executes the given command on the given container in the provided working directory.
    """
    shell_safe_command = shlex.quote(command)

    exit_code, output = container.exec_run(f"sh -c {shell_safe_command}", # run commands on the shell
                                           demux=False,
                                           workdir=workdir) 
    return exit_code, output.decode("utf-8")


def add_file_to_container(
    container: Container, 
    container_path: str, 
    content: str, 
    mode: int = 0o644 # default file permissions (rw-r--r--)
) -> bool:
    """
    Adds a file with the given content to the specified path inside the container
    using container.put_archive(). Handles multi-line content and permissions.

    Args:
        container (Container): The Docker container object.
        container_path (str): The absolute path in the container where the file should be created.
        content (str): The string content to write to the file.
        mode (int): File permissions in octal (e.g., 0o644).

    Returns:
        bool: True if the file was added successfully, False otherwise.
    """
    print(f"\n--- Adding file '{container_path}' to container '{container.name}' ---")
    try:
        # Create a tar archive in memory.
        tar_stream = io.BytesIO()

        with tarfile.open(fileobj=tar_stream, mode='w') as tar:

            # Create a TarInfo object for the file.
            tarinfo = tarfile.TarInfo(name=os.path.basename(container_path))
            tarinfo.size = len(content.encode('utf-8')) # Size in bytes
            tarinfo.mode = mode # Set permissions
            tarinfo.mtime = time.time() # Modification time

            # Add the string content as a file-like object.
            tar.addfile(tarinfo, io.BytesIO(content.encode('utf-8')))
        
        # Reset stream position to the beginning before reading.
        tar_stream.seek(0) 

        # Put the archive into the container.
        # The 'path' argument to put_archive is the *directory* where the tar's contents will be extracted.
        succeeded = container.put_archive(
            path=os.path.dirname(container_path) or '/', # Destination directory in container
            data=tar_stream.read()
        )

        if succeeded:
            print(f"LOG: File '{container_path}' added successfully.")
        else:
            print("LOG: File creation failed.")

        return succeeded
    except Exception as e:
        print(f"LOG: Error adding file '{container_path}': {e}")
        return False


