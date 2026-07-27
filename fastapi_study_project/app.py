import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from fastapi_study_project.routers import auth, todos, users
from fastapi_study_project.schemas import (
    Message,
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI()
database = []

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():

    return {'message': 'Hello world'}
