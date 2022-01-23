import datetime as dt
import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
from djask.auth.abstract import AbstractUser

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


@as_declarative()
class Model:
    """The base model class.

    .. versionadded:: 0.1.0
    """

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self, exclude: t.Tuple[str] = None) -> t.Dict[str, t.Any]:
        """Convert Model to dict.

        .. versionadded:: 0.3.0
        """
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
                        item.to_dict(exclude=v.back_populates) for item in attribute
                    ]
                else:
                    result[k] = attribute.to_dict(exclude=(v.back_populates))
        return result

    @classmethod
    def to_schema(cls) -> t.Type[SQLAlchemyAutoSchema]:
        """Convert Model to a marshmallow schema.

        :return: [description]
        :rtype: t.Type[SQLAlchemyAutoSchema]
        """

        class Schema(SQLAlchemyAutoSchema):
            class Meta:
                model = cls
                load_instance = True
                include_relationships = True
                include_fk = True

        return Schema
