import os.path as path
import typing as t

from flask import Blueprint, abort
from apiflask import APIFlask
from apiflask.exceptions import HTTPError

from .blueprints import Blueprint as DjaskBlueprint
from .extensions import bootstrap, compress, csrf, db
from .globals import current_app
from .mixins import ModelFunctionalityMixin
from .types import Config, ErrorResponse, ModelType


def _avoid_none(data: t.Any) -> t.Any:
    return data if data else ""


def _initialize_bootstrap_icons() -> str:
    if current_app.debug:  # pragma: no cover
        return "/djask/static/css/bootstrap-icons.css"
    return "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.0/font/bootstrap-icons.css"


class Djask(APIFlask, ModelFunctionalityMixin):
    """
    The djask object implements an APIFlask application and acts as a central object
    for all djask applications. You can refer to the flask documentation and the apiflask
    documentation for more detailed information.
    Note that config class or dict can be passed directly to the __init__ function.
    I achieved this by adding an optional argument named ``config`` to the argument list.

    .. versionadded:: 0.1.0
    :param swagger_path: The url path to swagger-ui web api documentation.
    :param redoc_path: The url path to redoc web api documentation.
    :param config: The config object for the application, can be a dict or another Python object.
    :param import_name: Exactly the same as the ``import_name`` parameter in :class:`~flask.Flask`.
    """

    blueprint_objects: t.List[Blueprint] = []

    def __init__(
        self,
        import_name: str,
        config: t.Optional[Config] = None,
        swagger_path: t.Optional[str] = "/api/docs",
        redoc_path: t.Optional[str] = "/api/redoc",
        *args,
        **kwargs,
    ):
        super().__init__(
            *[import_name, *args],
            **{"docs_path": swagger_path, "redoc_path": redoc_path, **kwargs},
        )

        # set default configuration for Djask.
        djask_default_config = dict(
            SECRET_KEY="djask_secret_key",  # CHANGE THIS!!!
            ADMIN_SITE=False,
            COMPRESS_LEVEL=9,
            COMPRESS_BR_LEVEL=9,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            DJASK_MODELS_PER_PAGE=8,
        )
        for k, v in djask_default_config.items():
            if self.config.get(k) is None:  # pragma: no cover
                self.config[k] = v
        if isinstance(config, dict):
            self.config.from_mapping(config)
        else:  # pragma: no cover
            self.config.from_object(config)

        self.template_folder = path.abspath(
            path.join(path.dirname(__file__), "templates")
        )
        self.jinja_env.globals["djask_bootstrap_icons"] = _initialize_bootstrap_icons

        self._register_extensions()
        self._register_static_files()

    def _register_extensions(self) -> None:
        """
        Register the built-in extensions.

        .. versionadded:: 0.1.0
        """
        for ext in (
            bootstrap,
            compress,
            csrf,
            db,
        ):
            ext.init_app(self)
        self.db = db

    def _register_static_files(self) -> None:
        """
        Register the built-in static files
        """
        static = Blueprint(
            "djask",
            __name__,
            static_folder="static",
            static_url_path="/djask" + self.static_url_path,
        )
        self.register_blueprint(blueprint=static)

    @staticmethod
    def _error_handler(error: HTTPError) -> ErrorResponse:
        """
        Override the default error handler in APIFlask.

        .. versionadded:: 0.1.0
        :param error: The error object.
        """
        status_code, message = (
            _avoid_none(error.status_code),
            _avoid_none(error.message),
        )
        detail: t.Union[t.Dict, t.Any] = error.detail
        body = f"{status_code} {message}{'<br />' + str(detail) if detail else ''}"
        return body, error.status_code, error.headers

    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None:
        """
        Bound blueprint objects to the app instead of strings

        .. versionadded:: 0.1.0
            :param blueprint: the blueprint object to register
            :param options: other options such as url_prefix
        """
        blueprint.register(self, options)
        conditions = [
            blueprint not in self.blueprint_objects,
            isinstance(blueprint, DjaskBlueprint),
        ]
        if all(conditions):
            self.blueprint_objects.append(blueprint)

    def get_model_by_name(self, name: str) -> ModelType:
        """
        Get a model registered by name.

        .. versionadded:: 0.2.0
            :param name: the model name to get
        """
        name = name.lower()
        models = self.models
        for bp in self.blueprint_objects:
            models.extend(bp.models)
        registered_models = [model.__name__.lower() for model in models]
        if name not in registered_models:
            abort(404, "Data model not defined or registered.")
        return models[registered_models.index(name)]
