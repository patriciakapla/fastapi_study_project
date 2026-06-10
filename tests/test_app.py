from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_study_project.app import app


def test_root_must_return_hello_world():
    """
    Triple A testD
    A: Arrange
    A: Act - executes SUT
    A: Assert - asserts that x is x
    """
    # arrange
    client = TestClient(app)
    # act
    response = client.get('/')
    # assert
    assert response.json() == {'message': 'Hello world'}
    assert response.status_code == HTTPStatus.OK


def test_vamps_must_return_html_with_vamps_names():
    client = TestClient(app)
    response = client.get('/vamps')
    assert response.text == '<h1>Vamps:</h1>\
        <p>Angel, Spike, Drusilla</p>'


def test_vamps_status_code_OK():
    client = TestClient(app)
    response = client.get('/vamps')
    assert response.status_code == HTTPStatus.OK
