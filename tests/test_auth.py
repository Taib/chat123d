from fastapi.testclient import TestClient


def test_register_and_login(test_client: TestClient):
    """Test registration endpoint"""
    register_payload = {
        "username": "testuser",
        "password": "testpass",
        "email": "test@test.com",
        "address": "123 Test St",
    }
    register_response = test_client.post("/auth/register", json=register_payload)
    print("Register response:", register_response.json())
    assert register_response.status_code == 200, register_response.text

    # Test login endpoint (adjust path and payload as needed)
    login_payload = {"username": "testuser", "password": "testpass"}
    login_response = test_client.post("/auth/login", data=login_payload)
    assert login_response.status_code == 200, login_response.text

    response_data = login_response.json()
    assert "access_token" in response_data


def test_duplicate_registration(test_client: TestClient):
    # Attempt to register the same user twice
    payload = {
        "username": "duplicateuser",
        "password": "duppass",
        "email": "duplicateuser@test.com",
        "address": "123 Test St",
    }
    # First registration should succeed
    response1 = test_client.post("/auth/register", json=payload)
    assert response1.status_code == 200, response1.text

    # Second registration should fail (adjust expected status code as needed)
    response2 = test_client.post("/auth/register", json=payload)
    assert response2.status_code in (400, 500), (
        response2.text
    )  # TODO: using 500 here for now, need to improve for better numbering


def test_invalid_login(test_client: TestClient):
    # Attempt login with non-existent user credentials
    payload = {"username": "nonexistent", "password": "wrongpass"}
    response = test_client.post("/auth/login", data=payload)
    # Assuming invalid credentials return 401 (adjust as needed)
    assert response.status_code == 401, response.text


def test_access_protected_route(test_client: TestClient):
    # Register and login to obtain an access token for a protected route
    register_payload = {
        "username": "protecteduser",
        "password": "protectedpass",
        "email": "protecteduser@test.com",
        "address": "123 Test St",
    }
    test_client.post("/auth/register", json=register_payload)
    login_response = test_client.post("/auth/login", data=register_payload)
    token = login_response.json().get("access_token")
    assert token

    # Now access a protected route (adjust the route and headers as needed)
    headers = {"Authorization": f"Bearer {token}"}
    protected_response = test_client.get("/books", headers=headers)
    assert protected_response.status_code == 200, protected_response.text
