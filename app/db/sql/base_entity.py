import datetime
import enum
from typing import Annotated
import typing
from sqlalchemy import TIMESTAMP, func
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column

# To avoid writing the same code for each entity, am using these annotated types
# for the created_at and updated_at fields.
type_created_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]
type_updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        nullable=False,
        server_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP(),
    ),
]


class BaseEntity(DeclarativeBase):
    """Base class for all SQLAlchemy entities."""

    type_annotation_map = {
        # just mapping any datetime type to a SQLAlchemy TIMESTAMP
        datetime.datetime: TIMESTAMP(timezone=True),
        # doing the same for literal types
        typing.Literal: sqlalchemy.Enum(enum.Enum),
    }
