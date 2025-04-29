from typing import Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

# Create type variables for generic typing
T = TypeVar("T", bound=BaseModel)
S = TypeVar("S", bound=DeclarativeBase)


def sqlalchemy_to_pydantic(
    sqlalchemy_entity: S,
    pydantic_model: Type[T],
    exclude: set[str] = None,
    relationship_converters: dict[str, any] = None,
) -> T:
    """
    Convert a SQLAlchemy entity to a Pydantic model instance.

    Args:
        sqlalchemy_entity: SQLAlchemy model instance to convert
        pydantic_model: Pydantic model class to create
        exclude: Set of field names to exclude from conversion
        relationship_converters: Dict mapping relationship names to conversion functions

    Returns:
        Instance of the Pydantic model
    """
    exclude = exclude or set()
    relationship_converters = relationship_converters or {}

    # Get all column values
    entity_data = {
        column.name: getattr(sqlalchemy_entity, column.name)
        for column in sqlalchemy_entity.__table__.columns
        if column.name not in exclude
    }

    # Handle relationships
    for rel_name, converter in relationship_converters.items():
        if hasattr(sqlalchemy_entity, rel_name):
            rel_value = getattr(sqlalchemy_entity, rel_name)
            if rel_value is None:
                entity_data[rel_name] = None
            elif isinstance(rel_value, list):
                entity_data[rel_name] = [converter(item) for item in rel_value]
            else:
                entity_data[rel_name] = converter(rel_value)

    return pydantic_model(**entity_data)


def pydantic_to_sqlalchemy(
    pydantic_model: T, sqlalchemy_model: Type[S], exclude_unset: bool = True
) -> S:
    """
    Convert a Pydantic model to a SQLAlchemy model instance.

    Args:
        pydantic_model: Instance of Pydantic model to convert
        sqlalchemy_model: SQLAlchemy model class to create
        exclude_unset: Whether to exclude fields not set in the Pydantic model

    Returns:
        Instance of the SQLAlchemy model
    """
    # Get the model data as dict
    model_data = pydantic_model.model_dump(exclude_unset=exclude_unset)

    # Filter out any fields that don't exist in SQLAlchemy model
    sa_fields = {column.name for column in sqlalchemy_model.__table__.columns}
    filtered_data = {
        key: value for key, value in model_data.items() if key in sa_fields
    }

    return sqlalchemy_model(**filtered_data)
