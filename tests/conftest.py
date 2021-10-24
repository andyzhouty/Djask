import warnings

import pytest

from djask import Djask


@pytest.fixture
def app():
    warnings.filterwarnings("ignore")
    app = Djask(__name__)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture
def client(app):
    return app.test_client()
