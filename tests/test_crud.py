import pytest
import requests


@pytest.fixture
def created_user(base_url):
    payload = {"firstName": "Dmitry", "lastName": "Erakhtin"}

    response = requests.post(f"{base_url}/users/add", json=payload)
    assert response.status_code == 201

    user = response.json()
    print(f"\nподготовка: создан пользователь с id {user['id']}")

    yield user

    delete_response = requests.delete(f"{base_url}/users/{user['id']}")
    print(
        f"уборка: удаляю пользователя {user['id']}, ответ {delete_response.status_code}")

    # dummyjson не хранит созданные объекты, поэтому на удаление отвечает 404.
    # Уборка не должна ронять прогон, если объекта уже нет.
    assert delete_response.status_code in (200, 404)


def test_created_user_has_id(created_user):
    assert created_user["id"] > 0


def test_created_user_has_expected_fields(created_user):
    assert created_user["firstName"] == "Dmitry"
    assert created_user["lastName"] == "Erakhtin"