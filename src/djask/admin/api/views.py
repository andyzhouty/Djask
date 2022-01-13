from flask import jsonify
from flask.views import MethodView
from apiflask import input, output
from apiflask.exceptions import abort

from djask.auth.models import User
from djask.blueprints import APIBlueprint

# fmt: off
from .schemas import (
    TokenInSchema, TokenOutSchema,
    UserSchema
)
# fmt: on
from .decorators import admin_required

admin_api = APIBlueprint("admin_api", __name__)


@admin_api.route("/user/<int:user_id>")
class UserAPI(MethodView):
    @admin_required
    @output(UserSchema)
    def get(self, user_id: int) -> User:
        """
        returns a user
        """
        return User.query.get(user_id)


@admin_api.route("/token")
class TokenAPI(MethodView):
    @input(TokenInSchema, location="form")
    @output(TokenOutSchema)
    def post(self, data):
        """
        returns the access token and other info
        """
        user: User = (
            User.query.filter_by(username=data["username"])
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
