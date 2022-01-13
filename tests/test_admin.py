from djask.admin.ext import Admin
from djask.auth.models import User
from djask.extensions import db


def test_no_admin(client):
    resp = client.get("/admin/")
    assert resp.status_code == 404


def test_admin_redirections(admin, client):
    client.get("/admin/logout")  # log out first
    resp = client.get("/admin/")
    assert resp.status_code == 302


def test_frontend_pages(admin, client):
    resp = client.get("/admin/login")
    assert resp.status_code == 200


def test_admin_login(admin, client):
    client.get("/admin/logout")  # log out first

    # add a user without admin access
    user = User(username="test2", is_admin=False)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()

    # wrong username
    resp = client.post(
        "/admin/login",
        data={"username": "wrong", "password": "test"},
        follow_redirects=True,
    )
    assert "User not found." in resp.get_data(as_text=True)

    # no admin access
    resp = client.post(
        "/admin/login",
        data={"username": "test2", "password": "test"},
        follow_redirects=True,
    )
    assert "User not administrative." in resp.get_data(as_text=True)

    # wrong password
    resp = client.post(
        "/admin/login",
        data={"username": "test", "password": "test2"},
        follow_redirects=True,
    )
    assert "Wrong password." in resp.get_data(as_text=True)


def test_admin_page(admin, client):
    resp = client.get("/admin/")
    assert resp.status_code == 200


def test_custom_prefix(app, client):
    app.config["ADMIN_PREFIX"] = "/abcd"
    admin_ext = Admin()
    admin_ext.init_app(app)
    db = app.db
    user = User(username="test", is_admin=True)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()

    client.post("/abcd/login", data={"username": "test", "password": "test"})
