from app.auth.auth_guard import get_librarian_active_user, get_admin_active_user
from fastapi import APIRouter, Depends, HTTPException, status
from app.users.models.models import UserNew, UserUpdate
from app.users.repositories.inject_repo import get_users_repository
from app.users.repositories.repository import IUsersRepository


users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_librarian_active_user)],
)


@users_router.get("/", dependencies=[Depends(get_admin_active_user)])
async def get_users(repo: IUsersRepository = Depends(get_users_repository)):
    """
    Get all users.
    """
    try:
        return repo.get_users()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


@users_router.get("/{user_id}")
async def get_user(
    user_id: str, repo: IUsersRepository = Depends(get_users_repository)
):
    """
    Get a user by ID.
    """
    try:
        return repo.get_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found: {str(e)}",
        )


@users_router.post("/")
async def create_user(
    user: UserNew, repo: IUsersRepository = Depends(get_users_repository)
):
    """
    Create a new user.
    """
    try:
        return repo.create_user(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}",
        )


@users_router.put("/")
async def update_user(
    user: UserUpdate, repo: IUsersRepository = Depends(get_users_repository)
):
    """
    Update an existing user.
    """
    try:
        return repo.update_user(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating user: {str(e)}",
        )


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: str, repo: IUsersRepository = Depends(get_users_repository)
):
    """
    Delete a user by ID.
    """
    try:
        return repo.delete_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found: {str(e)}",
        )


# @users_router.get("/loaners")
# async def get_loaners():
#     """
#     Get all loaners.
#     """
#     return {"message": "Get all loaners"}


# @users_router.post("/loaners/")
# async def create_loaner(loaner: dict):
#     """
#     Create a new loaner.
#     """
#     return {"message": "Create a new loaner", "loaner": loaner}


# @users_router.put("/loaners/{user_id}")
# async def update_loaner(user_id: str, loaner: dict):
#     """
#     Update an existing loaner.
#     """
#     return {"message": f"Update loaner with ID {user_id}", "loaner": loaner}


# @users_router.delete("/loaners/{user_id}")
# async def delete_loaner(user_id: str):
#     """
#     Delete a loaner by ID.
#     """
#     return {"message": f"Delete loaner with ID {user_id}"}


# @users_router.get("/loaners/{user_id}/loans")
# async def get_loaner_loans(user_id: str):
#     """
#     Get all loans for a loaner.
#     """
#     return {"message": f"Get all loans for loaner with ID {user_id}"}
