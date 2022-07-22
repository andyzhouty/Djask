import os
import os.path as path
import typing as t

from apiflask import APIFlask
from apiflask.exceptions import HTTPError
from apispec import APISpec
from flask import abort
from flask import Blueprint
from flask.helpers import get_debug_flag
from flask.helpers import get_env
from flask.helpers import get_load_dotenv

from . import cli
from .auth.abstract import AbstractUser
from .blueprints import Blueprint as DjaskBlueprint
from .exceptions import AuthModelInvalid
from .extensions import bootstrap
from .extensions import compress
from .extensions import csrf
from .extensions import db
from .extensions import login_manager
from .globals import current_app as current_app
from .globals import g as g
from .globals import request as request  # noqa
from .globals import session as session  # noqa
from .mixins import ModelFunctionalityMixin
from .types import Config
from .types import ErrorResponse
from .types import ModelType


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
        swagger_path: t.Optional[str] = "/admin/api/docs",
        redoc_path: t.Optional[str] = "/admin/api/redoc",
        title: t.Optional[str] = "Djask API",
        version: t.Optional[str] = "0.1.0",
        *args,
        **kwargs,
    ):
        super().__init__(
            *(
                import_name,
                *args,
            ),
            **{  # type: ignore
                "docs_path": swagger_path,
                "redoc_path": redoc_path,
                "title": title,
                "version": version,
                **kwargs,
            },
        )  # type: ignore

        # set default configuration for Djask.
        djask_default_config = dict(
            SECRET_KEY="djask_secret_key",  # CHANGE THIS!!!
            ADMIN_SITE=False,
            COMPRESS_LEVEL=9,
            COMPRESS_BR_LEVEL=9,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            DJASK_MODELS_PER_PAGE=8,
            DOCS_FAVICON="/djask" + (self.static_url_path or "") + "/icon/djask.ico",
        )
        for k, v in djask_default_config.items():
            self.config[k] = v
        if isinstance(config, dict):
            self.config.from_mapping(config)
        else:  # pragma: no cover
            self.config.from_object(config)

        if self.config.get("AUTH_MODEL") is None:
            from .auth.models import User

            self.config["AUTH_MODEL"] = User
        elif not isinstance(
            self.config.get("AUTH_MODEL"), type(AbstractUser)
        ):  # pragma: no cover
            raise AuthModelInvalid

        self.jinja_env.globals["djask_bootstrap_icons"] = _initialize_bootstrap_icons

        self._register_extensions()
        self._register_static_files()
        self._register_global_user_model()

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
            login_manager,
        ):
            ext.init_app(self)
        self.db = db
        self.login_manager = login_manager

    def _register_static_files(self) -> None:
        """Register the built-in static files

        .. versionadded:: 0.1.0
        """
        static = Blueprint(
            "djask",
            __name__,
            static_folder="static",
            static_url_path="/djask" + (self.static_url_path or ""),
            template_folder=path.abspath(
                path.join(path.dirname(__file__), "templates")
            ),
        )
        self.register_blueprint(blueprint=static)

    def _register_global_user_model(self) -> None:
        """Make a shortcut to the ``app.config["AUTH_MODEL"]``

        .. versionadded:: 0.3.0
        """

        @self.before_request
        def before_request():
            g.User = self.config["AUTH_MODEL"]

    @staticmethod
    def _error_handler(error: HTTPError) -> ErrorResponse:
        """Override the default error handler in APIFlask.

        .. versionadded:: 0.1.0
        :param error: The error object.
        """
        status_code, message = tuple(
            map(lambda x: x if x else "", (error.status_code, error.message))
        )
        detail: t.Union[t.Dict, t.Any] = error.detail
        body = "{} {}<br /> {}".format(
            status_code, message, str(detail) if detail else ""
        )
        return body, error.status_code, error.headers  # type: ignore

    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None:
        """Bind blueprint objects to the app instead of strings

        .. versionadded:: 0.1.0
        .. versionchanged:: 0.3.2
            :param blueprint: the blueprint object to register
            :param options: other options such as url_prefix
        """
        # register the built-in bootstrap blueprint as `djask_bootstrap`.
        if (
            blueprint.name == "bootstrap"
            and "bootstrap" not in self.blueprint_objects
            and "djask_bootstrap" not in self.blueprints
        ):
            blueprint.name = "djask_bootstrap"  # add a prefix to the blueprint
        super().register_blueprint(blueprint, **options)
        conditions = [
            blueprint not in self.blueprint_objects,
            isinstance(blueprint, DjaskBlueprint),
        ]
        if all(conditions):
            self.blueprint_objects.append(blueprint)

    def get_model_by_name(self, name: str) -> ModelType:
        """Get a model registered by name.

        .. versionadded:: 0.2.0
            :param name: the model name to get
        """
        name = name.lower()
        models = self.models
        for bp in self.blueprint_objects:
            models.extend(bp.models)  # type: ignore
        registered_models = [model.__name__.lower() for model in models]
        if name not in registered_models:
            abort(404, "Data model not defined or registered.")
        return models[registered_models.index(name)]

    def run(
        self,
        host: t.Optional[str] = None,
        port: t.Optional[int] = None,
        debug: t.Optional[bool] = None,
        load_dotenv: bool = True,
        **options: t.Any,
    ):  # pragma: no cover
        """Runs the application on a local development server.

        Do not use ``run()`` in a production setting. It is not intended to
        meet security and performance requirements for a production server.
        Instead, see :doc:`/deploying/index` for WSGI server recommendations.

        If the :attr:`debug` flag is set the server will automatically reload
        for code changes and show a debugger in case an exception happened.

        If you want to run the application in debug mode, but disable the
        code execution on the interactive debugger, you can pass
        ``use_evalex=False`` as parameter.  This will keep the debugger's
        traceback screen active, but disable code execution.

        It is not recommended to use this function for development with
        automatic reloading as this is badly supported.  Instead you should
        be using the :command:`djask` command line script's ``run`` support.
        """
        if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
            from flask.debughelpers import explain_ignored_app_run

            explain_ignored_app_run()
            return

        if get_load_dotenv(load_dotenv):
            cli.load_dotenv()

            # if set, let env vars override previous values
            if "FLASK_ENV" in os.environ:
                self.env = get_env()
                self.debug = get_debug_flag()
            elif "FLASK_DEBUG" in os.environ:
                self.debug = get_debug_flag()

        # debug passed to method overrides all other sources
        if debug is not None:
            self.debug = bool(debug)

        server_name = self.config.get("SERVER_NAME")
        sn_host = sn_port = None

        if server_name:
            sn_host, _, sn_port = server_name.partition(":")

        if not host:
            if sn_host:
                host = sn_host
            else:
                host = "127.0.0.1"

        if port or port == 0:
            port = int(port)
        elif sn_port:
            port = int(sn_port)
        else:
            port = 5000

        options.setdefault("use_reloader", self.debug)
        options.setdefault("use_debugger", self.debug)
        options.setdefault("threaded", True)

        cli.show_server_banner(self.env, self.debug, self.name, False)

        from werkzeug.serving import run_simple

        try:
            run_simple(t.cast(str, host), port, self, **options)
        finally:
            # reset the first request information if the development server
            # reset normally.  This makes it possible to restart the server
            # without reloader and that stuff from an interactive shell.
            self._got_first_request = False

    def _generate_spec(self) -> APISpec:
        """Add data models to the spec.

        .. versionadded:: 0.3.0
        """
        # call parental _generate_spec
        spec = super()._generate_spec()
        # get the prefix
        custom_prefix = self.config.get("ADMIN_PREFIX")
        prefix = custom_prefix if isinstance(custom_prefix, str) else "/admin"

        for m in set(self.models):
            m_name = m.__name__

            # register the schema to spec
            spec.components.schema(m_name, schema=m.to_schema())

            # define some common parameters, responses, etc.
            not_found = {
                "content": {"application/json": {"schema": "HTTPError"}},
                "description": "Not found",
            }
            bad_request = {
                "content": {"application/json": {"schema": "ValidationError"}},
                "description": "Validation error",
            }
            parameter_model_id = {
                "in": "path",
                "name": f"{m_name.lower()}_id",
                "schema": {"type": "integer"},
                "required": True,
            }
            response_model_schema = {
                "content": {"application/json": {"schema": m_name}}
            }
            tag = "Admin_Api.Models"
            # register the url route
            spec.path(
                path="{0}/api/{1}/{{{1}_id}}".format(prefix, m_name.lower()),
                operations=dict(
                    get=dict(
                        parameters=[parameter_model_id],
                        responses={
                            "200": response_model_schema,
                            "404": not_found,
                            "400": bad_request,
                        },
                        tags=[tag],
                        summary=f"returns a {m_name.lower()}",
                    ),
                    put=dict(
                        parameters=[parameter_model_id],
                        requestBody={
                            "content": {"application/json": {"schema": m_name}}
                        },
                        responses={
                            "200": response_model_schema,
                            "404": not_found,
                            "400": bad_request,
                        },
                        tags=[tag],
                        summary=f"updates a {m_name.lower()}",
                    ),
                    delete=dict(
                        parameters=[parameter_model_id],
                        responses={
                            "204": {"description": "Successful response"},
                            "404": not_found,
                        },
                        tags=[tag],
                        summary=f"deletes a {m_name.lower()}",
                    ),
                ),
                description=f"Operate on {m_name}",
            ).path(
                path=f"{prefix}/api/{m_name.lower()}",
                operations=dict(
                    post=dict(
                        requestBody={
                            "content": {"application/json": {"schema": m_name}}
                        },
                        responses={
                            "201": response_model_schema,
                            "400": bad_request,
                        },
                        tags=[tag],
                        summary=f"creates a {m_name.lower()}",
                    )
                ),
            )
        return spec
