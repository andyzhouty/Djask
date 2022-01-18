import sqlalchemy as sa
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import AbstractConcreteBase
from flask_login.mixins import UserMixin, AnonymousUserMixin

from ..extensions import db
from ..globals import current_app


class AbstractUser(AbstractConcreteBase, UserMixin):
    """
    A base class for all user models.

    It enables you to define a user model other than the User model below

    .. versionadded:: 0.1.0
    """

    username = sa.Column(sa.String(128), index=True, unique=True)
    name = sa.Column(sa.String(128))
    email = sa.Column(sa.String(256), unique=True)
    password_hash = sa.Column(sa.String(256))
    is_admin = sa.Column(sa.Boolean, default=False)

    def set_password(self, password: str) -> None:
        """Set the password for the user

        :param password: The password to set
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the password is correct

        :param password: The password to check
        """
        return check_password_hash(self.password_hash, password)

    def api_token(self, expiration=3600):
        """Generate a new API token for the user

        :param expiration: The expiration time of the token in seconds
        """
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"id": self.id}).decode("ascii")


class User(AbstractUser, db.Model):
    """
    An implementation of the AbstractUser class used for admin interface.

    .. versionadded:: 0.1.0
    """

    def __repr__(self):  # pragma: no cover
        return f"<User {self.username}>"


class AnonymousUser(AnonymousUserMixin):
    """
    An implementation of the AnonymousUserMixin provided by flask-login.

    .. versionadded:: 0.1.0
    """

    # set is_admin to False to prevent attribute errors
    is_admin = False
