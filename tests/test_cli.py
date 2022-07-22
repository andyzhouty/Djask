import os
import pathlib
import shutil

from djask.admin.cli import create_superuser
from djask.auth.models import User
from djask.cli import create_app_command
from djask.cli import create_bp_command
from djask.exceptions import AppDirectoryNotFoundError


def test_create_admin(app, runner):
    runner.invoke(create_superuser, ["--username", "test", "--password", "password"])
    u = User.query.filter_by(username="test").first()
    assert u.check_password("password")
    assert u.is_admin


def test_create_app(app, runner):
    with runner.isolated_filesystem():
        runner.invoke(create_app_command, ["djaskr"])
        p = pathlib.Path("./djaskr")
        assert p.exists() and (p / "wsgi.py").exists()
        shutil.rmtree(p)


def test_create_blueprint(app, runner):
    with runner.isolated_filesystem():
        runner.invoke(create_app_command, ["djaskr2"])
        os.chdir("djaskr2")

        runner.invoke(create_bp_command, ["test"])
        p_ = pathlib.Path("djaskr2/test")
        assert p_.exists() and (p_ / "__init__.py").exists()
        shutil.rmtree(p_)

        print("here")
        os.remove("wsgi.py")
        result = runner.invoke(create_bp_command, ["test"])
        assert isinstance(result.exception, FileNotFoundError)

        open("wsgi.py", "w+").close()

        shutil.rmtree("djaskr2")
        result = runner.invoke(create_bp_command, ["test"])
        assert isinstance(result.exception, AppDirectoryNotFoundError)
