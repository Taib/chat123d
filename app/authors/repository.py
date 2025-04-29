from fastapi import Depends
from sqlalchemy.orm import Session
from app.authors.entities import AuthorEntity
from app.db.sql.base_repository import BaseRepository
from app.db.sql.utils import pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from app.authors.models import Author, AuthorCreate, AuthorUpdate
from app.db.get_db import get_db
from app.users.models.models import User
from app.auth.auth_guard import get_current_active_user

import logging

logger = logging.getLogger("liboo.app.authors.repository")


def author_entity_to_model(entity: AuthorEntity) -> Author:
    """
    Convert a AuthorEntity to a model.
    """
    return sqlalchemy_to_pydantic(entity, Author, exclude={"password"})


def author_model_to_entity(model: Author) -> AuthorEntity:
    """
    Convert a model to a AuthorEntity.
    """
    return pydantic_to_sqlalchemy(model, AuthorEntity, exclude_unset=True)


class AuthorRepository(BaseRepository[AuthorEntity]):
    def __init__(
        self,
        session: Session = Depends(get_db),
        user: User = Depends(get_current_active_user),
    ):
        super().__init__(AuthorEntity, session)
        self.user = user

    def get_author(self, author_id: str) -> Author | None:
        """
        Get a author by ID.
        """
        author = self.find_by_id(author_id)
        if author:
            return author_entity_to_model(author)
        return None

    def get_all_authors(self) -> list[Author]:
        """
        Get all authors.
        """
        authors = self.query().all()
        return [author_entity_to_model(author) for author in authors]

    def get_author_by_name(self, name: str) -> Author | None:
        """
        Get a author by name.
        """
        author = self.query().filter_by(name=name).first()
        if author:
            return author_entity_to_model(author)
        return None

    def create_author(self, author: AuthorCreate) -> Author:
        """
        Create a new author.
        """

        try:
            entity = author_model_to_entity(author)
            entity.created_by = self.user.id
            entity.updated_by = self.user.id
            result = self.create(entity)
            return author_entity_to_model(result)
        except Exception as e:
            logger.error(f"Error creating author: {e}")
            raise ValueError("author-creation-failed")

    def update_author(self, author: AuthorUpdate) -> Author:
        """
        Update an existing author.
        """
        dump = author.model_dump(exclude_unset=True)
        dump["updated_by"] = self.user.id
        self.update(author.id, dump)
        return self.find_by_id(author.id)

    def delete_author(self, author_id: str) -> bool:
        """
        Delete a author by ID.
        """
        return self.delete(author_id)
