import typing as t

from flask_login import LoginManager
from flask_sqlalchemy import Model

from .views import admin_bp
from ..app import Djask
from ..auth.models import User, AnonymousUser

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)


class Admin:
    def __init__(self, app: Djask = None) -> None:
        """Initialize the Admin extension."""
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app: Djask) -> None:
        """Initialize"""
        if app is not None:  # pragma: no cover
            self.app = app
        if not hasattr(app, "extensions") or app.extensions is None:  # pragma: no cover
            self.app.extensions = {}
        login_manager.init_app(app)
        login_manager.anonymous_user = AnonymousUser

        self.app.config["ADMIN_MODELS"] = [User]
        self.app.register_blueprint(admin_bp)

    def register_model(self, model: Model) -> None:
        self.app.config["ADMIN_MODELS"].append(model)

    def register_models(self, *models: t.List[Model]) -> None:
        for model in models:
            self.register_model(model)
