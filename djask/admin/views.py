from flask import Blueprint, render_template, abort
from flask.globals import current_app

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
def index():
    return render_template(
        "admin/main.html", models=current_app.config["ADMIN_MODEL_MAP"].values()
    )


@admin_bp.route("/<model_name>")
def specific_model(model_name: str):
    model_name = model_name.lower()
    if model_name not in [
        name.lower() for name in current_app.config["ADMIN_MODEL_MAP"].keys()
    ]:
        abort(404, "Data model not defined or registered.")
    return render_template(
        "admin/model.html", model=current_app.config["ADMIN_MODEL_MAP"][model_name]
    )
