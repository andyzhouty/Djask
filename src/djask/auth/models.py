from ..db import Model
from .abstract import AbstractUser
from .permission import Permission as Permission  # noqa


class User(AbstractUser, Model):
    """
    An implementation of the AbstractUser class used for admin interface.

    .. versionadded:: 0.1.0
    """

    pass
