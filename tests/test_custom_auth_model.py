import sqlalchemy as sa
import pytest

from djask import Djask
from djask.auth.abstract import AbstractUser
from djask.db.models import Model
from djask.admin.ext import Admin
from .test_admin_api import admin_headers


class CustomUser(AbstractUser, Model):
    age = sa.Column(sa.Integer)
    articles = sa.orm.relationship("Article", back_populates="author")


class Article(Model):
    title = sa.Column(sa.String(255))
    author = sa.orm.relationship("CustomUser", back_populates="articles")
    author_id = sa.Column(sa.ForeignKey("customuser.id"))


@pytest.fixture
def new_client():
    app = Djask(
        __name__, {"TESTING": True, "WTF_CSRF_ENABLED": False, "AUTH_MODEL": CustomUser}
    )
    app.register_model(Article)
    ctx = app.app_context()
    ctx.push()
    admin_ext = Admin()
    admin_ext.init_app(app)

    db = app.db
    db.create_all()

    user = CustomUser(username="test", is_admin=True)
    user.age = 15
    user.set_password("test")
    db.session.add(user)
    db.session.commit()

    client = app.test_client()
    client.post("/admin/login", data={"username": "test", "password": "test"})
    yield client
    db.session.remove()
    db.drop_all()
    ctx.pop()


def test_user_age(new_client):
    resp = new_client.get("/admin/customuser/1")
    assert resp.status_code == 200
    rv_data = resp.get_data(as_text=True)
    assert "15" in rv_data


def test_post(new_client):
    new_client.post(
        "/admin/api/article",
        json={"title": "abc", "author_id": 1},
        headers=admin_headers(new_client),
    )
    p = Article.query.get(1)
    assert p.author == CustomUser.query.get(1)
