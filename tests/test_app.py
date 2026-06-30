from http import HTTPStatus

from fastapi_study_project.schemas import UserPublic


def test_root_must_return_hello_world(client):
    response = client.get('/')
    assert response.json() == {'message': 'Hello world'}
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


def test_create_user_when_username_conflict(client, add_user):

    response = client.post(
        '/users/',
        json={
            'username': 'bob',
            'email': 'bobby@example.com',
            'password': 'mistery',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Invalid username'}


def test_create_user_when_email_conflict(client, add_user):

    response = client.post(
        '/users/',
        json={
            'username': 'bobby',
            'email': 'bob@example.com',
            'password': 'mistery',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Invalid e-mail'}


def test_read_users_empty_table(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, add_user):

    user_schema = UserPublic.model_validate(add_user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, add_user):
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


def test_update_user_when_user_not_found(client):
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


def test_update_integrity_error(client, add_user):
    client.post(
        '/users',
        json={
            'username': 'kiki',
            'email': 'kiki@theguillotine.com',
            'password': 'secret',
        },
    )

    response = client.put(
        f'/users/{add_user.id}',
        json={
            'username': 'kiki',
            'email': 'bob@example.com',
            'password': 'mystery',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_delete_user_when_user_not_found(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, add_user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_read_user_by_id(client, add_user):
    response = client.get(f'/users/{add_user.id}')

    user_schema = UserPublic.model_validate(add_user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_by_id_when_user_not_found(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
