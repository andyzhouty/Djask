import datetime as dt
import typing as t

import sqlalchemy as sa
from sqlalchemy.orm import as_declarative
from sqlalchemy.ext.declarative import declared_attr

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


@as_declarative()
class Model:
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @classmethod
    def to_schema(cls) -> t.Type[SQLAlchemyAutoSchema]:
        class Schema(SQLAlchemyAutoSchema):
            class Meta:
                model = cls
                load_instance = True
                include_relationships = True
                include_fk = True

        return Schema
