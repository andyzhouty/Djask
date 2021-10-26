import os

from flask import current_app
from flask_sqlalchemy import Model

from .views import admin_bp
from ..app import Djask


class Admin:
    def __init__(self, app: Djask = None) -> None:
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app: Djask) -> None:
        if app is not None:  # pragma: no cover
            self.app = app
        if not hasattr(app, "extensions") or app.extensions is None:  # pragma: no cover
            self.app.extensions = {}
        self.app.extensions["djask_admin"] = self
        self.app.config["ADMIN_MODEL_MAP"] = {}

        self.app.register_blueprint(admin_bp, url_prefix="/admin")

    def register_model(self, model: Model) -> None:
        self.app.config["ADMIN_MODEL_MAP"][model.__name__] = model

    def register_models(self, *models: list[Model]) -> None:
        for model in models:
            self.register_model(model)
