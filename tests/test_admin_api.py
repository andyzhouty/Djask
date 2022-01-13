import typing as t

from djask.auth.models import User
from djask.extensions import db


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
