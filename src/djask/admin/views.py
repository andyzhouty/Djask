from typing import Optional

from flask import render_template, abort, flash, redirect, url_for
from flask_login.utils import login_user, logout_user

from .forms import LoginForm
from .decorators import admin_required
from ..auth.models import User
from ..blueprints import Blueprint
from ..globals import current_app, request

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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
    models = current_app.models
    registered_models = [model.__name__.lower() for model in models]
    if model_name not in registered_models:
        abort(404, "Data model not defined or registered.")
    model = models[registered_models.index(model_name)]
    return render_template("admin/model.html", model=model, model_name=model.__name__)


@admin_bp.route("/<model_name>/add")
@admin_required
def add_model(model_name: str):
    # TODO: Write add_model view
    return "Hello World"  # pragma: no cover
