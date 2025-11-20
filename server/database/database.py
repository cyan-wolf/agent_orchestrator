from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

_URL = os.environ.get("DATABASE_URL")

if _URL is None:
    raise Exception("missing database connection string")

engine = create_engine(_URL, pool_pre_ping=True)

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
