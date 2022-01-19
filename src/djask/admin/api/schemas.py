from apiflask import Schema
from apiflask.fields import Integer, String, Boolean


class TokenInSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class TokenOutSchema(Schema):
    access_token = String()
    expires_in = Integer()


class UserOutSchema(Schema):
    id = Integer()
    username = String()
    name = String()
    email = String()
    is_admin = Boolean()


class UserInSchema(Schema):
    username = String(required=True)
    name = String()
    email = String()
    is_admin = Boolean(dump_default=False)
    password = String(required=True)
