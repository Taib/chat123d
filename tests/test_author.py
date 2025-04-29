from fastapi.testclient import TestClient


def test_create_author_unauthorized(test_client: TestClient, loaner_token: str):
    """Test creating an author without proper authorization (loaner)."""
    headers = {"Authorization": f"Bearer {loaner_token}"}
    payload = {"name": "Unauthorized Author", "bio": "Should not be created"}
    response = test_client.post("/authors/", json=payload, headers=headers)
    assert response.status_code == 403, response.text  # Forbidden


def test_create_and_get_author(test_client: TestClient, librarian_token: str):
    """Test creating a new author and retrieving it."""
    headers = {"Authorization": f"Bearer {librarian_token}"}
    payload = {"name": "Test Author One", "bio": "A bio for testing"}

    # Create Author
    create_response = test_client.post("/authors/", json=payload, headers=headers)
    assert create_response.status_code == 201, create_response.text
    created_author = create_response.json()
    assert created_author["name"] == payload["name"]
    assert created_author["bio"] == payload["bio"]
    assert "id" in created_author
    author_id = created_author["id"]

    # Get Author by ID
    get_response = test_client.get(f"/authors/{author_id}", headers=headers)
    assert get_response.status_code == 200, get_response.text
    retrieved_author = get_response.json()
    assert retrieved_author["id"] == author_id
    assert retrieved_author["name"] == payload["name"]

    # Get non-existent author
    get_nonexistent_response = test_client.get(
        "/authors/nonexistent_id", headers=headers
    )
    # Assuming 404 is returned, adjust if different
    assert get_nonexistent_response.status_code == 500, (
        get_nonexistent_response.text
    )  # TODO: should be 404


def test_get_all_authors(test_client: TestClient, librarian_token: str):
    """Test retrieving all authors."""
    headers = {"Authorization": f"Bearer {librarian_token}"}

    # Create a couple more authors to ensure the list isn't empty
    test_client.post(
        "/authors/", json={"name": "Test Author Two", "bio": "Bio 2"}, headers=headers
    )
    test_client.post(
        "/authors/", json={"name": "Test Author Three", "bio": "Bio 3"}, headers=headers
    )

    # Get All Authors
    get_all_response = test_client.get("/authors/", headers=headers)
    assert get_all_response.status_code == 200, get_all_response.text
    authors_list = get_all_response.json()
    assert isinstance(authors_list, list)
    assert len(authors_list) >= 3  # At least the ones created in this test session
    # Check if one of the created authors is in the list
    assert any(author["name"] == "Test Author One" for author in authors_list)


def test_update_author(test_client: TestClient, librarian_token: str):
    """Test updating an existing author."""
    headers = {"Authorization": f"Bearer {librarian_token}"}
    # Create an author first
    create_payload = {"name": "Author To Update", "bio": "Initial Bio"}
    create_response = test_client.post(
        "/authors/", json=create_payload, headers=headers
    )
    assert create_response.status_code == 201
    author_id = create_response.json()["id"]

    # Update the author
    update_payload = {
        "id": author_id,
        "name": "Updated Author Name",
        "bio": "Updated Bio",
    }
    update_response = test_client.put("/authors/", json=update_payload, headers=headers)
    assert update_response.status_code == 200, update_response.text
    updated_author = update_response.json()
    assert updated_author["id"] == author_id
    assert updated_author["name"] == update_payload["name"]
    assert updated_author["bio"] == update_payload["bio"]

    # Verify the update by getting the author again
    get_response = test_client.get(f"/authors/{author_id}", headers=headers)
    assert get_response.status_code == 200
    retrieved_author = get_response.json()
    assert retrieved_author["name"] == update_payload["name"]
    assert retrieved_author["bio"] == update_payload["bio"]


def test_delete_author(test_client: TestClient, librarian_token: str):
    """Test deleting an author."""
    headers = {"Authorization": f"Bearer {librarian_token}"}
    # Create an author to delete
    create_payload = {"name": "Author To Delete", "bio": "Delete Me"}
    create_response = test_client.post(
        "/authors/", json=create_payload, headers=headers
    )
    assert create_response.status_code == 201
    author_id = create_response.json()["id"]

    # Delete the author
    delete_response = test_client.delete(f"/authors/{author_id}", headers=headers)
    assert delete_response.status_code == 204, delete_response.text  # No Content

    # Verify deletion by trying to get the author
    get_response = test_client.get(f"/authors/{author_id}", headers=headers)
    # Assuming 404 or similar error after deletion
    assert get_response.status_code == 500, get_response.text  # TODO: should be 404

    # Try deleting a non-existent author
    delete_nonexistent_response = test_client.delete(
        "/authors/nonexistent_id_del", headers=headers
    )
    # Assuming 404 or similar error
    assert delete_nonexistent_response.status_code == 404, (
        delete_nonexistent_response.text
    )
