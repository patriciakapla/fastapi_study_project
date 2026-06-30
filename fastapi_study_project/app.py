from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_study_project.database import get_session
from fastapi_study_project.models import User
from fastapi_study_project.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI()
database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello world'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):

    db_user = session.scalar(  # scalar will return User | None
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Invalid username'
            )
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Invalid e-mail'
        )

    db_user = User(**user.model_dump())

    session.add(db_user)
    session.commit()

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10, offset: int = 0, session: Session = Depends(get_session)
):

    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):

    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    try:
        user_db.username = user.username
        user_db.email = user.email
        user_db.password = user.password

        session.add(user_db)
        session.commit()

        return user_db
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    # big discussion if delete should return something or not.
    # when not returning, HTTP status will be 204 (no content).
    # when returning, 200. in this case it will return, so 200.
    response_model=Message,
)
def delete_user(user_id: int, session: Session = Depends(get_session)):

    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(user_db)
    session.commit()

    return {'message': 'User deleted'}


# @app.get(
#     '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
# )
# def read_user_by_id(user_id: int):

#     return ...
