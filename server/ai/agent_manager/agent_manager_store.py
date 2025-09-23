from ai.agent_manager.agent_manager_interface import IAgentManager
import uuid

class AgentMangerInMemoryStore:
    """
    An in-memory store for agent managers.
    """

    def __init__(self):
        """
        Initializes an empty in-memory store.
        """
        self.in_memory_store: dict[uuid.UUID, IAgentManager] = {}

    
    def get_manager_for_chat(self, chat_id: uuid.UUID) -> IAgentManager | None:
        """
        Returns the agent manager for the given chat. Returns `None` if a manager has not 
        been registered for the chat yet.
        """
        return self.in_memory_store.get(chat_id)

    
    def register_manager_for_chat(self, manager: IAgentManager):
        """
        Registers an agent manager to its associated chat.
        """

        print(f"LOG: manager registered for chat {manager.get_chat_id()}")
        self.in_memory_store[manager.get_chat_id()] = manager


    def delete_entry_with_chat_id(self, chat_id: uuid.UUID) -> bool:
        """
        Deletes a manager entry in the in-memory store.
        """

        if chat_id in self.in_memory_store:
            del self.in_memory_store[chat_id]
            return True
        
        return False


_SINGLETON_MEM_STORE = AgentMangerInMemoryStore()

def get_manager_in_mem_store() -> AgentMangerInMemoryStore:
    return _SINGLETON_MEM_STORE

