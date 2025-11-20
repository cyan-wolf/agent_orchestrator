from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from utils.utils import get_env_raise_if_none

engine = create_engine(
    get_env_raise_if_none("DATABASE_URL"), 
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
"""
The base class for all ORM table classes.
"""

def get_database():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
