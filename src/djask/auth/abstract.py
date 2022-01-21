import sqlalchemy as sa
from sqlalchemy.ext.declarative import AbstractConcreteBase
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login.mixins import UserMixin

from ..globals import current_app


class AbstractUser(AbstractConcreteBase, UserMixin):
    """
    A base class for all user models.

    It enables you to define a user model other than the
    :class:`~djask.auth.models.User` model below.

    .. versionadded:: 0.1.0
    """

    __table_args__ = {"extend_existing": True}
    username = sa.Column(sa.String(128), index=True, unique=True)
    name = sa.Column(sa.String(128))
    email = sa.Column(sa.String(256), unique=True)
    password_hash = sa.Column(sa.String(256))
    is_admin = sa.Column(sa.Boolean, default=False)

    def __repr__(self):  # pragma: no cover
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Set the password for the user.

        :param password: The password to set
        .. versionadded:: 0.1.0
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the password is correct.

        :param password: The password to check
        .. versionadded:: 0.1.0
        """
        return check_password_hash(self.password_hash, password)

    def api_token(self, expiration=3600) -> str:
        """Generate a new API token for the user.

        :param expiration: The expiration time of the token in seconds
        :returns: The API token
        .. versionadded:: 0.3.0
        """
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"id": self.id}).decode("ascii")
