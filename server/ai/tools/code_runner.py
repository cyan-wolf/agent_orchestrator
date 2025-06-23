import subprocess
from subprocess import DEVNULL

import os

from ai.tracing import trace, ProgramRunningSideEffectTrace

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = "\\".join(SCRIPT_PATH.split("\\")[:-1])

def write_python_source_file_to_disk(source_file_contents: str):
    with open(f"{SCRIPT_DIR}/dev_env/main.py", "w") as f:
        f.write(source_file_contents)

def build_container():
    res = subprocess.run(f"docker build -t dev_env_python {SCRIPT_DIR}/dev_env", stdout=DEVNULL, stderr=DEVNULL)
    
    if res.returncode != 0:
        raise Exception("could not build container")


def run_container() -> bytes:
    res = subprocess.run("docker run -it --rm dev_env_python", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if res.returncode != 0:
        raise Exception("could not run container")

    return res.stdout


def cleanup_docker_images():
    res = subprocess.run("docker image prune --force", stdout=DEVNULL, stderr=DEVNULL)

    if res.returncode != 0:
        raise Exception("could not clean up images")


def prepare_run_python_program_tool(agent_manager):
    @trace(agent_manager.tracer)
    def run_python_program(program_source_code: str) -> str:
        """This tool takes the contents of a Python source file as an argument. Then, the tool 
            automatically runs the file and returns the program's output.
        """
        try:
            print("WARNING: calling run file tool")

            write_python_source_file_to_disk(program_source_code)

            build_container()
            program_stdout = run_container().decode("utf-8")

            cleanup_docker_images()

            agent_manager.tracer.add(ProgramRunningSideEffectTrace(
                source_code=program_source_code,
                language="Python",
                output=program_stdout,
            ))

            return program_stdout

        except Exception as ex:
            return f"error: {ex}"
        
    return run_python_program
