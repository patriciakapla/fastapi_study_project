from datetime import datetime
from enum import Enum

# from fastapi_study_project.settings import Settings
from sqlalchemy import ForeignKey, func  # , create_engine
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

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
    todos: Mapped[list[Todo]] = relationship(
        init=False,
        cascade='all, delete-orphan',
        # when a user is deleted, all its todos are also deleted
        lazy='selectin',
        # selectin = select in -> everytime a user is selected,
        # all their todos are returned in a list.
        # could also be joined - see sqlalchemy's doc
    )


class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todo'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    state: Mapped[TodoState] = mapped_column()
    is_urgent: Mapped[bool] = mapped_column(insert_default=False)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
