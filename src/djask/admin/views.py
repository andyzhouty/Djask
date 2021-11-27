from typing import Optional

from sqlalchemy.orm.attributes import InstrumentedAttribute
from flask import render_template, flash, redirect, url_for
from flask_login.utils import login_user, logout_user
from flask_wtf import FlaskForm

from wtforms import SubmitField
from wtforms_sqlalchemy.orm import model_form


from .forms import LoginForm
from .decorators import admin_required
from ..auth.forms import UserForm
from ..auth.models import User
from ..blueprints import Blueprint
from ..globals import current_app, request
from ..extensions import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@admin_required
def index():
    blueprints = current_app.blueprint_objects
    return render_template(
        "admin/dashboard.html",
        User=User,
        models=current_app.models,
        blueprints=blueprints,
    )


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # identify the user
        if not user:
            flash("User not found.", "danger")
        elif not user.is_admin:
            flash("User not administrative.", "danger")
        elif not user.check_password(form.password.data):
            flash("Wrong password.", "danger")
        else:
            login_user(user, form.remember_me.data)
            next: Optional[str] = request.args.get("next")
            return redirect(next or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_bp.route("/<model_name>")
@admin_required
def specific_model(model_name: str):
    model_name = model_name.lower()
    model = current_app.get_model_by_name(model_name)
    schema = {}
    for name, value in model.__dict__.items():
        if isinstance(value, InstrumentedAttribute):
            schema[name] = value
    print(model)
    instances = model.query.all()
    return render_template(
        "admin/model.html",
        model=model,
        model_name=model.__name__,
        schema=schema,
        instances=instances,
    )


@admin_bp.route(
    "/<model_name>/add",
    methods=(
        "GET",
        "POST",
    ),
)
@admin_required
def add_model(model_name: str):
    model = current_app.get_model_by_name(model_name)
    ModelForm = model_form(model, base_class=FlaskForm)
    ModelForm.submit = SubmitField()
    form = ModelForm() if model != User else UserForm()
    if form.validate_on_submit():
        m = model()
        for name in form._fields.keys():
            value = form.__getattribute__(name).data
            if not value:
                continue
            print(name)
            if model == User and name == "password":
                m.set_password(value)
            else:
                m.__setattr__(name, value)
        db.session.add(m)
        db.session.commit()
        flash(f"A new instance of {model_name} has been created!", "success")
        return redirect(url_for("admin.specific_model", model_name=model.__name__))
    return render_template("admin/model_add.html", form=form, model_name=model.__name__)
