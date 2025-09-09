# from ai.agent_manager import AgentManager # commented out due to circular import errors
from db.schemas import UserSettingsTempDB
import os

class TempDB:
    def __init__(self):
        self.create_temp_store_dir_if_not_present()

        # self.chat_db: ChatTempDB = self.load_chat_db()
        self.user_settings_db: UserSettingsTempDB = self.load_user_settings_db()

        # chat ID -> AgentContext (AgentManager)
        # self.runtime_agent_managers: dict[str, IAgentManager] = {}


    def create_temp_store_dir_if_not_present(self):
        if not os.path.exists("db_placeholder_store"):
            os.mkdir("db_placeholder_store")
        

    def load_user_settings_db(self):
        try:    
            with open("db_placeholder_store/user_settings.json", "r", encoding="utf-8") as f:
                json = f.read()
                return UserSettingsTempDB.model_validate_json(json)
        
        except FileNotFoundError:
            print(f"LOG: could not load user settings; generating empty table")
            return UserSettingsTempDB(user_settings={})


    def store_user_settings_db(self):
        with open("db_placeholder_store/user_settings.json", "w", encoding="utf-8") as f:
            json = self.user_settings_db.model_dump_json()
            f.write(json)


DB = TempDB()

def get_temp_db() -> TempDB:
    return DB

