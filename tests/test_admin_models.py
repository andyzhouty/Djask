from djask import Blueprint
from djask.auth.models import User
from djask.db.models import Model
from djask.extensions import db


def test_register_model(admin, client):
    @admin.model
    class TestModel(Model):
        pass

    class TestModel2(Model):
        pass

    class TestModel3(Model):
        pass

    assert TestModel in admin.models
    db.create_all()

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


def test_model_schema(admin, client):
    rv = client.get("/admin/User")
    assert rv.status_code == 200
    rv_data = rv.get_data(as_text=True)
    assert "id" in rv_data
    assert str(User.query.get(1).created_at)[:4] in rv_data


def test_blueprints(admin, client):
    bp = Blueprint("bp", __name__)

    @bp.model
    class TestModel(Model):
        __table_args__ = {"extend_existing": True}
        pass

    assert TestModel in bp.models
    db.create_all()
    # Test register a blueprint multiple times
    admin.register_blueprint(bp)
    admin.register_blueprint(bp, url_prefix="/bp/")

    rv = client.get("/admin/")
    rv_data = rv.get_data(as_text=True)
    assert "bp" in rv_data
    assert "TestModel" in rv_data

    rv = client.get("/admin/TestModel")
    assert rv.status_code == 200


def test_model_add(admin, client):
    rv = client.get("/admin/user/add")
    assert rv.status_code == 200

    rv = client.post(
        "/admin/user/add",
        data=dict(username="123", password="abcd", email="test@example.com"),
        follow_redirects=True,
    )
    assert rv.status_code == 200
    u = User.query.filter_by(username="123").first()
    assert u is not None
    assert u.check_password("abcd")


def test_model_edit(admin, client):
    rv = client.get("/admin/user/1/edit")
    assert rv.status_code == 200

    rv = client.post(
        "/admin/user/1/edit",
        data=dict(username="123", password="test"),
        follow_redirects=True,
    )
    assert rv.status_code == 200
    u = User.query.get(1)
    assert u.username == "123"
    assert u.check_password("test")

    rv = client.get("/admin/user/10")
    assert rv.status_code == 404
    assert "id 10 not found" in rv.get_data(as_text=True)
