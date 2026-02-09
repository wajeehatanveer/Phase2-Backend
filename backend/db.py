from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
from .settings import settings
import logging

logger = logging.getLogger(__name__)

# Try to create the primary database engine from settings. If that fails
# (e.g. remote DB not reachable in dev), fall back to a local SQLite file
# so the API remains usable for local development and testing.
def _create_engine_from_url(url: str):
    return create_engine(
        url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )

engine = None
try:
    if getattr(settings, "database_url", None):
        engine = _create_engine_from_url(settings.database_url)
        # Try a quick connect to validate the DB is reachable
        try:
            with engine.connect():
                pass
        except Exception as e:
            logger.warning("Primary database unreachable, falling back to SQLite: %s", e)
            engine = None
    if engine is None:
        # Fallback to SQLite file for local/dev usage
        sqlite_url = "sqlite:///./dev.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        logger.info("Using fallback SQLite database at %s", sqlite_url)
except OperationalError as e:
    # If something goes wrong creating the engine, fall back to SQLite
    logger.warning("Operational error when creating DB engine, falling back to SQLite: %s", e)
    engine = create_engine("sqlite:///./dev.db", connect_args={"check_same_thread": False})