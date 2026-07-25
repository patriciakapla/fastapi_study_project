from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_token_expired_after_time(client, user):
    with freeze_time('1981-01-19 12:00:00'):
        response = client.post(
            'auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('1981-01-19 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'nope',
                'email': 'nope@nope.com',
                'password': 'nopy-nope',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_wrong_password(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': 'nopy-nope'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect password'}


def test_token_wrong_user(client):
    response = client.post(
        '/auth/token', data={'username': 'nopety-no', 'password': 'nopy-nope'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect e-mail'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_token_expired_dont_refresh(client, user):
    with freeze_time('1981-01-19 12:00:00'):
        response = client.post(
            'auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('1981-01-19 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
