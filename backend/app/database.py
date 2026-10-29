
import logging
import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings

logger = logging.getLogger(__name__)


def _get_connect_args() -> dict[str, ssl.SSLContext | bool]:
    """Return database connection arguments with optional SSL."""
    if settings.DATABASE_SSL:
        # Keep certificate and hostname verification enabled.
        ssl_context = ssl.create_default_context()
        return {"ssl": ssl_context}

    return {"ssl": False}


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=_get_connect_args(),
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session and manage its transaction."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Register all models and create missing database tables."""
    # Import the package to register model classes in Base.metadata.
    from . import models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    logger.info("Database tables created/verified successfully.")


async def close_db() -> None:
    """Dispose of the database connection pool during application shutdown."""
    await engine.dispose()
    logger.info("Database connection pool closed.")
