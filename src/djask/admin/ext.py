"""Provide a pluggable admin interface for Djask."""

import typing as t
from djask import current_app

from flask_login import LoginManager

from .views import admin_bp
from ..app import Djask, Blueprint
from ..auth.anonymous import AnonymousUser
from ..extensions import csrf
from .api.views import admin_api

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: int):
    return current_app.config["AUTH_MODEL"].query.get(user_id)


class Admin:
    """
    The admin interface for Djask applications.

    .. versionadded: 0.1.0
    :param app: The app to wrap.
    """

    app: Djask
    blueprint: Blueprint

    def __init__(
        self, app: t.Optional[Djask] = None, admin_prefix: t.Optional[str] = None
    ) -> None:
        """
        Initialize the Admin extension.

        .. versionadded:: 0.1.0
        :param app: A Djask app
        """
        if app is not None:  # pragma: no cover
            self.init_app(app, admin_prefix)

    def init_app(self, app: Djask, admin_prefix: t.Optional[str] = "/admin") -> None:
        """
        Another way to initialize the Admin extension.

        .. versionchanged:: 0.2.0

        .. versionadded:: 0.1.0
        """
        self.app = app
        if not hasattr(app, "extensions") or app.extensions is None:  # pragma: no cover
            self.app.extensions = {}
        login_manager.init_app(app)
        login_manager.anonymous_user = AnonymousUser

        self.app.models.append(app.config["AUTH_MODEL"])
        custom_prefix = self.app.config.get("ADMIN_PREFIX")
        if isinstance(custom_prefix, str):  # pragma: no cover
            admin_prefix = custom_prefix
        self.app.register_blueprint(admin_bp, url_prefix=admin_prefix)
        self.blueprint = admin_bp
        self.app.register_blueprint(admin_api, url_prefix=admin_prefix + "/api")
        csrf.exempt(admin_api)
