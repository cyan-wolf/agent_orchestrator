# from ai.agent_manager import AgentManager # commented out due to circular import errors
from db.models import ChatTempDB, ScheduleTempDB, UserSettingsTempDB
from ai.agent_manager_interface import IAgentManager
import os

class TempDB:
    def __init__(self):
        self.create_temp_store_dir_if_not_present()

        self.chat_db: ChatTempDB = self.load_chat_db()
        self.schedules_db: ScheduleTempDB = self.load_schedules_db()
        self.user_settings_db: UserSettingsTempDB = self.load_user_settings_db()

        # chat ID -> AgentContext (AgentManager)
        self.runtime_agent_managers: dict[str, IAgentManager] = {}


    def create_temp_store_dir_if_not_present(self):
        if not os.path.exists("db_placeholder_store"):
            os.mkdir("db_placeholder_store")


    def load_chat_db(self):
        try:
            with open("db_placeholder_store/chats.json", "r", encoding="utf-8") as f:
                json = f.read()
                return ChatTempDB.model_validate_json(json)
            
        except FileNotFoundError:
            print(f"LOG: could not load chats; generating empty table")
            return ChatTempDB(chats={})
        

    def load_schedules_db(self):
        try:
            with open("db_placeholder_store/schedules.json", "r", encoding="utf-8") as f:
                json = f.read()
                return ScheduleTempDB.model_validate_json(json)
            
        except FileNotFoundError:
            print(f"LOG: could not load schedules; generating empty table")
            return ScheduleTempDB(schedules={})
        

    def load_user_settings_db(self):
        try:    
            with open("db_placeholder_store/user_settings.json", "r", encoding="utf-8") as f:
                json = f.read()
                return UserSettingsTempDB.model_validate_json(json)
        
        except FileNotFoundError:
            print(f"LOG: could not load user settings; generating empty table")
            return UserSettingsTempDB(user_settings={})


    def store_chat_db(self):
        with open("db_placeholder_store/chats.json", "w", encoding="utf-8") as f:
            json = self.chat_db.model_dump_json()
            f.write(json)


    def store_schedules_db(self):
        with open("db_placeholder_store/schedules.json", "w", encoding="utf-8") as f:
            json = self.schedules_db.model_dump_json()
            f.write(json)


    def store_user_settings_db(self):
        with open("db_placeholder_store/user_settings.json", "w", encoding="utf-8") as f:
            json = self.user_settings_db.model_dump_json()
            f.write(json)


    def reset_runtime_agent_managers_for_user(self, username: str):
        """
        Resets (deletes) all the runtime agent managers associated with this user.
        """
        for chat in self.chat_db.chats[username]:
            if chat.chat_id in self.runtime_agent_managers:
                del self.runtime_agent_managers[chat.chat_id]
                print(f"LOG: deleted runtime agent manager for chat ({chat.chat_id})")


DB = TempDB()

def get_temp_db() -> TempDB:
    return DB

