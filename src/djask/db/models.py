from __future__ import annotations

import datetime as dt
from typing import Any
from typing import Iterable

import sqlalchemy as sa
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm.collections import InstrumentedList


class BaseModel:
    """Provide a base model class which has no pre-defined columns.

    ..versionadded:: 0.4.1
    """

    def to_dict(self, exclude: Iterable[str] = None) -> dict[str, Any]:
        """Convert Model to dict.

        .. versionadded:: 0.4.1
        """
        from ..auth.abstract import AbstractUser

        result = {}
        for k, v in self.__dict__.items():
            conditions = (
                k.startswith("_"),
                isinstance(self, AbstractUser) and k == "password_hash",
                exclude is not None and k in exclude,
            )
            if any(conditions):
                continue
            result[k] = v
        for k, v in inspect(type(self)).relationships.items():
            if exclude is None or k not in exclude:
                attribute = self.__getattribute__(k)
                if isinstance(attribute, InstrumentedList):  # pragma: no cover
                    result[k] = [
                        item.to_dict(exclude=v.back_populates)
                        for item in attribute
                        if hasattr(item, "to_dict")
                    ]
                else:
                    if hasattr(attribute, "to_dict"):  # pragma: no cover
                        result[k] = attribute.to_dict(exclude=(v.back_populates))
        return result

    @classmethod
    def to_schema(cls) -> type[SQLAlchemyAutoSchema]:
        """Convert Model to a marshmallow schema.

        .. versionadded:: 0.4.1
        """

        class Schema(SQLAlchemyAutoSchema):
            class Meta:
                model = cls
                load_instance = True
                include_relationships = True
                include_fk = True

        return Schema


@as_declarative()
class PureModel(BaseModel):
    """Provide a base model class with no pre-built columns.

    .. versionadded:: 0.4.1
    """

    pass


@as_declarative()
class Model(BaseModel):
    """The base model class.

    .. versionadded:: 0.1.0
    """

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
