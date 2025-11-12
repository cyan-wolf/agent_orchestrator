from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

from ai.tracing.schemas import AIMessageTrace, HumanMessageTrace
from ai.tracing.trace_decorator import Tracer
from ai.agent.runtime.agent_interface import IAgent
from chat.tables import ChatTable
from chat.chat_summaries import chat_summaries
from sqlalchemy.orm import Session
from ai.agent_manager.agent_context import AgentCtx
import uuid

from dataclasses import dataclass

@dataclass
class AgentHandoff:
    agent_name_prev: str
    agent_name_new: str
    handoff_reason: str


class RuntimeAgentManager:
    """
    The runtime representation of an agent manager. 
    """

    def __init__(self, chat: ChatTable, chat_summaries: defaultdict[str, str], tracer: Tracer):
        """
        Initializes an agent manager.

        Args:
            db: The DB session to use during initialization.
            chat_id: The ID of the chat associated with this agent manager.
            owner_username: The username of the user associated with this manager.
            chat_summaries: The current chat summaries present when this manager was created.
            tracer: The tracer associated with this manager.
        """
        self.agents: dict[str, IAgent] = {}

        self.tracer = tracer

        self.chat_summaries = chat_summaries

        self.chat_id = chat.id
        self.owner_username = chat.user.username
        self.owner_user_id = chat.user.id

        self.queued_handoff: AgentHandoff | None = None


    # ===== Protocol methods for `AgentManager` interface. =====

    def get_owner_username(self) -> str:
        return self.owner_username
    
    def get_owner_user_id(self) -> uuid.UUID:
        return self.owner_user_id

    def get_chat_id(self) -> uuid.UUID:
        return self.chat_id

    def get_tracer(self) -> Tracer:
        return self.tracer
    
    def get_agent_dict(self) -> dict[str, IAgent]:
        return self.agents
    
    def get_chat_summary_dict(self) -> defaultdict[str, str]:
        return self.chat_summaries
    
    def set_chat_summary_for_current(self, db: Session, chat_summary_content: str) -> None:
        self._set_chat_summary(db, chat_summary_content)

    def invoke_agent(self, agent: IAgent, user_input: str, db: Session, as_main_agent: bool = False) -> str:
        """
        Invokes the given agent using the provided user input.
        """

        # Bookeeping to keep track of the agent currently in control.
        prev_agent = self.agents["current_agent"]
        self.agents["current_agent"] = agent

        content = agent.invoke_with_text(user_input)
        self.tracer.add(db, AIMessageTrace(agent_name=agent.get_name(), content=content, is_main_agent=as_main_agent))

        if self.queued_handoff is not None:
            handoff = self.queued_handoff
            self.queued_handoff = None
            
            self._execute_agent_handoff(db, handoff)

        else:
            # If no hand-off occured, then we can safely restore the 'current_agent' back to its original value.
            self.agents["current_agent"] = prev_agent

        return content

    def invoke_main_agent_with_text(self, username: str, user_input: str, db: Session) -> str:
        """
        Invokes the agent that is currently designated to be the main agent.
        """
        self.curr_db_session = db
        self.tracer.add(db, HumanMessageTrace(username=username, content=user_input))

        return self.invoke_agent(self.agents["main_agent"], user_input, db, as_main_agent=True)


    def queue_agent_handoff(self, agent_name_prev: str, agent_name_new: str, handoff_reason: str):
        self.queued_handoff = AgentHandoff(
            agent_name_prev=agent_name_prev,
            agent_name_new=agent_name_new,
            handoff_reason=handoff_reason,
        )


    # ===== Other methods =====

    def initialize_agents(self, agents: list[IAgent]):
        """
        Initializes and registers several agents.
        """

        for agent in agents:
            self._register_agent(agent)

        # "main_agent" is the agent that the user directly chats with.
        self.agents["main_agent"] = self.agents["supervisor_agent"]

        # "current_agent" is the agent currently in control. 
        self.agents["current_agent"] = self.agents["main_agent"]


    def to_ctx(self, db: Session) -> AgentCtx:
        return AgentCtx(manager=self, db=db)

    def _register_agent(self, agent: IAgent):
        """
        Registers the given agent to the agent manager. Allows the agent to be 
        called by other agents using its name.
        """
        self.agents[agent.get_name()] = agent


    def _set_chat_summary(self, db: Session, chat_summary_content: str):
        """
        Sets the chat summary for the current agent.
        """
        agent_name = self._get_current_agent_name()

        # Save the chat summary to both the DB and the manager's runtime dictionary.
        chat_summaries.set_agent_chat_summary_in_db(db, self.chat_id, agent_name, chat_summary_content)
        self.chat_summaries[agent_name] = chat_summary_content


    def _get_current_agent_name(self) -> str:
        return self.agents["current_agent"].get_name()
    
        
    def _execute_agent_handoff(self, db: Session, agent_handoff: AgentHandoff):
        # Switch the 'main_agent' (i.e. the agent actually in control).
        self.get_agent_dict()["main_agent"] = self.get_agent_dict()[agent_handoff.agent_name_new]

        # Tell the new 'main_agent' what it's supposed to do.
        # NOTE: We don't use the `invoke_main_agent_with_text` method since that assumes the message is from a user.
        self.invoke_agent(
            self.get_agent_dict()["main_agent"], 
            f"The '{agent_handoff.agent_name_prev}' agent handed off the user to you! Do your best. This was its reason: {agent_handoff.handoff_reason}",
            db,
            as_main_agent=True,
        )