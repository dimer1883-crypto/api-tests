import requests

BASE_URL = "https://reqres.in/api"

def test_create_user():
    payload = {"name": "Dmitry", "job": "QA Engineer"}

    response = requests.post(f"{BASE_URL}/users", json=payload)
    # сервер должен ответить 201 Created
    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "Dmitry"
    assert body["job"] == "QA Engineer"

    # id и createdAt сервер генерирует сам — их значение неизвестно,
    # поэтому проверяем только то, что они появились в ответе
    assert "id" in body
    assert "createdAt" in body
