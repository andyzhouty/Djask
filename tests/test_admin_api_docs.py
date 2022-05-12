from djask.db import Model


def test_new_model(app):
    @app.model
    class Test(Model):
        pass

    assert "test" in str(app.spec).lower()
