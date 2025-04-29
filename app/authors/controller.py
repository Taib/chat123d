from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_guard import get_librarian_active_user
from app.authors.repository import AuthorRepository
from app.authors.models import AuthorCreate, AuthorUpdate


authors_router = APIRouter(
    prefix="/authors",
    tags=["authors"],
    dependencies=[Depends(get_librarian_active_user)],
)


@authors_router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_authors(repo: AuthorRepository = Depends()):
    """
    Get all authors.
    """
    try:
        return repo.get_all_authors()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@authors_router.get(
    "/{author_id}",
    status_code=status.HTTP_200_OK,
)
async def get_author(
    author_id: str,
    repo: AuthorRepository = Depends(),
):
    """
    Get a author by ID.
    """
    try:
        author = repo.get_author(author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found",
            )
        return author
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@authors_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_author(
    author: AuthorCreate,
    repo: AuthorRepository = Depends(),
):
    """
    Create a new author.
    """
    try:
        return repo.create_author(author)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@authors_router.put(
    "/",
    status_code=status.HTTP_200_OK,
)
async def update_author(
    author: AuthorUpdate,
    repo: AuthorRepository = Depends(),
):
    """
    Update a author.
    """
    try:
        return repo.update_author(author)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@authors_router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_author(
    author_id: str,
    repo: AuthorRepository = Depends(),
):
    """
    Delete a author.
    """
    try:
        result = repo.delete_author(author_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
