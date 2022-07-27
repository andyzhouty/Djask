import pytest

from djask.auth.anonymous import AnonymousUser
from djask.auth.anonymous import NoDBForAnonymousError


def test_anonymous(client):
    user = AnonymousUser()
    assert not user.is_admin
    for method in ("set_password", "check_password"):
        with pytest.raises(NoDBForAnonymousError):
            getattr(user, method)("password")
    with pytest.raises(NoDBForAnonymousError):
        user.delete()
