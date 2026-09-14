import requests

def test_get_single_user():
    # 1. отправляем GET-запрос на https://reqres.in/api/users/2
    response = requests.get("https://reqres.in/api/users/2")

    # 2. проверяем код статуса (должен быть 200)
    assert response.status_code == 200

    # 3. тело ответа превращаем в словарь и достаём данные пользователя
    data = response.json()["data"]

    # 4. проверяем имя и фамилию
    assert data["first_name"] == "Janet"
    assert data["last_name"] == "Weaver"