from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms_sqlalchemy.orm import model_form

from .models import User


UserForm = model_form(User, base_class=FlaskForm)
UserForm.password = PasswordField("password")
