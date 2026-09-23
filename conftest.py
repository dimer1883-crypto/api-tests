import pytest

@pytest.fixture(scope="session")
def base_url():
    return "https://dummyjson.com"


@pytest.fixture(scope="session")
def booking_url():
    return "https://restful-booker.herokuapp.com"