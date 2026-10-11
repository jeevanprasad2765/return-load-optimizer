import sys
import asyncio
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase
import sqlalchemy.types as types
from datetime import datetime, timezone
from app.config import settings

# Fix Windows ProactorEventLoop issue with asyncpg/aiosqlite in older Python versions
if sys.platform == "win32" and sys.version_info < (3, 14):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class UTCDateTime(types.TypeDecorator):
    """
    Ensures datetimes are stored as timezone-aware UTC and retrieved as timezone-aware UTC.
    Fixes SQLite timezone truncation by guaranteeing UTC tzinfo on every read and write.
    """
    impl = types.DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, str):
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
        return value

# Create Engine
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        datetime: UTCDateTime
    }

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
