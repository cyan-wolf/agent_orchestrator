from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
load_dotenv()

from fastapi import FastAPI

from auth.router import router as auth_router
from chat.router import router as chat_router
from user_settings.router import router as user_settings_router

from pathlib import Path

# For making sure the database is setup.
from database.database import Base, engine

# Side-effect import all the tables to make sure they are loaded.
import auth.tables as _
import user_settings.tables as _
import ai.tools.scheduling.tables as _

# Create the metadata on the engine.
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(user_settings_router)



FRONTEND_BUILD_PATH = Path(__file__).parent.parent / "client" / "agent-orchestrator-client" / "dist"

if not FRONTEND_BUILD_PATH.is_dir():
    raise RuntimeError(
        "Frontend build directory not found. Please run 'npm run build' inside the 'frontend' directory first."
    )

# Mounts a static route for hosting necessary assets.
app.mount("/assets", StaticFiles(directory=FRONTEND_BUILD_PATH / "assets"), name="assets")

# Catch all route that serves the frontend `index.html`.
@app.get("/{full_path:path}")
def serve_front_end_with_catchall():
    return FileResponse(FRONTEND_BUILD_PATH / "index.html")

