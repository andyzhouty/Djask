from flask.globals import current_app, g, session, request

from .app import Djask

# Change the type annotation for ``current_app``
current_app: Djask = current_app  # type: ignore
