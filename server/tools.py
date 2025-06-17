from datetime import datetime

import subprocess
from subprocess import DEVNULL

import os

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = "\\".join(SCRIPT_PATH.split("\\")[:-1])

def write_python_source_file_to_disk(source_file_contents: str):
    with open(f"{SCRIPT_DIR}/dev_env/main.py", "w") as f:
        f.write(source_file_contents)


def build_container():
    subprocess.run(f"docker build -t dev_env_python {SCRIPT_DIR}/dev_env", stdout=DEVNULL, stdin=DEVNULL)


def run_container():
    res = subprocess.run("docker run -it --rm dev_env_python", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.stdout


def cleanup_docker_images():
    subprocess.run("docker image prune --force", stdout=DEVNULL, stderr=DEVNULL)


def run_python_program(program_source_code: str) -> str:
    """This tool takes the contents of a Python source file as an argument. Then, the tool 
        automatically runs the file and returns the program's output.
    """
    print("WARNING: calling run file tool")

    write_python_source_file_to_disk(program_source_code)

    print("LOG: WROTE PYTHON SOURCE FILE")

    build_container()
    stdout = run_container()

    cleanup_docker_images()

    return stdout.decode("utf-8")


def get_current_date():
    """Returns the current date and time as a Python datetime object."""
    return datetime.now()


def compute_beans_function(x: int, y: int):
    """Applies the given argument to the beans function."""
    return x % 10 + y % 10


def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def add_two_numbers(x: int, y: int) -> int:
    """Definitely adds two numbers..."""
    return 2 * x + y