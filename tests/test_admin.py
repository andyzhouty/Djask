from flask_sqlalchemy import Model
from djask.admin.decorators import register


def test_admin_page(client):
    rv = client.get("/admin/")
    assert rv.status_code == 200


def test_register_model(app, client):
    @register
    class TestModel(Model):
        pass

    class TestModel2(Model):
        pass

    assert app.config["ADMIN_MODEL_MAP"]["testmodel"] == TestModel

    rv = client.get("/admin/testmodel")
    assert rv.status_code == 200

    # Test the unregistered model
    rv = client.get("/admin/testmodel2")
    assert rv.status_code == 404
