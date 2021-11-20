import datetime as dt

import sqlalchemy as sa
from sqlalchemy.orm import as_declarative

from sqlalchemy.ext.declarative import declared_attr


@as_declarative()
class Model:
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=dt.datetime.utcnow)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
