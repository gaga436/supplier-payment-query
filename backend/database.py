"""
数据库引擎和会话管理
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/payments.db")
# SQLite WAL mode for better concurrent reads
_extra = {"connect_args": {"check_same_thread": False}} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, echo=False, **_extra)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a session and closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
