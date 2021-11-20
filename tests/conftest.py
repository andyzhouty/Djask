import warnings

import pytest

from djask import Djask
from djask.admin import Admin
from djask.auth.models import User


@pytest.fixture
def app():
    warnings.filterwarnings("ignore")
    app = Djask(__name__, {"TESTING": True, "WTF_CSRF_ENABLED": False})
    app.config["TESTING"] = True
    ctx = app.app_context()
    ctx.push()
    app.db.create_all()
    yield app
    app.db.drop_all()
    ctx.pop()


@pytest.fixture
def client(app):
    return app.test_client()


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
    return app


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
