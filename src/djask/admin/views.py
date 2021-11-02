from typing import Optional

from flask import render_template, abort, flash, redirect, url_for
from flask.globals import current_app, request
from flask.blueprints import Blueprint
from flask_login.utils import login_user, logout_user

from .forms import LoginForm
from .decorators import admin_required
from ..auth.models import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@admin_required
def index():
    return render_template("admin/main.html", models=current_app.config["ADMIN_MODELS"])


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
    registered_models = [
        model.__name__.lower() for model in current_app.config["ADMIN_MODELS"]
    ]
    if model_name not in registered_models:
        abort(404, "Data model not defined or registered.")
    return render_template(
        "admin/model.html",
        model=current_app.config["ADMIN_MODELS"][registered_models.index(model_name)],
    )
