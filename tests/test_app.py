from http import HTTPStatus


def test_root_must_return_hello_world(client):
    response = client.get('/')
    assert response.json() == {'message': 'Hello world'}
    assert response.status_code == HTTPStatus.OK
