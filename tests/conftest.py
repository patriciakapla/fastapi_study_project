from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastapi_study_project.app import app
from fastapi_study_project.database import get_session
from fastapi_study_project.models import User, table_registry


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


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        # allows multiple threads to use this connection
        # (needed for client fixture)
        poolclass=StaticPool,  # uses same connection to both threads
        # necessary because in-memory SQLite database exists
        # only for a single connection. Ensures only one sqlite connection
        # so in-memory database is shared.
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as s:
        yield s

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def add_user(session: Session):
    user = User(
        username='bob',
        email='bob@example.com',
        password='mistery',
    )
    session.add(user)
    session.commit()
    session.refresh(user)

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
