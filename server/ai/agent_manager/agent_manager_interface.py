from typing import Protocol
from ai.tracing.tracer import Tracer
from ai.agent.agent_interface import IAgent
from sqlalchemy.orm import Session
import uuid
from collections import defaultdict

class IAgentManager(Protocol):
    """
    An interface that represents a manager of various agents.
    """
    
    def get_owner_username(self) -> str:
        ...

    def get_owner_user_id(self) -> uuid.UUID:
        ...

    def get_chat_id(self) -> uuid.UUID:
        ...

    def get_tracer(self) -> Tracer:
        ...

    def get_agent_dict(self) -> dict[str, IAgent]:
        ...
    
    def get_chat_summary_dict(self) -> defaultdict[str, str]:
        ...

    def set_chat_summary_for_current(self, db: Session, chat_summary_content: str) -> None:
        ...

    def invoke_agent(self, agent: IAgent, user_input: str, db: Session, as_main_agent: bool = False) -> str:
        ...

    def invoke_main_agent_with_text(self, username: str, user_input: str, db: Session) -> str:
        ...

    def queue_agent_handoff(self, agent_name_prev: str, agent_name_new: str, handoff_reason: str):
        ...