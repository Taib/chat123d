from fastapi.testclient import TestClient
import pytest


# Helper to create an author and return its ID
def create_test_author(test_client: TestClient, token: str) -> str:
    author_payload = {"name": "Test Author for Books", "bio": "Bio for book tests"}
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post("/authors/", json=author_payload, headers=headers)
    assert response.status_code == 201, f"Failed to create author: {response.text}"
    return response.json()["id"]


@pytest.fixture(scope="module")
def test_author_id(test_client: TestClient, librarian_token: str) -> str:
    """Fixture to provide a valid author_id for book tests."""
    return create_test_author(test_client, librarian_token)


def test_create_book_unauthorized(
    test_client: TestClient, loaner_token: str, test_author_id: str
):
    """Test creating a book without proper authorization (loaner)."""
    headers = {"Authorization": f"Bearer {loaner_token}"}
    payload = {
        "title": "Unauthorized Book",
        "author_id": test_author_id,
        "year": 2024,
        "isbn": "978-1234567890",
    }
    response = test_client.post("/books/", json=payload, headers=headers)
    assert response.status_code == 403, response.text  # Forbidden


def test_create_and_get_book(
    test_client: TestClient,
    librarian_token: str,
    test_author_id: str,
    loaner_token: str,
):
    """Test creating a new book and retrieving it."""
    headers = {"Authorization": f"Bearer {librarian_token}"}
    payload = {
        "title": "Test Book One",
        "author_id": test_author_id,
        "year": 2023,
        "isbn": "978-0987654321",
        "description": "A test book description.",
    }

    # Create Book
    create_response = test_client.post("/books/", json=payload, headers=headers)
    assert create_response.status_code == 201, create_response.text
    created_book = create_response.json()
    assert created_book["title"] == payload["title"]
    assert created_book["author_id"] == payload["author_id"]
    assert created_book["year"] == payload["year"]
    assert created_book["isbn"] == payload["isbn"]
    assert "id" in created_book
    book_id = created_book["id"]

    # Get Book by ID (requires librarian/admin)
    get_response = test_client.get(f"/books/{book_id}", headers=headers)
    assert get_response.status_code == 200, get_response.text
    retrieved_book = get_response.json()
    assert retrieved_book["id"] == book_id
    assert retrieved_book["title"] == payload["title"]

    # Try getting book with loaner token (should fail as endpoint requires librarian)
    loaner_headers = {"Authorization": f"Bearer {loaner_token}"}
    get_loaner_response = test_client.get(f"/books/{book_id}", headers=loaner_headers)
    assert get_loaner_response.status_code == 403, get_loaner_response.text  # Forbidden

    # Get non-existent book
    get_nonexistent_response = test_client.get("/books/nonexistent_id", headers=headers)
    assert get_nonexistent_response.status_code == 404, get_nonexistent_response.text


def test_query_books(
    test_client: TestClient,
    librarian_token: str,
    loaner_token: str,
    test_author_id: str,
):
    """Test querying books with and without filters, accessible by any authenticated user."""
    lib_headers = {"Authorization": f"Bearer {librarian_token}"}
    loaner_headers = {"Authorization": f"Bearer {loaner_token}"}

    # Ensure some books exist
    test_client.post(
        "/books/",
        json={
            "title": "Query Book Alpha",
            "author_id": test_author_id,
            "year": 2022,
            "isbn": "978-1111111111",
        },
        headers=lib_headers,
    )
    test_client.post(
        "/books/",
        json={
            "title": "Query Book Beta",
            "author_id": test_author_id,
            "year": 2021,
            "isbn": "978-2222222222",
        },
        headers=lib_headers,
    )

    # Query all books (loaner)
    get_all_loaner_response = test_client.get("/books/", headers=loaner_headers)
    assert get_all_loaner_response.status_code == 200, get_all_loaner_response.text
    books_list_loaner = get_all_loaner_response.json()
    assert isinstance(books_list_loaner, list)
    assert len(books_list_loaner) >= 2

    # Query all books (librarian)
    get_all_lib_response = test_client.get("/books/", headers=lib_headers)
    assert get_all_lib_response.status_code == 200, get_all_lib_response.text
    books_list_lib = get_all_lib_response.json()
    assert isinstance(books_list_lib, list)
    assert len(books_list_lib) >= 2

    # Query with a specific term (librarian)
    query_response = test_client.get("/books/?query=Alpha", headers=lib_headers)
    assert query_response.status_code == 200, query_response.text
    query_results = query_response.json()
    assert isinstance(query_results, list)
    assert len(query_results) > 0
    assert any(book["title"] == "Query Book Alpha" for book in query_results)
    assert not any(book["title"] == "Query Book Beta" for book in query_results)

    # Query with ordering (default is year descending)
    get_ordered_response = test_client.get("/books/", headers=lib_headers)
    ordered_books = get_ordered_response.json()
    assert (
        ordered_books[0]["year"] >= ordered_books[1]["year"]
    )  # Assuming at least 2 books


