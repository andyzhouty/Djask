from djask.admin.ext import Admin
from djask.auth.models import User
from djask.extensions import db


def test_no_admin(client):
    rv = client.get("/admin/")
    assert rv.status_code == 404


def test_admin_redirections(admin, client):
    client.get("/admin/logout")  # log out first
    rv = client.get("/admin/")
    assert rv.status_code == 302


def test_frontend_pages(admin, client):
    rv = client.get("/admin/login")
    assert rv.status_code == 200


def test_admin_login(admin, client):
    client.get("/admin/logout")  # log out first

    # add a user without admin access
    user = User(username="test2", is_admin=False)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()

    # wrong username
    rv = client.post(
        "/admin/login",
        data={"username": "wrong", "password": "test"},
        follow_redirects=True,
    )
    assert "User not found." in rv.get_data(as_text=True)

    # no admin access
    rv = client.post(
        "/admin/login",
        data={"username": "test2", "password": "test"},
        follow_redirects=True,
    )
    assert "User not administrative." in rv.get_data(as_text=True)

    # wrong password
    rv = client.post(
        "/admin/login",
        data={"username": "test", "password": "test2"},
        follow_redirects=True,
    )
    assert "Wrong password." in rv.get_data(as_text=True)


def test_admin_page(admin, client):
    rv = client.get("/admin/")
    assert rv.status_code == 200


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
