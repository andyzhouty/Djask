from __future__ import annotations

from time import time

from authlib.jose import JoseError
from authlib.jose import jwt
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms_sqlalchemy.orm import model_form

from .auth.abstract import AbstractUser
from .extensions import db
from .globals import current_app
from .globals import g
from .globals import request
from .types import ModelType


def get_model_form(model_name: str) -> tuple[ModelType, FlaskForm]:
    """Generate and return a form for a model

    :param model_name: The name of the model
    :return: A tuple of the model and the form
    .. versionadded: 0.1.0
    """
    model = current_app.get_model_by_name(model_name)  # type: ignore
    if model != g.User:  # pragma: no cover
        ModelForm = model_form(model, base_class=FlaskForm, db_session=db.session)
    else:
        ModelForm = model_form(
            model,
            base_class=FlaskForm,
            exclude=("password_hash",),
            db_session=db.session,
        )
        ModelForm.password = PasswordField("password")
    ModelForm.submit = SubmitField()
    return model, ModelForm()


def get_user_from_token(token: str) -> AbstractUser | None:
    """Get the user from an access token

    :param token: The access token
    :return: A user
    .. versionadded: 0.3.0
    """
    try:
        data = jwt.decode(token.encode("ascii"), current_app.config["SECRET_KEY"])
        current = time()
        expiration = int(data.get("expiration", -1))
        created = int(data.get("created", current))
        if current > created + expiration:  # pragma: no cover
            raise JoseError("Token expired.")
    except ValueError:  # pragma: no cover
        return None
    except JoseError:  # pragma: no cover
        return None
    return g.User.query.get(data.get("id"))


def get_user_from_headers() -> AbstractUser | None:
    """Get the user from the request headers.
    Expected to be called from the web api.

    .. versionadded: 0.3.0
    """
    token = request.headers.get("Authorization")
    if token is not None:
        return get_user_from_token(token)
    return None  # pragma: no cover
