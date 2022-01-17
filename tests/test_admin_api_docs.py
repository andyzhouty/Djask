from djask.db import Model
from djask.extensions import db


def test_new_model(app):
    @app.model
    class Test(Model):
        __table_args__ = {"extend_existing": True}

    print(app.spec)
    assert "test" in str(app.spec).lower()
