import typing as t
from functools import wraps

from flask_login import current_user
from flask import Response, current_app, redirect, url_for
from flask_sqlalchemy import Model


def register(model: Model) -> Model:
    """
    Register the model to the admin page.
    
    .. versionadded:: 0.1.0
    
    :param model: The data model to be wrapped
    """
    current_app.config["ADMIN_MODELS"].append(model)
    return model


def admin_required(func: t.Callable) -> t.Callable:
    """
    Decorator to require admin access.
    
    .. versionadded:: 0.1.0
    
    :param func: The route to be wrapped by this decorator.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        print(current_user)
        if not (current_user.is_authenticated and current_user.is_admin):
            return redirect(url_for("admin.login"))
        return func(*args, **kwargs)

    return wrapper
