from ai.agent_manager import AgentManager
from db.models import ChatTempDB, UserTempDB


class TempDB:
    def __init__(self):
        self.user_db: UserTempDB = self.load_users_db()
        self.chat_db: ChatTempDB = self.load_chat_db()

        # chat ID -> AgentManager
        self.runtime_agent_managers: dict[str, AgentManager] = {}
    
    def load_users_db(self):
        with open("db_placeholder_store/users.json", "r", encoding="utf-8") as f:
            json = f.read()
            return UserTempDB.model_validate_json(json)


    def load_chat_db(self):
        with open("db_placeholder_store/chats.json", "r", encoding="utf-8") as f:
            json = f.read()
            return ChatTempDB.model_validate_json(json)
        

    def store_users_db(self):
        with open("db_placeholder_store/users.json", "w", encoding="utf-8") as f:
            json = self.user_db.model_dump_json()
            f.write(json)


    def store_chat_db(self):
        with open("db_placeholder_store/chats.json", "w", encoding="utf-8") as f:
            json = self.chat_db.model_dump_json()
            f.write(json)

DB = TempDB()

def get_db() -> TempDB:
    return DB

