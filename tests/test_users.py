import requests

def test_get_single_user(base_url):
    response = requests.get(f"{base_url}/users/2")

    assert response.status_code == 200

    data = response.json()["data"]
    assert data["first_name"] == "Janet"
    assert data["last_name"] == "Weaver"