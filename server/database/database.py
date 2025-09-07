from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from pathlib import Path

PATH = Path(__file__).parent.parent / "agent_orchestrator.db"
URL = f"sqlite:///{PATH}"

engine = create_engine(URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_database():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
