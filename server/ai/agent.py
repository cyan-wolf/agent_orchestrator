from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Checkpointer

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