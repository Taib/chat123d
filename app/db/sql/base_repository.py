from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.sql.base_entity import BaseEntity

from typing import TypeVar, Generic

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(Generic[T]):
    """Base class for our SQLAlchemy repositories."""

    def __init__(self, entity_class: T, session: Session):
        self.session = session
        self.entity_class = entity_class

    def create(self, entity) -> T:
        """Add an entity to the session, and commit."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def query(self) -> list[T]:
        """Query the database for entities of a given class."""
        return self.session.query(self.entity_class)

    def find_by_id(self, entity_id: str) -> T | None:
        """Find an entity by ID."""
        stmt = select(self.entity_class).where(self.entity_class.id == entity_id)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def update(self, entity_id: str, entity: dict) -> T | None:
        """Update an entity by ID."""

        # just to be sure we don't update these fields
        entity.pop("created_at", None)
        entity.pop("updated_at", None)

        existing_entity = self.find_by_id(entity_id)
        if existing_entity:
            for key, value in entity.items():
                setattr(existing_entity, key, value)
            self.session.commit()
            self.session.refresh(existing_entity)
            return existing_entity

    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID."""
        existing_entity = self.find_by_id(entity_id)
        if existing_entity:
            self.session.delete(existing_entity)
            self.session.commit()
            return True
        return False
