from ai.agent_manager.agent_manager_interface import IAgentManager
import uuid

class AgentMangerInMemoryStore:
    def __init__(self):
        self.in_memory_store: dict[uuid.UUID, IAgentManager] = {}

    
    def get_manager_for_chat(self, chat_id: uuid.UUID) -> IAgentManager | None:
        return self.in_memory_store.get(chat_id)

    
    def register_manager_for_chat(self, manager: IAgentManager):
        print(f"LOG: manager registered for chat {manager.get_chat_id()}")
        self.in_memory_store[manager.get_chat_id()] = manager


    def delete_entry_with_chat_id(self, chat_id: uuid.UUID) -> bool:
        if chat_id in self.in_memory_store:
            del self.in_memory_store[chat_id]
            return True
        
        return False


_SINGLETON_MEM_STORE = AgentMangerInMemoryStore()

def get_manager_in_mem_store() -> AgentMangerInMemoryStore:
    return _SINGLETON_MEM_STORE

