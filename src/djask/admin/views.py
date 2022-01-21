from sys import prefix
import typing as t

from sqlalchemy.orm.attributes import InstrumentedAttribute
from flask import render_template, flash, redirect, url_for
from flask_login.utils import login_user, logout_user

from .forms import LoginForm
from .decorators import admin_required
from ..blueprints import Blueprint
from ..globals import current_app, request, g
from ..extensions import db
from ..helpers import get_model_form

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@admin_required
def index():
    blueprints = current_app.blueprint_objects
    return render_template(
        "admin/dashboard.html",
        User=g.User,
        models=current_app.models,
        blueprints=blueprints,
    )


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = g.User.query.filter_by(username=form.username.data).first()
        # identify the user
        if not user:
            flash("User not found.", "danger")
        elif not user.is_admin:
            flash("User not administrative.", "danger")
        elif not user.check_password(form.password.data):
            flash("Wrong password.", "danger")
        else:
            login_user(user, form.remember_me.data)
            next: t.Optional[str] = request.args.get("next")
            return redirect(next or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_bp.route("/<model_name>")
@admin_required
def specific_model(model_name: str):
    model = current_app.get_model_by_name(model_name)
    schema = {}
    for name, value in model.__dict__.items():
        if isinstance(value, InstrumentedAttribute):
            try:
                type = value.type.__repr__()
            except Exception:  # pragma: no cover
                type = f"Relationship({value.prop.argument})"
            schema[name] = type
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
    model, form = get_model_form(model_name)
    if form.validate_on_submit():
        m = model()
        for name in form._fields.keys():
            value = getattr(form, name).data
            if not value:
                continue
            if model == g.User and name == "password":
                m.set_password(value)
            else:
                setattr(m, name, value)
        db.session.add(m)
        db.session.commit()
        flash(f"A new instance of {model_name} has been created!", "success")
        return redirect(url_for("admin.specific_model", model_name=model.__name__))
    return render_template("admin/model_add.html", form=form, model_name=model.__name__)


@admin_bp.route(
    "/<model_name>/<int:model_id>",
    methods=(
        "GET",
        "POST",
    ),
)
@admin_bp.route(
    "/<model_name>/<int:model_id>/edit",
    methods=(
        "GET",
        "POST",
    ),
)
@admin_required
def edit_model(model_name: str, model_id: int):
    model, form = get_model_form(model_name)
    m = model.query.get(model_id)
    if m is None:
        return (
            render_template(
                "admin/model_404.html", model_id=model_id, model_name=model_name
            ),
            404,
        )

    if form.validate_on_submit():
        for name in form._fields.keys():
            value = getattr(form, name).data
            if not value:
                continue
            if model == g.User and name == "password":
                m.set_password(value)
            else:
                setattr(m, name, value)
        db.session.commit()
        flash(f"{model_name} id {m.id} has been modified!", "success")
        return redirect(url_for("admin.specific_model", model_name=model.__name__))
    for name in form._fields.keys():
        if (
            not (model == g.User and name == "password")
            and name != "submit"
            and name != "csrf_token"
        ):
            getattr(form, name).data = getattr(m, name)
    return render_template(
        "admin/model_edit.html", form=form, model_name=model.__name__, model_id=model_id
    )
