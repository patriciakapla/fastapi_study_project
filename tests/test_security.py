from http import HTTPStatus

from jwt import decode

from fastapi_study_project.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_password_verification():

    pwd = 'test'

    hashed_pwd = get_password_hash(pwd)

    verification = verify_password(pwd, hashed_pwd)

    assert verification


def test_jwt():
    claim = {'test': 'test'}

    token = create_access_token(claim)

    decoded = decode(token, SECRET_KEY, ALGORITHM)

    assert decoded['test'] == claim['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):

    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalid'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


# '''

# Exercício 01

# Faça um teste para cobrir o cenário que levanta exception
# credentials_exception na autenticação caso o email não seja
# enviado via JWT. Ao olhar a cobertura de security.py você vai
# notar que esse contexto não está coberto.

# '''


def test_token_without_email(client):

    claim = {'sub': ''}

    token = create_access_token(claim)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_user_not_found(client):

    claim = {'sub': 'email'}

    token = create_access_token(claim)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
