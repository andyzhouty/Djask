import os.path as path
import typing as t

from apiflask import APIFlask
from apiflask.exceptions import HTTPError
from apiflask.types import ErrorCallbackType

from flask_sqlalchemy import SQLAlchemy

from .admin import admin_bp


class Djask(APIFlask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.setdefault("ADMIN_MODEL_MAP", {})
        self.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.db = SQLAlchemy()
        self.db.init_app(self)
        self.template_folder = path.abspath(
            path.join(path.dirname(__file__), "templates")
        )
        self.register_blueprint(
            admin_bp,
            url_prefix="/admin",
        )

    @staticmethod
    def _error_handler(
        error: HTTPError,
    ) -> t.Union[t.Tuple[dict, int], t.Tuple[dict, int, t.Mapping[str, str]]]:
        """Override the default error handler in APIFlask"""
        body = f"{error.status_code} {error.message}<br />{error.detail}"
        return body, error.status_code, error.headers

    def error_processor(self, f: ErrorCallbackType) -> ErrorCallbackType:
        """Override the default error processor in APIFlask"""
        if hasattr(self, "ensure_sync"):  # pragma: no cover
            self.error_callback = self.ensure_sync(f)
        else:  # pragma: no cover
            self.error_callback = f
        return f
