"""Database connection and session management."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Database stored in web_data/ which persists across restarts
DB_DIR = Path(os.environ.get("WEB_DB_DIR", Path(__file__).resolve().parent.parent / "web_data"))
DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR / 'web.sqlite'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
