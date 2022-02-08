import pathlib
import shutil
from djask.auth.models import User
from djask.admin.cli import create_superuser
from djask.cli import create_app_command


def test_create_admin(app, runner):
    runner.invoke(create_superuser, ["--username", "test", "--password", "password"])
    u = User.query.filter_by(username="test").first()
    assert u.check_password("password")
    assert u.is_admin


def test_createapp(app, runner):
    runner.invoke(create_app_command, ["djaskr"])
    p = pathlib.Path("./djaskr")
    assert p.exists() and (p / "wsgi.py").exists()
    shutil.rmtree(p)
