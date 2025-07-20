from db.models import ChatTempDB, UserTempDB


class TempDB:
    def __init__(self):
        self.user_db: UserTempDB = self.load_users_db()
        self.chat_db: ChatTempDB = self.load_chat_db()

    
    def load_users_db(self):
        with open("db_placeholder_store/users.json", "r") as f:
            json = f.read()
            return UserTempDB.model_validate_json(json)


    def load_chat_db(self):
        with open("db_placeholder_store/chats.json", "r") as f:
            json = f.read()
            return ChatTempDB.model_validate_json(json)

DB = TempDB()

def get_db() -> TempDB:
    return DB

