import typing as t

from flask.testing import FlaskClient
from djask.auth.models import User
from djask.extensions import db
from djask.db import Model


def admin_headers(
    client,
    username: t.Optional[str] = "test",
    password: t.Optional[str] = "test",
):
    resp = client.post(
        "/admin/api/token",
        data={
            "username": username,
            "password": password,
        },
    )
    token = resp.get_json()["access_token"]
    return {
        "Authorization": token,
        "Accept": "application/json",
    }


def test_token(admin, client):
    resp = client.post(
        "/admin/api/token",
        data={
            "username": "test",
            "password": "wrong",
        },
    )
    assert resp.status_code == 400
    resp = client.post(
        "/admin/api/token",
        data={
            "username": "test",
            "password": "test",
        },
    )
    assert resp.status_code == 200


def test_get_user(admin, client):
    u = User.query.filter_by(username="test").first()
    resp = client.get(f"/admin/api/user/{u.id}", headers=admin_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "test"


def test_update_user(admin, client):
    u = User.query.filter_by(username="test").first()
    resp = client.put(
        f"/admin/api/user/{u.id}",
        json={"username": "abc"},
        headers=admin_headers(client),
    )
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "abc"


def test_delete_user(admin, client):
    u = User.query.filter_by(username="test").first()
    resp = client.delete(f"/admin/api/user/{u.id}", headers=admin_headers(client))
    assert resp.status_code == 204
    assert User.query.filter_by(username="test").count() == 0


def test_new_model(admin, client):
    @admin.model
    class Post(Model):
        title = db.Column(db.String(255))
        content = db.Column(db.Text)

    db.create_all()
    p = Post(title="abc", content="lorem ipsum")
    db.session.add(p)
    db.session.commit()

    resp = client.get(f"/admin/api/post/{p.id}", headers=admin_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "abc"

    resp = client.put(
        f"/admin/api/post/{p.id}",
        json={"title": "new"},
        headers=admin_headers(client),
    )
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "new"

    # test bad request
    resp = client.put(
        f"/admin/api/post/{p.id}",
        json={"lorem": "ipsum"},
        headers=admin_headers(client),
    )
    assert resp.status_code == 400

    resp = client.delete(f"/admin/api/post/{p.id}", headers=admin_headers(client))
    assert resp.status_code == 204
    assert Post.query.get(p.id) is None


def test_model_not_existing(admin, client):
    resp = client.get(f"/admin/api/fake/1", headers=admin_headers(client))
    assert resp.status_code == 404
