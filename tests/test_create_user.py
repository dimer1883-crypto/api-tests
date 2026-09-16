import requests

def test_create_user(base_url):
    payload = {"firstName": "Dmitry", "lastName": "Erakhtin"}

    response = requests.post(f"{base_url}/users/add", json=payload)

    # сервер должен ответить 201 Created
    assert response.status_code == 201

    body = response.json()
    assert body["firstName"] == "Dmitry"
    assert body["lastName"] == "Erakhtin"

    # id и createdAt сервер генерирует сам
    assert "id" in body