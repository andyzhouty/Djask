import os.path as path
import typing as t

from apiflask import APIFlask
from apiflask.exceptions import HTTPError

from .extensions import db


def _check_empty(data: t.Any) -> t.Any:
    return data if data else ""


class Djask(APIFlask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.setdefault("ADMIN_SITE", False)
        self.config.setdefault("ADMIN_MODEL_MAP", {})
        self.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.db = db
        self.db.init_app(self)
        self.template_folder = path.abspath(
            path.join(path.dirname(__file__), "templates")
        )

    @staticmethod
    def _error_handler(
        error: HTTPError,
    ) -> t.Union[t.Tuple[dict, int], t.Tuple[dict, int, t.Mapping[str, str]]]:
        """Override the default error handler in APIFlask"""
        status_code, message = (
            _check_empty(error.status_code),
            _check_empty(error.message),
        )
        detail = error.detail
        body = f"{status_code} {message}{'<br />'+detail if detail else ''}"
        return body, error.status_code, error.headers
