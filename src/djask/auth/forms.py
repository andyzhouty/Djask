from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms_sqlalchemy.orm import model_form

from ..globals import g


def UserForm() -> FlaskForm:
    form = model_form(g.User, base_class=FlaskForm, exclude=("password_hash",))
    form.password = PasswordField("password")
    return form()
