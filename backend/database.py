"""
ACDRIP+ Database Module
SQLAlchemy database engine and session management.
Supports SQLite (default) and PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create engine - use check_same_thread only for SQLite
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from models import User, Scan, Vulnerability, Report, Alert  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully.")
