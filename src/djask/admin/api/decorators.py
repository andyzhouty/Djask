from functools import wraps
import typing as t

from flask import abort

from djask.helpers import get_user_from_headers


def admin_required_api(f: t.Callable) -> t.Callable:
    """Require admin access in web api

    :param f: The view function/method to be decorated
    :return: The view function
    """

    @wraps(f)
    def decorator(*args, **kwargs) -> t.Callable:
        user = get_user_from_headers()
        if user is None or not user.is_admin:
            abort(403)  # pragma: no cover
        return f(*args, **kwargs)

    return decorator
