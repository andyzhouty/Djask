from typing import NoReturn

from flask_login import AnonymousUserMixin


class NoDBForAnonymousError(NotImplementedError):
    def __init__(self):
        # fmt: off
        super().__init__(
            "Djask doesn't provide a DB representation for AnonymousUser"
        )
        # fmt: on


class AnonymousUser(AnonymousUserMixin):
    """
    An implementation of the AnonymousUserMixin provided by flask-login.

    .. versionchanegd:: 0.7.0
    .. versionadded:: 0.1.0
    """

    def set_password(self, password: str) -> NoReturn:  # type: ignore
        raise NoDBForAnonymousError

    def check_password(self, password: str) -> NoReturn:  # type: ignore
        raise NoDBForAnonymousError

    def delete(self) -> NoReturn:
        raise NoDBForAnonymousError

    @property
    def is_admin(self) -> bool:
        return False
