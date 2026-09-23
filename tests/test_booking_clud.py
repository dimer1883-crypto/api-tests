import pytest
import requests

BOOKING_PAYLOAD = {
    "firstname": "Dmitry",
    "lastname": "Erakhtin",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-10-01", "checkout": "2026-10-05"},
    "additionalneeds": "Breakfast",
}

@pytest.fixture(scope="session")
def api_token(booking_url):
    response = requests.post(
        f"{booking_url}/auth",
        json={"username": "admin", "password": "password123"},
    )
    assert response.status_code == 200

    token = response.json()["token"]
    assert token, "сервер не выдал токен"

    return token

@pytest.fixture
def created_booking(booking_url, api_token):
    response = requests.post(f"{booking_url}/booking", json=BOOKING_PAYLOAD)
    assert response.status_code == 200

    booking_id = response.json()["bookingid"]
    print(f"\nподготовка: создана бронь {booking_id}")

    yield booking_id

    delete_response = requests.delete(
        f"{booking_url}/booking/{booking_id}", cookies={"token": api_token}
    )
    print(f"уборка: бронь {booking_id} удалена, ответ {delete_response.status_code}")

def test_created_booking_is_stored(booking_url, created_booking):
    response = requests.get(f"{booking_url}/booking/{created_booking}")

    assert response.status_code == 200

    booking = response.json()
    assert booking["firstname"] == BOOKING_PAYLOAD["firstname"]
    assert booking["lastname"] == BOOKING_PAYLOAD["lastname"]
    assert booking["totalprice"] == BOOKING_PAYLOAD["totalprice"]
    assert booking["bookingdates"] == BOOKING_PAYLOAD["bookingdates"]

def test_update_booking_changes_data(booking_url, api_token, created_booking):
    updated = {**BOOKING_PAYLOAD, "firstname": "Dmitry-updated", "totalprice": 999}

    response = requests.put(
        f"{booking_url}/booking/{created_booking}",
        json=updated,
        cookies={"token": api_token},
    )

    assert response.status_code == 200
    assert response.json()["firstname"] == "Dmitry-updated"

    check = requests.get(f"{booking_url}/booking/{created_booking}")
    assert check.json()["firstname"] == "Dmitry-updated"
    assert check.json()["totalprice"] == 999

def test_delete_booking_removes_it(booking_url, api_token):
    create_response = requests.post(f"{booking_url}/booking", json=BOOKING_PAYLOAD)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    delete_response = requests.delete(
        f"{booking_url}/booking/{booking_id}", cookies={"token": api_token}
    )
    assert delete_response.status_code == 201

    check = requests.get(f"{booking_url}/booking/{booking_id}")
    assert check.status_code == 404

def test_update_without_token_is_forbidden(booking_url, created_booking):
    response = requests.put(
        f"{booking_url}/booking/{created_booking}",
        json=BOOKING_PAYLOAD,
    )

    assert response.status_code == 403

def test_get_unknown_booking_returns_404(booking_url):
    response = requests.get(f"{booking_url}/booking/99999999")

    assert response.status_code == 404