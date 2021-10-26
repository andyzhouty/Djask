import pytest

from flask_sqlalchemy import Model

from djask.admin.decorators import register
from djask.admin.ext import Admin

admin_ext = Admin()


@pytest.fixture
def admin(app):
    admin_ext.init_app(app)
    return app


def test_no_admin(client):
    rv = client.get("/admin/")
    assert rv.status_code == 404


def test_admin_page(admin, client):
    rv = client.get("/admin/")
    assert rv.status_code == 200


def test_register_model(admin, client):
    @register
    class TestModel(Model):
        pass

    class TestModel2(Model):
        pass

    assert admin.config["ADMIN_MODEL_MAP"]["testmodel"] == TestModel

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
