from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_study_project.database import get_session
from fastapi_study_project.models import User
from fastapi_study_project.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_study_project.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()
database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():

    return {'message': 'Hello world'}


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):

    users = session.scalars(select(User).limit(limit).offset(offset))

    return {'users': users}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user_by_id(user_id: int, session: Session = Depends(get_session)):

    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user_db


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
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Invalid e-mail'
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()

    return db_user


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()

        return current_user

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
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),  # weirdddd
    session: Session = Depends(get_session),
):
    user = session.scalar(
        select(User).where(User.email == form_data.username)
        # in this case, the email is used to log in.
        # in the form, the data used to log in is called username,
        # even if its an email
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect e-mail'
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect password'
        )

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
