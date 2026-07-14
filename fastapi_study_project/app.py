from http import HTTPStatus

from fastapi import FastAPI

from fastapi_study_project.routers import auth, users
from fastapi_study_project.schemas import (
    Message,
)

app = FastAPI()
database = []

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():

    return {'message': 'Hello world'}
