import requests

def test_user_not_found(base_url):
    # пользователя с таким id звыдомо нет
    response = requests.get(f"{base_url}/users/9999")

    assert response.status_code == 404

    # у dummyjson вмусте с кодом приходит и текст ошибки
    assert response.json()["message"] == "User with id '9999' not found"

def test_login_without_password(base_url):
    # отправляем логин без пароля
    response = requests.post(
        f"{base_url}/auth/login", json={"username": "emilys"})

    assert response.status_code == 400

    assert response.json()["message"] == "Username and password required"

def test_login_with_wrong_credentials(base_url):
    # логин есть, пароль неверный
    response = requests.post(
        f"{base_url}/auth/login",
        json={"username": "emilys", "password": "***"},
    )

    assert response.status_code == 400

    assert response.json()["message"] == "Invalid credentials"
