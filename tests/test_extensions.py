import pytest
from flask_bootstrap import Bootstrap5

from djask import Djask


@pytest.fixture
def app():
    app = Djask(__name__, {"TESTING": True, "WTF_CSRF_ENABLED": False})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_register_extensions(app):
    Bootstrap5(app)
    assert isinstance(app.extensions["bootstrap"], Bootstrap5)
