from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from factory.base import Factory
from factory.declarations import LazyAttribute, Sequence
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fastapi_study_project.app import app
from fastapi_study_project.database import get_session
from fastapi_study_project.models import User, table_registry
from fastapi_study_project.security import get_password_hash
from fastapi_study_project.settings import Settings


@pytest.fixture
def client(session):
    # session is the session yielded by fixture session()
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        # since dependency_overrides is replacing a func, it expects a func
        # thats why we dont pass the session provided by the fixture directly!
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        # allows multiple threads to use this connection
        # (needed for client fixture)
        poolclass=StaticPool,  # uses same connection to both threads
        # necessary because in-memory SQLite database exists
        # only for a single connection. Ensures only one sqlite connection
        # so in-memory database is shared.
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
        # run_sync creates tables sync, NOT async!

    async with AsyncSession(engine, expire_on_commit=False) as s:
        yield s

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session: AsyncSession):

    pwd = 'mystery'
    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = pwd  # pyright: ignore
    # monkeypatch! -> change or attach behavior/data at runtime.
    # here, clean password isnt on the db, only in the object
    # we'll use for verifying if hash pwd = clean pwd

    return user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):

    pwd = 'mystery'
    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = pwd  # pyright: ignore

    return user


@contextmanager
def _mock_db_time(model, time=datetime(2026, 6, 26)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    event.listen(model, 'before_update', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)
    event.remove(model, 'before_update', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def token(client, user):

    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()


class UserFactory(Factory):
    class Meta:
        model = User

    # when instantiated, this class creates a new
    # User (table class) object

    username = Sequence(lambda n: f'test{n}')
    email = LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = LazyAttribute(lambda obj: f'{obj.username}.pass')
    # created_at and id are init=True, so we dont have to tell
    # the class what are the values, they are automatically
    # generated when it goes through the db
