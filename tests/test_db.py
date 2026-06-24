from dataclasses import asdict

from sqlalchemy import select

from fastapi_study_project.models import User
from fastapi_study_project.settings import Settings


def test_settings(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')

    settings = Settings()
    assert settings.DATABASE_URL == 'sqlite:///test.db'


def test_create_user_object(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='buffy', email='buffy@vampslayer.com', password='angel123'
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'buffy'))

    assert asdict(user) == {
        'id': 1,
        'username': 'buffy',
        'email': 'buffy@vampslayer.com',
        'password': 'angel123',
        'created_at': time,
        'updated_at': time,
        # mock_db_time fnc yields time, so it can be used!
    }
