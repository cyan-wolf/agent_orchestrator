from fastapi import FastAPI

from auth.router import router as auth_router
from chat.router import router as chat_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}