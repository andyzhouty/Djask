import os.path as path
import typing as t

from apiflask import APIFlask
from apiflask.exceptions import HTTPError
from flask_sqlalchemy import SQLAlchemy


class Djask(APIFlask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.setdefault("ADMIN_SITE", False)
        self.config.setdefault("ADMIN_MODEL_MAP", {})
        self.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.db = SQLAlchemy()
        self.db.init_app(self)
        self.template_folder = path.abspath(
            path.join(path.dirname(__file__), "templates")
        )

    @staticmethod
    def _error_handler(
        error: HTTPError,
    ) -> t.Union[t.Tuple[dict, int], t.Tuple[dict, int, t.Mapping[str, str]]]:
        """Override the default error handler in APIFlask"""
        body = f"{error.status_code} {error.message}<br />{error.detail}"
        return body, error.status_code, error.headers
