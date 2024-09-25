import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..core.database import Base, get_session
from ..crud.user import authenticate_user, create_user, get_user_by_email
from ..main import app
from ..schemas.user import UserCreate

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Ensure that the event loop is properly set up for async tests
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# Create a test engine and session for the database
@pytest.fixture(scope="session")
async def test_engine():
    # Create the test database engine
    engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    # Create the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # Drop the database tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(test_engine):
    # Create a new session for each test
    async_session_maker = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


# Override the get_session dependency to use the test session
@pytest.fixture(scope="function", autouse=True)
def override_get_session(async_session):
    async def _get_test_session():
        yield async_session

    app.dependency_overrides[get_session] = _get_test_session
    yield
    app.dependency_overrides[get_session] = get_session


# Now, we can write test functions to test our database interactions
@pytest.mark.anyio
async def test_create_user(async_session):
    user_in = UserCreate(
        email="testuser@example.com", username="testuser", password="testpassword"
    )
    new_user = await create_user(async_session, user_in)
    assert new_user.email == "testuser@example.com"
    assert new_user.username == "testuser"


@pytest.mark.anyio
async def test_get_user_by_email(async_session):
    user = await get_user_by_email(async_session, "testuser@example.com")
    assert user is not None
    assert user.email == "testuser@example.com"


@pytest.mark.anyio
async def test_authenticate_user(async_session):
    user = await authenticate_user(async_session, "testuser", "testpassword")
    assert user is not None
    assert user.username == "testuser"
