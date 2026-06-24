from datetime import datetime

# from fastapi_study_project.settings import Settings
from sqlalchemy import func  # , create_engine
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()

# engine = create_engine(Settings().DATABASE_URL)


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
