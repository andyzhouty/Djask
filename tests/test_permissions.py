import pytest
import sqlalchemy as sa

from djask.auth.models import Permission
from djask.auth.models import User
from djask.auth.permission import PermissionExistingWarning
from djask.db.models import Model
from djask.exceptions import ModelNotFoundError


class Post(Model):
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(127))
    content = sa.Column(sa.String(255))


def test_user_permissions(app):
    u = User(username="test")
    assert u.has_permission(Permission(Post, "read"))
    # specifying the table name directly
    assert u.has_permission(Permission("post", "read"))

    with pytest.raises(ModelNotFoundError):
        Permission("non-existing", "read")

    with pytest.warns(PermissionExistingWarning):
        u.add_permission(Permission(Post, "read"))
