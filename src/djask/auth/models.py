from ..db import Model
from .abstract import AbstractUser


class User(AbstractUser, Model):
    """
    An implementation of the AbstractUser class used for admin interface.

    .. versionadded:: 0.1.0
    """

    pass
