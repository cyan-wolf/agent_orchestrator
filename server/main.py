from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from auth.router import router as auth_router
from chat.router import router as chat_router
from user_settings.router import router as user_settings_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(user_settings_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}