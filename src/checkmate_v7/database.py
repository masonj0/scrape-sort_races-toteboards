# src/checkmate_v7/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings
from .models import Base

class DatabaseManager:
    """A singleton manager for the application's database engine and sessions."""
    _engine = None
    _SessionLocal = None

    @classmethod
    def get_engine(cls):
        """
        Returns the singleton SQLAlchemy engine instance, creating it if necessary.
        Implements production-grade connection pooling.
        """
        if cls._engine is None:
            cls._engine = create_engine(
                settings.DATABASE_URL,
                pool_size=20,          # Production-ready pool size
                max_overflow=30,       # Allow for burst connections
                pool_pre_ping=True,      # Check connections before use
                pool_recycle=3600,       # Recycle connections hourly
                connect_args={"check_same_thread": False} # Required for SQLite
            )
            # Create tables if they don't exist
            Base.metadata.create_all(bind=cls._engine)
        return cls._engine

    @classmethod
    def get_session(cls):
        """
        Returns a new SQLAlchemy session from our session factory.
        """
        if cls._SessionLocal is None:
            engine = cls.get_engine()
            cls._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        return cls._SessionLocal()

# Convenience function for dependency injection
def get_db_session():
    return DatabaseManager.get_session()