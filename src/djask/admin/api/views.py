import typing as t

from apiflask.decorators import doc

from flask import jsonify
from flask.views import MethodView
from apiflask import input, output
from apiflask.exceptions import abort

from djask.auth.abstract import AbstractUser
from djask.blueprints import APIBlueprint

# fmt: off
from .schemas import (
    TokenInSchema, TokenOutSchema,
    UserInSchema, UserOutSchema
)
# fmt: on
from .decorators import admin_required_api
from djask.globals import current_app, request, g
from djask.extensions import db

admin_api = APIBlueprint("admin_api", __name__)


@admin_api.route("/user/<int:user_id>")
class UserAPI(MethodView):
    decorators = [admin_required_api]

    def get(self, user_id: int) -> AbstractUser:
        """Retrieve a user."""
        return g.User.query.get(user_id).to_dict()

    def put(self, user_id: int) -> AbstractUser:
        """Update a user."""
        user = g.User.query.get_or_404(user_id)
        for attr, value in request.get_json().items():
            if not hasattr(user, attr) and attr != "password":  # pragma: no cover
                abort(400, f"User model has no attribute {attr}.")
            elif attr == "password":
                user.set_password(value)
                continue
            if attr == "password_hash":  # pragma: no cover
                abort(400, "You should not hard-code the password hash.")
            user.__setattr__(attr, value)
        db.session.commit()
        user = g.User.query.get(user_id)
        return user.to_dict()

    def delete(self, user_id: int):
        """Delete a user."""
        user = g.User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {}, 204


@admin_api.route("/user")
class UserCreateAPI(MethodView):
    decorators = [admin_required_api]

    def post(self) -> AbstractUser:
        """Create a user."""
        user = g.User()
        for attr, value in request.get_json().items():
            if not hasattr(user, attr) and attr != "password":  # pragma: no cover
                abort(400, f"User model has no attribute {attr}.")
            elif attr == "password":
                user.set_password(value)
                continue
            if attr == "password_hash":  # pragma: no cover
                abort(400, "You should not hard-code the password hash.")
            user.__setattr__(attr, value)
        db.session.add(user)
        db.session.commit()
        user = g.User.query.get(user.id)
        return user.to_dict(), 201


@admin_api.route("/token")
class TokenAPI(MethodView):
    @input(TokenInSchema, location="form")
    @output(TokenOutSchema)
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


@admin_api.route("/<model>/<int:model_id>")
class ModelAPI(MethodView):
    decorators = [doc(hide=True), admin_required_api]

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


@admin_api.route("/<model>")
class ModelCreateAPI(MethodView):
    decorators = [doc(hide=True), admin_required_api]

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
