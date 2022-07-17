from __future__ import annotations

from time import time
from typing import Any

import sqlalchemy as sa
from apiflask.exceptions import abort
from authlib.jose import jwt
from flask_login.mixins import UserMixin
from sqlalchemy.ext.declarative import AbstractConcreteBase
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from ..extensions import db


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

    def api_token(self, expiration=3600 * 24 * 7) -> str:
        """Generate a new API token for the user.

        :param expiration: The expiration time of the token in seconds
        :returns: The API token
        .. versionadded:: 0.3.0
        .. versionchanged:: 0.4.2
        """
        from ..globals import current_app  # noreorder

        header = {"alg": "HS256"}
        data = {"id": self.id, "created": time(), "expiration": expiration}
        return jwt.encode(header, data, current_app.config["SECRET_KEY"]).decode()

    def update(self, data: dict[str, Any]) -> None:
        """Update the user with the given dict.

        :param data: The dict containing user data
        .. versionadded:: 0.4.2
        """
        for attr, value in data.items():
            if not hasattr(self, attr) and attr != "password":  # pragma: no cover
                abort(400, f"User model has no attribute {attr}.")
            elif attr == "password":
                self.set_password(value)
                continue
            if attr == "password_hash":  # pragma: no cover
                abort(400, "You should not hard-code the password hash.")
            self.__setattr__(attr, value)
        db.session.add(self)
        db.session.commit()
