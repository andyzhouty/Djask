from djask.db import Model


def test_new_model(app):
    @app.model
    class Test(Model):
        __table_args__ = {"extend_existing": True}

    assert "test" in str(app.spec).lower()
