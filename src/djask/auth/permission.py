from typing import Union

from ..exceptions import ModelNotFoundError
from ..extensions import db
from ..types import ModelType


class Permission(str):
    """
    The permission model for djask users.

    .. versionadded:: 0.7.0

    :param model: The
    :type model: Union[str, ModelType]
    :param permission_name: _description_
    :type permission_name: str
    :raises ModelNotFoundError: _description_
    :raises TableNameAsciiExpectedError: _description_
    :return: _description_
    :rtype: str | NoReturn
    """

    def __new__(
        cls, model: Union[str, ModelType], permission_name: str
    ) -> "Permission":
        if isinstance(model, str):
            model_found = model in (
                mapper.class_.__tablename__ for mapper in db.Model.registry.mappers
            )

            if not model_found:
                raise ModelNotFoundError(model)

            return super().__new__(cls, f"{model}_{permission_name}")

        return super().__new__(cls, model.__tablename__ + f"_{permission_name}")


class PermissionExistingWarning(Warning):
    """Warn user if adding an permission that they already have"""

    def __init__(self, username: str, perm: Permission):
        super().__init__(f"<User '{username}'> already has <Permission '{perm}'>")
