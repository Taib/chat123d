from app.users.models.models import User, UserNew, UserUpdate, UserWithPassword


class IUsersRepository:
    """
    Interface for user repository.
    """

    def get_user(self, user_id: str) -> User | None:
        """
        Get a user by ID.
        """
        raise NotImplementedError

    def get_users(self) -> list[User]:
        """
        Get all users.
        """
        raise NotImplementedError

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by email.
        """
        raise NotImplementedError

    def get_user_with_password_by_email(self, email: str) -> UserWithPassword | None:
        """
        Get a user (with their password) by email.
        """
        raise NotImplementedError

    def get_user_with_password_by_username(
        self, username: str
    ) -> UserWithPassword | None:
        """
        Get a user (with their password) by username.
        """
        raise NotImplementedError

    def get_loaners(
        self,
    ) -> list[User]:
        """
        Get all loaners.
        """
        raise NotImplementedError

    def create_user(self, user: UserNew) -> User:
        """
        Create a new user.
        """
        raise NotImplementedError

    def update_user(self, user: UserUpdate) -> User:
        """
        Update an existing user.
        """
        raise NotImplementedError

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user by ID.
        """
        raise NotImplementedError
