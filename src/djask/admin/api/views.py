from apiflask.exceptions import abort
from flask import jsonify

from .decorators import admin_required_api
from .schemas import TokenInSchema
from .schemas import TokenOutSchema
from djask.blueprints import APIBlueprint
from djask.extensions import db
from djask.globals import current_app
from djask.globals import g
from djask.globals import request

admin_bp = APIBlueprint("admin_api", __name__)


@admin_bp.route(
    "/user/<int:uid>",
    methods=(
        "GET",
        "PUT",
        "DELETE",
    ),
)
@admin_required_api
def user_api(uid: int):
    if request.method == "GET":
        return g.User.query.get(uid).to_dict()

    elif request.method == "PUT":
        user = g.User.query.get_or_404(uid)
        user.update(request.get_json())
        user = g.User.query.get(uid)
        return user.to_dict()

    elif request.method == "DELETE":
        user = g.User.query.get_or_404(uid)
        db.session.delete(user)
        db.session.commit()
        return {}, 204


@admin_bp.post("/user")
@admin_required_api
def create_user():
    user = g.User()
    user.update(request.get_json())
    user = g.User.query.get(user.id)
    return user.to_dict(), 201


@admin_bp.post("/token")
@admin_bp.input(TokenInSchema, location="form")
@admin_bp.output(TokenOutSchema)
def get_token(data):
    """Return the access token and expiration."""
    user = (
        g.User.query.filter_by(username=data["username"])
        .filter_by(is_admin=True)
        .first()
    )
    if user is None or not user.check_password(data["password"]):
        abort(400, "Username or password invalid")
    token = user.api_token()
    response = jsonify(
        {
            "access_token": token,
            "expires_in": 3600 * 24 * 7,
        }
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


@admin_bp.route(
    "/<model>/<int:model_id>",
    methods=(
        "GET",
        "PUT",
        "DELETE",
    ),
)
@admin_bp.doc(hide=True)
@admin_required_api
def model_api(model: str, model_id: int):
    if request.method == "GET":
        model = current_app.get_model_by_name(model)
        instance = model.query.get_or_404(model_id)
        return instance.to_dict()

    elif request.method == "PUT":
        model = current_app.get_model_by_name(model)
        instance = model.query.get_or_404(model_id)
        for attr, value in request.get_json().items():
            if not hasattr(instance, attr):
                abort(400, f"Model {model} has no attribute {attr}.")
            instance.__setattr__(attr, value)
        db.session.commit()
        instance = model.query.get(model_id)
        return instance.to_dict()

    elif request.method == "DELETE":
        model = current_app.get_model_by_name(model)
        instance = model.query.get_or_404(model_id)
        db.session.delete(instance)
        db.session.commit()
        return {}, 204


@admin_bp.post("/<model>")
@admin_bp.doc(hide=True)
def post(model: str):
    """Create an instance of a model."""
    model = current_app.get_model_by_name(model)
    instance = model()
    for attr, value in request.get_json().items():
        if attr not in [column.key for column in model.__table__.columns]:
            abort(400, f"Model {model} has no attribute {attr}.")
        instance.__setattr__(attr, value)
    db.session.add(instance)
    db.session.commit()
    instance = model.query.get(instance.id)
    return instance.to_dict(), 201
