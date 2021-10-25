from .views import admin_bp
from ..app import Djask


class Admin:
    def __init__(self, app: Djask = None):
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app: Djask):
        if not hasattr(app, "extensions") or app.extensions is None:  # pragma: no cover
            app.extensions = {}
        app.extensions["djask_admin"] = self
        app.config["ADMIN_MODEL_MAP"] = {}

        app.register_blueprint(admin_bp, url_prefix="/admin")
