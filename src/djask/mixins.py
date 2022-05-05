import typing as t

from djask.db.models import Model
from .types import ModelList, ModelType
from .exceptions import ModelTypeError


class ModelFunctionalityMixin:
    """
    A mixin that adds some SQL functionalities to the classes which inherit it.
    Those classes which inherit it are expected to be subclasses
    of :class:`~flask.Blueprint` or :class:`~flask.Flask`.


    .. versionadded:: 0.1.0

    .. versionchanged:: 0.4.0
    """

    models: ModelList = []

    def model(self, model: ModelType) -> ModelType:
        """
        A decorator to register a database model directly to the app.

        .. versionadded:: 0.1.0
        :param model: The database model to wrap.
        """
        self.register_model(model)
        return model

    def register_model(self, model: ModelType) -> None:
        """
        Register a model.

        :param model: The model to register
        :return: None
        """
        if not isinstance(model, type(Model)):
            raise ModelTypeError
        self.models.append(model)

    def register_models(self, models: t.Iterable[ModelType]) -> None:
        """
        Register multiple models at a time.

        :param models: The models to register
        :return: None
        """
        for model in models:
            self.register_model(model)
