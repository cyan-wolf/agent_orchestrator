from ai.agent_manager.agent_manager_interface import IAgentManager
from sqlalchemy.orm import Session
from dataclasses import dataclass

@dataclass
class AgentCtx:
    """
    A context object that holds a reference to an agent manager and a DB session.
    """
    manager: IAgentManager
    db: Session
