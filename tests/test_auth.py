import os

import pytest
import requests

GITHUB_API = "https://api.github.com"


@pytest.fixture(scope="session")
def github_token():
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        pytest.skip(
            "переменная GITHUB_TOKEN не задана - тесты GitHub пропущены")

    return token


@pytest.fixture(scope="session")
def github_headers(github_token):
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }


def test_get_my_profile(github_headers):
    response = requests.get(f"{GITHUB_API}/user", headers=github_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["login"] == "dimer1883-crypto"


def test_request_without_token():
    response = requests.get(f"{GITHUB_API}/user")

    assert response.status_code == 401

    assert response.json()["message"] == "Requires authentication"


def test_github_user_not_found():
    response = requests.get(
        f"{GITHUB_API}/users/etot-polzovatel-tochno-ne-sushchestvuet-123"
    )

    assert response.status_code == 404

    assert response.json()["message"] == "Not Found"
