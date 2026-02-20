"""Pytest configuration and fixtures for tests"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base

# Import all models to ensure they're registered with SQLAlchemy
from app.user_app.models import (  # noqa: F401
    User, Employe, Service, Group, ServiceGroup,
    UserGroup, Permission, GroupPermission, Contrat, Document
)
from app.paie_app.models import (  # noqa: F401
    Alert, RetenueEmploye, PeriodePaie, EntreePaie
)


TEST_DATABASE_URL = (
    "postgresql+asyncpg://neondb_owner:npg_gZ4eYlSdwr3o@"
    "ep-tiny-sound-agslibpd-pooler.c-2.eu-central-1.aws.neon.tech/"
    "rh_db?ssl=require"
)


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with transaction rollback"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()
