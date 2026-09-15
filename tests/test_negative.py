import requests

def test_user_not_found(base_url):
    # запрашиваем пользователя с заведомо несуществующим id
    response = requests.get(f"{base_url}/users/23")

    # сервер обязан честно ответить 404 Not Found
    assert response.status_code == 404

def test_login_without_password(base_url):
    # отправляем логин без пароля
    response = requests.post(f"{base_url}/login", json={"email": "dmitry@test.ru"})

    assert response.status_code == 400

    body = response.json()
    assert body["error"] == "Missing password"

def test_login_with_wrong_credentials(base_url):
    # логин есть, пароль неверный
    response = requests.post(
        f"{base_url}/login",
        json={"email": "dmitry@test.ru", "password": "wrong"},
    )

    assert response.status_code == 400

    assert response.json()["error"] == "user not found"