import requests

# контракт ответа: какие поля обязаны быть и какого они типа
USER_FIELDS = {
    "id": int,
    "firstName": str,
    "lastName": str,
    "email": str,
    "username": str,
    "age": int,
}

def test_user_response_structure(base_url):
    response = requests.get(f"{base_url}/users/1")

    assert response.status_code == 200

    data = response.json()

    for field, expected_type in USER_FIELDS.items():
        assert field in data, f"в ответе нет обязательного поля {field}"
        assert isinstance(data[field], expected_type), (
            f"поле {field}: ждали {expected_type.__name__}, "
            f"получили {type(data[field]).__name__}"
    )