import warnings

import pytest

from djask import Djask
from djask.admin import Admin
from djask.auth.models import User


@pytest.fixture(scope="class")
def app():
    app = Djask(__name__, {"TESTING": True, "WTF_CSRF_ENABLED": False})
    ctx = app.app_context()
    ctx.push()
    db = app.db
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def admin(app, client):
    admin_ext = Admin()
    admin_ext.init_app(app)
    db = app.db
    user = User(username="test", is_admin=True)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/admin/login", data={"username": "test", "password": "test"})
    yield app


@pytest.fixture
def runner(app):
    yield app.test_cli_runner()
