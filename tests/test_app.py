from http import HTTPStatus


def test_root_must_return_hello_world(client):
    response = client.get('/')
    assert response.json() == {'message': 'Hello world'}
    assert response.status_code == HTTPStatus.OK


def test_vamps_must_return_html_with_vamps_names(client):
    response = client.get('/vamps')
    assert (
        response.text
        == '<h1>Vamps:</h1>\
        <p>Angel, Spike, Drusilla</p>'
    )


def test_vamps_status_code_ok(client):
    response = client.get('/vamps')
    assert response.status_code == HTTPStatus.OK


def test_create_user(client):

    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'alice',
                'email': 'alice@example.com',
            }
        ]
    }


def test_update_client(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mistery',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_update_client_exception(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mistery',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
