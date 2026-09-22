import pytest
import requests
from jsonschema import ValidationError, validate


USER_SCHEMA = {
    "type": "object",
    "required": ["id", "firstName", "lastName", "age", "email", "hair"],
    "properties": {
        "id": {"type": "integer"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"},
        "hair": {
            "type": "object",
            "required": ["color"],
            "properties": {
                "color": {"type": "string"},
                "type": {"type": "string"},
            }
        }
    }
}


@pytest.mark.smoke
def test_user_matches_schema(base_url):
    response = requests.get(f"{base_url}/users/1")

    assert response.status_code == 200

    validate(instance=response.json(), schema=USER_SCHEMA)


def test_schema_catches_broken_data():
    broken_user = {
        "id": 1,
        "firstName": "Emily",
        "lastName": "Johnson",
        "age": "29",
        "email": "emily.johnson@x.dummyjson.com",
        "hair": {"color": "Brown", "type": "Curly"},
    }

    with pytest.raises(ValidationError):
        validate(instance=broken_user, schema=USER_SCHEMA)
