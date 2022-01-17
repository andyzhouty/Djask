"""
This app.py is just a simple demo. Do not write code like this in production.
"""
from djask import Djask
from djask.admin import Admin
from djask.db import Model
from djask.auth.models import User
import sqlalchemy as sa

app = Djask(__name__)
admin_ext = Admin()  # initialize the admin site
admin_ext.init_app(app)
db = app.db


class Post(Model):
    content = sa.Column(sa.Text)


@app.before_first_request
def init_db():
    app.register_model(Post)
    db.create_all()
    admin = User(username="test", is_admin=True)
    admin.set_password("password")
    db.session.add(admin)
    db.session.commit()
