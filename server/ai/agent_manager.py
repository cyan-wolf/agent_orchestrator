from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.runnables.config import RunnableConfig

from ai.tools import code_runner, control_flow, web_searching
from ai.tracing import Tracer, AIMessageTrace, HumanMessageTrace

from ai.agent import Agent

from datetime import datetime

def get_latest_agent_msg(agent_response: dict) -> BaseMessage:
    return agent_response["messages"][-1]


class AgentManager:
    def __init__(self):
        """
        Initializes an agent manager.
        """
        self.agents = {}

        config: RunnableConfig = {"configurable": {"thread_id": "1"}}
        self.config = config

        self.tracer = Tracer()

        self.initialize_agents()


    def initialize_agents(self):
        """
        Initializes and registers several agents.
        """

        self.register_agent(Agent("math_agent", "You are a helpful math assistant.", []))

        self.register_agent(Agent("coding_agent", 
            """
            You are a helpful coding assistant. You only work with Python, no other programming language.
            Always add comments and type annotations to any Python code you run.
            """, 
            [code_runner.prepare_run_python_program_tool(self), control_flow.prepare_switch_back_to_supervisor_tool(self)],
            checkpointer=InMemorySaver(),
        ))

        self.register_agent(Agent("research_agent",  
            f"""
            You are a helpful research agent. Use the web search tool to look for information. 
            The current date is {datetime.now()}.
            """, 
            [web_searching.prepare_web_search_tool(self)],
            checkpointer=InMemorySaver(),
        ))

        self.register_agent(Agent("writer_agent", 
            """
            You are a writer. You receive requests to write textual content such as poems, stories, scripts.
            """,
            []
        ))

        self.register_agent(Agent("supervisor_agent", 
            """
            You are a helpful assistant. You are kind of sassy. 
            You can answer any topic except for one caveat: never EVER answer questions about Bruno.

            Don't hesitate to use the `switch_to_more_qualified_agent` tool.
            """,
            control_flow.prepare_supervisor_agent_tools(self),
            checkpointer=InMemorySaver()
        ))

        # "main_agent" is the agent that the user directly chats with.
        self.agents["main_agent"] = self.agents["supervisor_agent"]

        # "current_agent" is the agent currently in control. This is 
        # used to keep track of which agents call the tools.
        self.agents["current_agent"] = self.agents["main_agent"]
 

    def register_agent(self, agent: Agent):
        """
        Registers the given agent to the agent manager. Allows the agent to be 
        called by other agents using its name.
        """
        self.agents[agent.name] = agent


    def invoke_agent(self, agent: Agent, user_input: str, as_main_agent: bool = False) -> str:
        """
        Invokes the given agent using the provided user input.
        """

        # Bookeeping to keep track of the agent currently in control.
        prev_agent = self.agents["current_agent"]
        self.agents["current_agent"] = agent

        res = agent.graph.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            self.config,
        )
        message = get_latest_agent_msg(res)
        content = str(message.content)
        self.tracer.add(AIMessageTrace(agent_name=agent.name, content=content, is_main_agent=as_main_agent))

        # `agent` is no longer in control.
        self.agents["current_agent"] = prev_agent

        return content


    def invoke_main_with_text(self, username: str, user_input: str) -> str:
        """
        Invokes the agent that is currently designated to be the main agent.
        """
        self.tracer.add(HumanMessageTrace(username=username, content=user_input))

        return self.invoke_agent(self.agents["main_agent"], user_input, as_main_agent=True)
