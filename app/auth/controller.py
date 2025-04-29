from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.models import AuthRegister
from app.auth.service import AuthService

import logging

logger = logging.getLogger("liboo.app.auth.controller")

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.post("/login")
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(),
):
    """
    Login a user.
    """
    try:
        user = service.login(
            username=credentials.username, password=credentials.password
        )
        return user
    except ValueError as e:
        logger.error(f"Error in get_user_from_credentials: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error in get_user_from_credentials: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.post("/register")
async def register(payload: AuthRegister, service: AuthService = Depends()):
    """
    Register a new user.
    """
    try:
        return service.register(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
