from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from app.auth.utils import decode_session_token
from app.users.models.models import User
from app.users.repositories.inject_repo import get_users_repository
from app.users.repositories.repository import IUsersRepository


import logging

logger = logging.getLogger("liboo.app.admin_dashboard.repository_dashboard")

oauth2_password = OAuth2PasswordBearer(auto_error=False, tokenUrl="/auth/login")


async def get_user_from_token(
    token: Annotated[str | None, Depends(oauth2_password)] = None,
    users_repo: IUsersRepository = Depends(get_users_repository),
) -> User | None:
    if token is None:
        return None
    try:
        payload = decode_session_token(token)
        logger.debug("[get_user_from_token] payload: ", payload)
        user = users_repo.get_user(payload["sub"])
        if (
            user is None
            or user.role != payload["role"]
            or user.username != payload["username"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    token_user: Annotated[User, Depends(get_user_from_token)],
) -> User:
    return token_user


async def get_librarian_active_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.role not in ["librarian", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user


async def get_admin_active_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user
