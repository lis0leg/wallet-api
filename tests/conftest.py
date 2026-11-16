import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.base import Base
from app.db.database import get_session
from app.db import models
from app.main import app


@pytest_asyncio.fixture
async def engine_test():
    engine = create_async_engine(
        settings.database_url_test,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine_test):
    testing_session_local = async_sessionmaker(
        bind=engine_test,
        expire_on_commit=False,
    )

    async with testing_session_local() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine_test):
    testing_session_local = async_sessionmaker(
        bind=engine_test,
        expire_on_commit=False,
    )

    async def override_get_session():
        async with testing_session_local() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()