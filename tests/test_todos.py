from http import HTTPStatus

import factory.base
import factory.fuzzy
import pytest

from fastapi_study_project.models import Todo, TodoState


class TodoFactory(factory.base.Factory):
    class Meta:
        model = Todo

    title = factory.faker.Faker('text')
    description = factory.faker.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    is_urgent = factory.faker.Faker('boolean')
    user_id = 1


def test_create_todo(client, token):
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test todo',
            'description': 'a good description',
            'state': 'todo',
            'is_urgent': False,
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'test todo',
        'description': 'a good description',
        'state': 'todo',
        'is_urgent': False,
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):

    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):

    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    query_str = '?offset=1&limit=2'

    response = client.get(
        f'/todos/{query_str}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, client, user, token
):

    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    await session.commit()

    query_str = '?title=Test todo 1'

    response = client.get(
        f'/todos/{query_str}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session, client, user, token
):

    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description='Test todo 1')
    )
    await session.commit()

    query_str = '?description=Test todo 1'

    response = client.get(
        f'/todos/{query_str}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session, client, user, token
):

    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, state='done'))
    await session.commit()

    query_str = '?state=done'

    response = client.get(
        f'/todos/{query_str}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_delete_todo_not_found(client, token):

    response = client.delete(
        '/todos/100', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_delete_todo(client, session, user, token):

    session.add(TodoFactory(user_id=user.id))
    await session.commit()

    response = client.delete(
        '/todos/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


def test_patch_todo_not_found(client, token):

    response = client.patch(
        '/todos/100', headers={'Authorization': f'Bearer {token}'}, json={}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo(client, session, user, token):

    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'description': 'test'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['description'] == 'test'
