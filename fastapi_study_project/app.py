from http import HTTPStatus

from fastapi import FastAPI

from fastapi_study_project.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello world'}
