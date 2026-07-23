from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_study_project.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
        """ yield allows connection to be mantained.
        with return, session is closed immediately.
        with + yield ensures the session stays open for the
        entire request, and is closed automatically afterward"""
