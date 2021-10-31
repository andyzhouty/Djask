import pytest

from flask_sqlalchemy import Model

from djask.auth.models import User
from djask.admin.decorators import register
from djask.admin.ext import Admin
from djask.extensions import db

admin_ext = Admin()


@pytest.fixture
def admin(app, client):
    admin_ext.init_app(app)
    db.create_all()
    user = User(username="test", is_admin=True)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()

    rv = client.post("/admin/login", data={"username": "test", "password": "test"})
    return app


def test_no_admin(client):
    rv = client.get("/admin/")
    assert rv.status_code == 404


def test_admin_redirections(admin, client):
    client.get("/admin/logout")  # log out first
    rv = client.get("/admin/")
    assert rv.status_code == 302


def test_frontend_pages(admin, client):
    rv = client.get("/admin/login")
    assert rv.status_code == 200


def test_admin_login(admin, client):
    client.get("/admin/logout")  # log out first

    user = User(username="test2", is_admin=False)  # add a user without admin access
    user.set_password("test")
    db.session.add(user)
    db.session.commit()

    # wrong username
    rv = client.post(
        "/admin/login",
        data={"username": "wrong", "password": "test"},
        follow_redirects=True,
    )
    assert "User not found." in rv.get_data(as_text=True)

    # no admin access
    rv = client.post(
        "/admin/login",
        data={"username": "test2", "password": "test"},
        follow_redirects=True,
    )
    assert "User not administrative." in rv.get_data(as_text=True)

    # wrong password
    rv = client.post(
        "/admin/login",
        data={"username": "test", "password": "test2"},
        follow_redirects=True,
    )
    assert "Wrong password." in rv.get_data(as_text=True)


def test_admin_page(admin, client):
    rv = client.get("/admin/")
    assert rv.status_code == 200


def test_register_model(admin, client):
    @register
    class TestModel(Model):
        pass

    class TestModel2(Model):
        pass

    assert TestModel in admin.config["ADMIN_MODELS"]

    rv = client.get("/admin/testmodel")
    assert rv.status_code == 200

    # Test the unregistered model
    rv = client.get("/admin/testmodel2")
    assert rv.status_code == 404


def test_user_model(admin, client):
    from djask.auth.models import User

    # Test User model
    u = User()
    u.set_password("test")
    assert u.check_password("test")
    admin_ext.register_model(User)

    rv = client.get("/admin/user")
    assert rv.status_code == 200


def test_register_models(admin, client):
    from djask.auth.models import User

    class TestModel(Model):
        ...

    admin_ext.register_models(TestModel, User)
    rv = client.get("/admin/testmodel")
    assert rv.status_code == 200
    rv = client.get("/admin/user")
    assert rv.status_code == 200
