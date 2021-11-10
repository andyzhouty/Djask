from djask.auth.models import User
from djask.admin.cli import create_superuser


def test_create_admin(app, runner):
    runner.invoke(create_superuser, ["--username", "test", "--password", "password"])
    u = User.query.filter_by(username="test").first()
    assert u.check_password("password")
    assert u.is_admin
