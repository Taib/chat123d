from fastapi.testclient import TestClient
import pytest


# Helper function to get auth token for a specific role
def get_auth_token(test_client: TestClient, role: str = "librarian") -> str:
    # role here is similar to username in the dummy database
    # Coming from the init data defined in db/sql/init_db.py
    username = role
    password = "chat123d"

    # Login to get token
    login_payload = {"username": username, "password": password}
    login_response = test_client.post("/auth/login", data=login_payload)
    assert login_response.status_code == 200, (
        f"Login failed for {role}: {login_response.text}"
    )
    token = login_response.json().get("access_token")
    assert token, f"No access token found for {role}"
    return token


# Fixture to get librarian token
@pytest.fixture(scope="module")
def librarian_token(test_client: TestClient):
    return get_auth_token(test_client, "librarian")


# Fixture to get admin token (if needed for specific tests, though librarian should suffice)
@pytest.fixture(scope="module")
def admin_token(test_client: TestClient):
    return get_auth_token(test_client, "admin")


# Fixture to get loaner token (for testing unauthorized access)
@pytest.fixture(scope="module")
def loaner_token(test_client: TestClient):
    return get_auth_token(test_client, "loaner1")
