# flake8: noqa
from flask.globals import current_app
from flask.globals import g as g
from flask.globals import request as request
from flask.globals import session as session
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .app import Djask

# Change the type annotation for ``current_app``
current_app: "Djask" = current_app  # type: ignore
