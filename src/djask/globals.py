# flake8: noqa
from typing import TYPE_CHECKING

from flask.globals import current_app
from flask.globals import g as g
from flask.globals import request as request
from flask.globals import session as session

if TYPE_CHECKING:  # pragma: no cover
    from .app import Djask

# Change the type annotation for ``current_app``
current_app: "Djask" = current_app  # type: ignore
