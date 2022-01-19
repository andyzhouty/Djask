from functools import wraps
import typing as t

from flask import abort

from djask.auth.models import User
from djask.globals import request
from djask.helpers import get_user_from_token


def get_user_from_headers() -> t.Union[User, None]:
    token = request.headers.get("Authorization")
    if token is not None:
        return get_user_from_token(token)
    return None  # pragma: no cover


def admin_required(f: t.Callable) -> t.Callable:
    @wraps(f)
    def decorator(*args, **kwargs) -> t.Callable:
        user = get_user_from_headers()
        if user is None or not user.is_admin:
            abort(403)  # pragma: no cover
        return f(*args, **kwargs)

    return decorator
