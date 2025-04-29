from fastapi import Depends
from app.auth.models import AuthRegister, AuthSession, TokenData
from app.auth.utils import create_session_token, pwd_context
from app.db.guid import guid_gen
from app.users.models.models import User, UserNew
from app.users.repositories.inject_repo import get_users_repository
from app.users.repositories.repository import IUsersRepository


def hash_password(password: str) -> str:
    """
    Hash the password.
    """
    return pwd_context.hash(password)


def validate_password(hashed_password: str, plain_password: str) -> bool:
    """
    Validate the password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def build_user_session(user: User) -> AuthSession:
    """
    Build a user session.
    """
    return AuthSession(
        access_token=create_session_token(user),
        refresh_token=guid_gen(length=32)(),
        user=TokenData(
            id=user.id,
            email=user.email,
            username=user.username,
            address=user.address,
            max_week_loans=user.max_week_loans,
            role=user.role,
        ),
    )


class AuthService:
    def __init__(self, users_repo: IUsersRepository = Depends(get_users_repository)):
        self.users_repo = users_repo

    def login(
        self, *, email: str | None = None, username: str | None = None, password: str
    ) -> AuthSession:
        if email:
            user = self.users_repo.get_user_with_password_by_email(email)
        elif username:
            user = self.users_repo.get_user_with_password_by_username(username)

        if not user:
            raise ValueError("invalid-credentials")
        if validate_password(user.password, password):
            return build_user_session(user)
        raise ValueError("invalid-credentials")

    def register(self, payload: AuthRegister):
        new_user = UserNew(
            email=payload.email,
            username=payload.username,
            role="loaner",
            password=hash_password(payload.password),
            address=payload.address,
        )
        user = self.users_repo.create_user(new_user)
        return build_user_session(user)
