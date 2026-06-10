from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fastapi_study_project.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello world'}


@app.get('/vamps', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_vamps():
    return '<h1>Vamps:</h1>\
        <p>Angel, Spike, Drusilla</p>'
