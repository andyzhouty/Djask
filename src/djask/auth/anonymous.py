from flask_login import AnonymousUserMixin


class AnonymousUser(AnonymousUserMixin):
    """
    An implementation of the AnonymousUserMixin provided by flask-login.

    .. versionadded:: 0.1.0
    """

    # set is_admin to False to prevent attribute errors
    is_admin = False
