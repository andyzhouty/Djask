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


def test_create_user(admin, client):
    resp = client.post(
        f"/admin/api/user",
        headers=admin_headers(client),
        json={"username": "abc", "password": "abc"},
    )
    assert resp.status_code == 201


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
    
    resp = client.put(
        f"/admin/api/user/{u.id}",
        json={"password": "new"},
        headers=admin_headers(client, username="abc")
    )
    assert resp.status_code == 200
    assert u.check_password("new")    


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
    resp = client.post(
        f"/admin/api/post",
        headers=admin_headers(client),
        json={
            "title": "abc",
            "content": "lorem ipsum",
        },
    )
    assert resp.status_code == 201
    p = Post.query.filter_by(title="abc").first()
    assert not (p is None)

    resp = client.post(
        f"/admin/api/post",
        headers=admin_headers(client),
        json={"title": "xyz", "content": "lorem ipsum", "unexpected": "data"},
    )
    assert resp.status_code == 400
    p2 = Post.query.filter_by(title="xyz").first()
    assert p2 is None

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
