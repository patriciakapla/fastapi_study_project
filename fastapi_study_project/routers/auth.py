from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_study_project.database import get_session
from fastapi_study_project.models import User
from fastapi_study_project.schemas import (
    Token,
)
from fastapi_study_project.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2Form,  # weirdddd
    session: T_Session,
):
    user = await session.scalar(
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


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token({'sub': user.email})
    return {'access_token': new_access_token, 'token_type': 'Bearer'}
