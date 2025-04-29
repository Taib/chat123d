from app.db.sql.utils import pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from app.users.models.models import User, UserNew, UserUpdate, UserWithPassword
from sqlalchemy.orm import Session
from app.db.sql.base_repository import BaseRepository
from app.users.entities.entity import UserEntity
from app.users.repositories.repository import IUsersRepository


import logging

logger = logging.getLogger("liboo.app.users.repository")


def user_entity_to_model(entity: UserEntity) -> User:
    """
    Convert a UserEntity to a model.
    """
    return sqlalchemy_to_pydantic(entity, User, exclude={"password"})


def user_model_to_entity(model: User) -> UserEntity:
    """
    Convert a model to a UserEntity.
    """
    return pydantic_to_sqlalchemy(model, UserEntity, exclude_unset=True)


class SQLUsersRepository(BaseRepository[UserEntity], IUsersRepository):
    def __init__(self, session: Session):
        super().__init__(UserEntity, session)

    def get_user(self, user_id: str) -> User | None:
        """
        Get a user by ID.
        """
        user = self.find_by_id(user_id)
        if user:
            return user_entity_to_model(user)
        return None

    def get_users(self) -> User | None:
        """
        Get all users.
        """
        users = self.query().all()
        return [user_entity_to_model(user) for user in users]

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by email.
        """
        user = self.query().filter_by(email=email).first()
        if user:
            return user_entity_to_model(user)
        return None

    def get_user_with_password_by_email(self, email: str) -> UserWithPassword | None:
        """
        Get a user (with their password) by email.
        """
        user = self.query().filter_by(email=email).first()
        if user:
            model = user_entity_to_model(user).model_dump()
            model["password"] = user.password
            return UserWithPassword(**model)
        return None

    def get_user_with_password_by_username(
        self, username: str
    ) -> UserWithPassword | None:
        """
        Get a user (with their password) by username.
        """
        user = self.query().filter_by(username=username).first()
        if user:
            model = user_entity_to_model(user).model_dump()
            model["password"] = user.password
            return UserWithPassword(**model)
        return None

    def get_loaners(self) -> list[User]:
        """
        Get all loaners.
        """
        results = self.query().filter_by(role="loaner").all()
        return [user_entity_to_model(user) for user in results]

    def create_user(self, user: UserNew) -> User:
        """
        Create a new user.
        """

        try:
            entity = user_model_to_entity(user)
        except Exception as e:
            logger.error(f"Error converting user model to entity: {e}")
            raise ValueError("invalid-user-data")
        try:
            result = self.create(entity)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise ValueError("user-creation-failed")
        return user_entity_to_model(result)

    def update_user(self, user: UserUpdate) -> User:
        """
        Update an existing user.
        """
        self.update(user.id, user.model_dump(exclude_unset=True))
        return self.find_by_id(user.id)

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user by ID.
        """
        return self.delete(user_id)
