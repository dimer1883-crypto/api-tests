import pytest
import requests

@pytest.mark.parametrize(
    "user_id, expected_first_name, expected_last_name",
    [
        (1, "George", "Bluth"),
        (2, "Janet", "Weaver"),
        (3, "Emma", "Wong"),
        (4, "Eve", "Holt"),
    ],
)
def test_get_user_by_id(base_url, user_id, expected_first_name, expected_last_name):
    response = requests.get(f"{base_url}/users/{user_id}")

    assert response.status_code == 200

    data = response.json()["data"]
    assert data["id"] == user_id
    assert data["first_name"] == expected_first_name
    assert data["last_name"] == expected_last_name