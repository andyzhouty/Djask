import datetime as dt
import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import as_declarative
from sqlalchemy.ext.declarative import declared_attr

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

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Convert Model to dict.

        :return: [description]
        :rtype: t.Dict[str, t.Any]
        """
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

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
