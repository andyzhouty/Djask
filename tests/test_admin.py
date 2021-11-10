from flask_sqlalchemy import Model

from djask.blueprints import Blueprint
from djask.auth.models import User
from djask.extensions import db


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
    @admin.model
    class TestModel(Model):
        pass

    class TestModel2(Model):
        pass

    class TestModel3(Model):
        pass

    assert TestModel in admin.models

    rv = client.get("/admin/testmodel")
    assert rv.status_code == 200

    # Test the unregistered model
    rv = client.get("/admin/testmodel2")
    assert rv.status_code == 404

    admin.register_models([TestModel2, TestModel3])
    rv = client.get("/admin/testmodel2")
    assert rv.status_code == 200

    # Test if models are shown on main page
    rv = client.get("/admin/")
    rv_data = rv.get_data(as_text=True)
    assert "TestModel" in rv_data
    assert "User" in rv_data


def test_blueprints(admin, client):
    bp = Blueprint("bp", __name__)

    @bp.model
    class TestModel(Model):
        pass

    # test register a blueprint multiple times
    admin.register_blueprint(bp)
    admin.register_blueprint(bp, url_prefix="/bp/")

    print()

    rv = client.get("/admin/")
    rv_data = rv.get_data(as_text=True)
    assert "bp" in rv_data
    assert "TestModel" in rv_data
