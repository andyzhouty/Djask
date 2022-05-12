import pytest

from djask.admin.ext import Admin
from djask.admin.ext import AdminModeError
from djask.auth.models import User
from djask.db.models import Model


@pytest.fixture
def app_with_user(app):
    user = User(username="test", is_admin=True)
    user.set_password("test")
    app.db.session.add(user)
    app.db.session.commit()
    return app


def test_ui(app_with_user, client):
    app = app_with_user

    @app.model
    class TestModel(Model):
        __table_args__ = {"extend_existing": True}

    app.db.create_all()

    Admin(app, mode="ui")
    resp = client.post(
        "/admin/api/token",
        data={
            "username": "test",
            "password": "test",
        },
    )
    assert resp.status_code == 404

    resp = client.post(
        "/admin/login",
        data={"username": "test", "password": "test"},
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_api(app_with_user, client):
    app = app_with_user

    Admin(app, mode="api")
    resp = client.post(
        "/admin/api/token",
        data={
            "username": "test",
            "password": "test",
        },
    )
    assert resp.status_code == 200

    resp = client.get("/admin/login")
    assert resp.status_code == 404


def test_empty(app):
    with pytest.raises(AdminModeError):
        Admin(app, mode=[])
