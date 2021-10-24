from flask.globals import current_app
from flask_sqlalchemy import Model


def register(model: Model) -> Model:
    """Register the model to the admin page."""
    current_app.config["ADMIN_MODEL_MAP"][model.__name__.lower()] = model
    return model
