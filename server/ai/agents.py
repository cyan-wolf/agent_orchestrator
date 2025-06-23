from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage
from langgraph.types import Checkpointer
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.runnables.config import RunnableConfig

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph

from langchain_tavily import TavilySearch

from ai.tools import generic_tools, code_runner, control_flow
from ai.tracing import Tracer, AIMessageTrace, HumanMessageTrace

def get_latest_agent_msg(agent_response: dict) -> BaseMessage:
    return agent_response["messages"][-1]


class Agent:
    def __init__(self, name: str, master_prompt: str, tools: list, model: BaseChatModel | None = None, checkpointer: Checkpointer = None):
        """
        Initializes an agent.
        """
        self.name = name
        self.graph = self.prepare_agent_graph(master_prompt, tools, model, checkpointer)


    def prepare_default_chat_model(self) -> BaseChatModel:
        """
        Prepares a default chat model for an agent.
        """
        return init_chat_model(
            "google_genai:gemini-2.0-flash",
            temperature=0,
        )


    def prepare_agent_graph(self, master_prompt: str, tools: list, model: BaseChatModel | None = None, checkpointer: Checkpointer = None) -> CompiledGraph:
        """
        Prepares the graph that the agent uses for control flow.
        """
        if model is None:
            model = self.prepare_default_chat_model()

        return create_react_agent(
            model=model,  
            tools=tools,  
            prompt=master_prompt,
            checkpointer=checkpointer,
        )


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
            checkpointer=InMemorySaver()
        ))

        self.register_agent(Agent("research_agent",  
            """
            You are a helpful research agent. You look for articles on the internet. 
            You can also tell the current time and use it to tell if an article is 
            talking about something in the past or in the future.
            """, 
            # TODO: I need to trace the Tavily search tool      vvvvvvvvvvvvvvvvvvvvvvvvvvv
            [generic_tools.prepare_get_current_date_tool(self), TavilySearch(max_results=5)]
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

        self.agents["main_agent"] = self.agents["supervisor_agent"]
 

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

        res = agent.graph.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            self.config,
        )
        message = get_latest_agent_msg(res)
        content = str(message.content)
        self.tracer.add(AIMessageTrace(agent.name, content, as_main_agent=as_main_agent))
        return content


    def invoke_main_with_text(self, user_input: str) -> str:
        """
        Invokes the agent that is currently designated to be the main agent.
        """
        self.tracer.add(HumanMessageTrace("TEMP_USER", user_input))

        return self.invoke_agent(self.agents["main_agent"], user_input, as_main_agent=True)