def test_update_book(
    test_client: TestClient,
    librarian_token: str,
    test_author_id: str,
    loaner_token: str,
):
    """Test updating an existing book."""
    headers = {"Authorization": f"Bearer {librarian_token}"}
    # Create a book first
    create_payload = {
        "title": "Book To Update",
        "author_id": test_author_id,
        "year": 2020,
        "isbn": "978-3333333333",
    }
    create_response = test_client.post("/books/", json=create_payload, headers=headers)
    assert create_response.status_code == 201
    book_id = create_response.json()["id"]

    # Update the book
    update_payload = {
        "id": book_id,
        "title": "Updated Book Title",
        "year": 2021,
        "status": "loaned",  # Example update
    }
    update_response = test_client.put("/books/", json=update_payload, headers=headers)
    assert update_response.status_code == 200, update_response.text
    updated_book = update_response.json()
    assert updated_book["id"] == book_id
    assert updated_book["title"] == update_payload["title"]
    assert updated_book["year"] == update_payload["year"]
    assert updated_book["status"] == update_payload["status"]

    # Verify the update by getting the book again
    get_response = test_client.get(f"/books/{book_id}", headers=headers)
    assert get_response.status_code == 200
    retrieved_book = get_response.json()
    assert retrieved_book["title"] == update_payload["title"]
    assert retrieved_book["status"] == update_payload["status"]

    # Try updating with loaner token (should fail)
    loaner_headers = {"Authorization": f"Bearer {loaner_token}"}
    update_loaner_response = test_client.put(
        "/books/", json=update_payload, headers=loaner_headers
    )
    assert update_loaner_response.status_code == 403, (
        update_loaner_response.text
    )  # Forbidden


def test_delete_book(
    test_client: TestClient,
    librarian_token: str,
    test_author_id: str,
    loaner_token: str,
):
    """Test deleting a book."""
    headers = {"Authorization": f"Bearer {librarian_token}"}
    # Create a book to delete
    create_payload = {
        "title": "Book To Delete",
        "author_id": test_author_id,
        "year": 2019,
        "isbn": "978-4444444444",
    }
    create_response = test_client.post("/books/", json=create_payload, headers=headers)
    assert create_response.status_code == 201
    book_id = create_response.json()["id"]

    # Delete the book
    delete_response = test_client.delete(f"/books/{book_id}", headers=headers)
    assert delete_response.status_code == 204, delete_response.text  # No Content

    # Verify deletion by trying to get the book
    get_response = test_client.get(f"/books/{book_id}", headers=headers)
    assert get_response.status_code == 404, get_response.text  # Not Found

    # Try deleting a non-existent book
    delete_nonexistent_response = test_client.delete(
        "/books/nonexistent_id_del", headers=headers
    )
    assert delete_nonexistent_response.status_code == 404, (
        delete_nonexistent_response.text
    )

    # Try deleting with loaner token (should fail)
    loaner_headers = {"Authorization": f"Bearer {loaner_token}"}
    # Recreate the book to test deletion attempt
    create_response = test_client.post("/books/", json=create_payload, headers=headers)
    book_id_recreate = create_response.json()["id"]
    delete_loaner_response = test_client.delete(
        f"/books/{book_id_recreate}", headers=loaner_headers
    )
    assert delete_loaner_response.status_code == 403, (
        delete_loaner_response.text
    )  # Forbidden
