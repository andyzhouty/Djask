from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from sqlalchemy.ext.declarative import AbstractConcreteBase
from flask_login.mixins import UserMixin, AnonymousUserMixin


class AbstractUser(AbstractConcreteBase):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(256), unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class User(AbstractUser, db.Model, UserMixin):
    def __repr__(self):
        return f"<User {self.username}>"


class AnonymousUser(AnonymousUserMixin):
    is_admin = False
