import pytest
import requests

@pytest.mark.parametrize(
    "user_id, expected_first_name, expected_last_name",
    [
        (1, "Emily", "Johnson"),
        (2, "Michael", "Williams"),
        (3, "Sophia", "Brown"),
        (4, "James", "Davis"),
    ],
)
def test_get_user_by_id(base_url, user_id, expected_first_name, expected_last_name):
    response = requests.get(f"{base_url}/users/{user_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["firstName"] == expected_first_name
    assert data["lastName"] == expected_last_name