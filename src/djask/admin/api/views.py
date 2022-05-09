import typing as t
from apiflask.exceptions import abort
from flask import jsonify
from flask.views import MethodView

from .decorators import admin_required_api
from .schemas import TokenInSchema
from .schemas import TokenOutSchema
from djask.auth.abstract import AbstractUser
from djask.blueprints import APIBlueprint
from djask.extensions import db
from djask.globals import current_app
from djask.globals import g
from djask.globals import request

# fmt: off
# fmt: on

admin_bp = APIBlueprint("admin_api", __name__)


@admin_bp.route("/user/<int:user_id>")
class UserAPI(MethodView):
    decorators = [admin_required_api]

    def get(self, user_id: int) -> AbstractUser:
        """Retrieve a user."""
        return g.User.query.get(user_id).to_dict()

    def put(self, user_id: int) -> AbstractUser:
        """Update a user."""
        user = g.User.query.get_or_404(user_id)
        user.update(request.get_json())
        user = g.User.query.get(user_id)
        return user.to_dict()

    def delete(self, user_id: int):
        """Delete a user."""
        user = g.User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {}, 204


@admin_bp.route("/user")
class UserCreateAPI(MethodView):
    decorators = [admin_required_api]

    def post(self) -> t.Tuple[AbstractUser, int]:
        """Create a user."""
        user = g.User()
        user.update(request.get_json())
        user = g.User.query.get(user.id)
        return user.to_dict(), 201


@admin_bp.route("/token")
class TokenAPI(MethodView):
    @admin_bp.input(TokenInSchema, location="form")
    @admin_bp.output(TokenOutSchema)
    def post(self, data):
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
                "expires_in": 3600,
            }
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response


@admin_bp.route("/<model>/<int:model_id>")
class ModelAPI(MethodView):
    decorators = [admin_bp.doc(hide=True), admin_required_api]

    def get(self, model: str, model_id: int):
        """Retrieve an instance of a model."""
        model = current_app.get_model_by_name(model)
        instance = model.query.get_or_404(model_id)
        return instance.to_dict()

    def put(self, model: str, model_id: int):
        """Update an instance of a model."""
        model = current_app.get_model_by_name(model)
        instance = model.query.get_or_404(model_id)
        for attr, value in request.get_json().items():
            if not hasattr(instance, attr):
                abort(400, f"Model {model} has no attribute {attr}.")
            instance.__setattr__(attr, value)
        db.session.commit()
        instance = model.query.get(model_id)
        return instance.to_dict()

    def delete(self, model: str, model_id: int):
        """Delete an instance of a model."""
        model = current_app.get_model_by_name(model)
        instance = model.query.get_or_404(model_id)
        db.session.delete(instance)
        db.session.commit()
        return {}, 204


@admin_bp.route("/<model>")
class ModelCreateAPI(MethodView):
    decorators = [admin_bp.doc(hide=True), admin_required_api]

    def post(self, model: str):
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
