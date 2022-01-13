from tokenize import String

from sqlalchemy import Integer


from apiflask import Schema
from apiflask.fields import Integer, String, Boolean


class TokenInSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class TokenOutSchema(Schema):
    access_token = String()
    expires_in = Integer()


class UserSchema(Schema):
    id = Integer()
    username = String()
    name = String()
    email = String()
    is_admin = Boolean()
