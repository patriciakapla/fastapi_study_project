from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_study_project.models import User
from fastapi_study_project.settings import Settings


def test_settings(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')

    settings = Settings()
    assert settings.DATABASE_URL == 'sqlite:///test.db'


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='buffy', email='buffy@vampslayer.com', password='angel123'
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'buffy')
        )

    assert asdict(user) == {  # pyright: ignore[reportArgumentType]
        'id': 1,
        'username': 'buffy',
        'email': 'buffy@vampslayer.com',
        'password': 'angel123',
        'created_at': time,
        'updated_at': time,
        'todos': [],
        # mock_db_time fnc yields time, so it can be used!
    }
