import sqlalchemy as db
from sqlalchemy.ext.declarative import declared_attr, AbstractConcreteBase
from flask_sqlalchemy import Model

from djask.admin.decorators import register


@register
class User(AbstractConcreteBase, Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(256), unique=True)
