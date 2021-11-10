from flask import Blueprint as Bp
from apiflask import APIBlueprint as APIBp

from .mixins import ModelFunctionalityMixin


class Blueprint(Bp, ModelFunctionalityMixin):
    """
    Flask's :class:`~flask.Blueprint` object with some SQL support.
    """

    pass


class APIBlueprint(APIBp, ModelFunctionalityMixin):  # pragma: no cover
    """
    APIFlask's ``APIBlueprint`` object with some SQL support.
    """

    pass
