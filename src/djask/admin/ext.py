"""
Provide a pluggable admin interface for Djask.
"""

import typing as t

from flask_login import LoginManager

from .views import admin_bp
from ..app import Djask, Blueprint
from ..auth.models import User, AnonymousUser

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)


class Admin:
    """
    The admin interface for Djask applications

    .. versionadded: 0.1.0
    :param app: The app to wrap.
    """
    app: Djask
    blueprint: Blueprint

    def __init__(self, app: t.Optional[Djask] = None) -> None:
        """
        Initialize the Admin extension.

        .. versionadded:: 0.1.0
        :param app: A Djask app
        """
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app: Djask) -> None:
        """
        Another way to initialize the Admin extension.

        .. versionadded:: 0.1.0
        """
        self.app = app
        if not hasattr(app, "extensions") or app.extensions is None:  # pragma: no cover
            self.app.extensions = {}
        login_manager.init_app(app)
        login_manager.anonymous_user = AnonymousUser

        self.app.models.append(User)
        self.app.register_blueprint(admin_bp)
        self.blueprint = admin_bp
