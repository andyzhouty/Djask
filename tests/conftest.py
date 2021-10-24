import os

import pytest

from djask import Djask


@pytest.fixture
def app():
    app = Djask(__name__)
    return app


@pytest.fixture
def client(app):
    return app.test_client()
