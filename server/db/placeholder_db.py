# from ai.agent_manager import AgentManager # commented out due to circular import errors
from db.models import ChatTempDB, UserTempDB, ScheduleTempDB, UserSettingsTempDB
from typing import Any

class TempDB:
    def __init__(self):
        self.user_db: UserTempDB = self.load_users_db()
        self.chat_db: ChatTempDB = self.load_chat_db()
        self.schedules_db: ScheduleTempDB = self.load_schedules_db()
        self.user_settings_db: UserSettingsTempDB = self.load_user_settings_db()

        # chat ID -> AgentManager
        self.runtime_agent_managers: dict[str, Any] = {}
    
    def load_users_db(self):
        with open("db_placeholder_store/users.json", "r", encoding="utf-8") as f:
            json = f.read()
            return UserTempDB.model_validate_json(json)


    def load_chat_db(self):
        with open("db_placeholder_store/chats.json", "r", encoding="utf-8") as f:
            json = f.read()
            return ChatTempDB.model_validate_json(json)
        

    def load_schedules_db(self):
        with open("db_placeholder_store/schedules.json", "r", encoding="utf-8") as f:
            json = f.read()
            return ScheduleTempDB.model_validate_json(json)
        

    def load_user_settings_db(self):
        with open("db_placeholder_store/user_settings.json", "r", encoding="utf-8") as f:
            json = f.read()
            return UserSettingsTempDB.model_validate_json(json)
        

    def store_users_db(self):
        with open("db_placeholder_store/users.json", "w", encoding="utf-8") as f:
            json = self.user_db.model_dump_json()
            f.write(json)


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

DB = TempDB()

def get_db() -> TempDB:
    return DB

