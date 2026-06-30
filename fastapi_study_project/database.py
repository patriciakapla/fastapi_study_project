from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_study_project.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session
        """ yield allows connection to be mantained.
        with return, session is closed immediately.
        with + yield ensures the session stays open for the
        entire request, and is closed automatically afterward"""
