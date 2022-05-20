"""
This app.py is just a simple demo. Do not write code like this in production.
"""
from djask import Djask
from djask.admin import Admin
from djask.db import Model
from djask.auth.abstract import AbstractUser
import sqlalchemy as sa


class Post(Model):
    title = sa.Column(sa.String(255), index=True)
    content = sa.Column(sa.Text)
    author = sa.orm.relationship("User", back_populates="posts")
    author_id = sa.Column(sa.ForeignKey("user.id"))


class User(AbstractUser, Model):
    posts = sa.orm.relationship("Post", back_populates="author")


app = Djask(__name__, {"AUTH_MODEL": User})
admin_ext = Admin()  # initialize the admin site
admin_ext.init_app(app, mode="api")
db = app.db

app.config["AUTH_MODEL"] = User


@app.before_first_request
def init_db():
    db.drop_all()
    app.register_model(Post)
    db.create_all()
    admin = User(username="test", is_admin=True)
    admin.set_password("password")
    db.session.add(admin)
    db.session.commit()
    db.create_all()
