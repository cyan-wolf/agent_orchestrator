from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.runnables.config import RunnableConfig

from datetime import datetime

import subprocess
from subprocess import DEVNULL

AGENTS = {}

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def get_current_date():
    """Returns the current date and time as a Python datetime object."""
    return datetime.now()


def compute_beans_function(x: int, y: int):
    """Applies the given argument to the beans function."""
    return x % 10 + y % 10


def request_math_help(query: str) -> str:
    """Asks the math expert for help."""

    res = AGENTS["math_agent"].invoke(
        {"messages": [{"role": "user", "content": query}]},
        config,
    )
    return res["messages"][-1].content


def request_coding_help(query: str) -> str:
    """Asks the coding expert for help writing a Python program."""

    res = AGENTS["coding_agent"].invoke(
        {"messages": [{"role": "user", "content": query}]},
        config,
    )
    return res["messages"][-1].content


def write_python_source_file_to_disk(source_file_contents: str):
    with open("dev_env/main.py", "w") as f:
        f.write(source_file_contents)


def build_container():
    subprocess.run("docker build -t dev_env_python ./dev_env", stdout=DEVNULL, stderr=DEVNULL)


def run_container():
    res = subprocess.run("docker run -it --rm dev_env_python", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.stdout


def run_python_file(source_file_contents: str) -> str:
    """This tool takes the contents of a Python source file as an argument. Then, the tool 
        automatically runs the file and returns the program's output.
    """
    print("WARNING: calling run file tool")

    write_python_source_file_to_disk(source_file_contents)
    build_container()
    stdout = run_container()

    cleanup_docker_images()

    return stdout.decode("utf-8")


def cleanup_docker_images():
    subprocess.run("docker image prune --force", stdout=DEVNULL, stderr=DEVNULL)


def run_python_program(program_source_code: str) -> str:
    """Runs the given Python source code."""

    return run_python_file(program_source_code)


def prepare_agent():
    model = init_chat_model(
        "google_genai:gemini-2.0-flash",
        temperature=0,
    )

    checkpointer = InMemorySaver()

    agent = create_react_agent(
        model=model,  
        tools=[get_weather, compute_beans_function, get_current_date, request_math_help, request_coding_help, run_python_program],  
        prompt="You are a helpful assistant. You are kind of sassy. You can answer any topic except for one caveat: never EVER answer questions about Bruno.",
        checkpointer=checkpointer,
    )

    return agent


def prepare_math_agent():
    model = init_chat_model(
        "google_genai:gemini-2.0-flash",
        temperature=0,
    )

    def add_two_numbers(x: int, y: int) -> int:
        """Definitely adds two numbers..."""
        return 2 * x + y

    return create_react_agent(
        model=model,  
        tools=[add_two_numbers],  
        prompt="You are a helpful math assistant.",
    )

def prepare_coding_agent():
    model = init_chat_model(
        "google_genai:gemini-2.0-flash",
        temperature=0,
    )

    return create_react_agent(
        model=model,  
        tools=[],  
        prompt="You are a helpful coding assistant. You generate Python programs.",
    )

def prepare_helper_agents():
    AGENTS["math_agent"] = prepare_math_agent()
    AGENTS["coding_agent"] = prepare_coding_agent()

prepare_helper_agents()
agent = prepare_agent()
config: RunnableConfig = {"configurable": {"thread_id": "1"}}


def invoke_agent(user_input: str) -> dict:
    # Run the agent
    res = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
    )
    return res


def get_latest_agent_msg(agent_response: dict) -> str:
    return agent_response["messages"][-1].content


def run_debug_prompt_loop():
    while True:
        try:
            user_input = input("user> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            resp = invoke_agent(user_input)
            message = get_latest_agent_msg(resp)

            for m in resp["messages"]:
                print(type(m))
                print(m.content)

            # print(f"AI> {message}")

        except Exception as ex:
            print(f"error: {ex}")
            break


if __name__ == "__main__":
    run_debug_prompt_loop()
