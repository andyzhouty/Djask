import typing as t

from flask_wtf import FlaskForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from wtforms import SubmitField
from wtforms_sqlalchemy.orm import model_form

from .auth.forms import UserForm
from .auth.models import User
from .globals import current_app
from .types import ModelType


def get_model_form(model_name: str) -> t.Tuple[ModelType, FlaskForm]:
    model = current_app.get_model_by_name(model_name)
    ModelForm = model_form(model, base_class=FlaskForm) if model != User else UserForm
    ModelForm.submit = SubmitField()
    return model, ModelForm()


def get_user_from_token(token: str) -> User:
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token.encode("ascii"))
    except:  # pragma: no cover
        return None
    return User.query.get(data.get("id"))
