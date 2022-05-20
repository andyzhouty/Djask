"""
Provide a pluggable admin interface for Djask.
"""
import importlib
import typing as t
from flask_login import LoginManager
from typing_extensions import Literal

from ..app import Blueprint
from ..app import Djask
from ..auth.anonymous import AnonymousUser
from ..extensions import csrf
from djask import current_app

# support python 3.7

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: int):
    return current_app.config["AUTH_MODEL"].query.get(user_id)


ModeLiteral = Literal["api", "ui"]
ModeArg = t.Union[
    ModeLiteral,
    t.Sequence[ModeLiteral],
]


class AdminModeError(Exception):
    def __init__(self):
        super().__init__("Expecting mode to be either 'api' or 'ui'")


class Admin:
    """
    The admin interface for Djask applications.

    .. versionadded: 0.1.0

        :param app: The app to wrap.
    """

    app: Djask
    blueprint: Blueprint

    def __init__(
        self,
        app: t.Optional[Djask] = None,
        admin_prefix: t.Optional[str] = None,
        mode: ModeArg = None,
    ) -> None:
        """
        Initialize the Admin extension.

        .. versionadded:: 0.1.0
        .. versionchanged:: 0.5.0
            Add mode support.

        :param app: A Djask app
        """
        if app is not None:  # pragma: no cover
            self.init_app(app, admin_prefix, mode)

    def init_app(
        self,
        app: Djask,
        admin_prefix: t.Optional[str] = "/admin",
        mode: t.Optional[ModeArg] = ("api", "ui"),
    ) -> None:
        """
        Another way to initialize the Admin extension.

        .. versionadded:: 0.1.0

        .. versionchanged:: 0.5.0
        """
        self.app = app
        if not hasattr(app, "extensions") or app.extensions is None:  # pragma: no cover
            self.app.extensions = {}
        login_manager.init_app(app)
        login_manager.anonymous_user = AnonymousUser

        self.app.models.append(app.config["AUTH_MODEL"])
        custom_prefix = self.app.config.get("ADMIN_PREFIX")
        admin_prefix = custom_prefix or "/admin"

        if isinstance(mode, str):
            self._register_bp(mode, admin_prefix)
        elif isinstance(mode, t.Sequence):
            if len(mode) == 0:
                raise AdminModeError
            for m in mode:
                self._register_bp(m, admin_prefix)  # type: ignore
        else:  # pragma: no cover
            raise AdminModeError

    def _register_bp(self, mode: ModeLiteral, admin_prefix: str):
        module = importlib.import_module(f".admin.{mode}.views", "djask")
        self.app.register_blueprint(
            module.admin_bp,
            url_prefix=admin_prefix if mode == "ui" else (admin_prefix + "/api"),
        )
        if mode == "api":
            csrf.exempt(module.admin_bp)
