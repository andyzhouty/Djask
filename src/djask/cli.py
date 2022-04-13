"""This file is nearly the same as flask.cli except for some modifications."""
import ast
import inspect
import os
import platform
import re
import sys
import traceback
from functools import update_wrapper

import click

import flask
from flask.cli import (
    locate_app,
    prepare_import,
    _called_with_wrong_args,
    _validate_key,
)
from flask.cli import (
    DispatchingApp,
    ScriptInfo as FlaskScriptInfo,
    FlaskGroup,
    AppGroup,
    CertParamType,
    SeparatedPathType,
    NoAppException,
)
from flask.cli import (
    routes_command,
)
from flask.helpers import get_debug_flag
from flask.helpers import get_env
from flask.helpers import get_load_dotenv

from .custom_commands import create_app_command


try:
    import dotenv
except ImportError:
    dotenv = None


def find_best_app(module):
    """Given a module instance this tries to find the best possible
    application in the module or raises an exception.
    """
    from . import Djask

    # Search for the most common names first.
    for attr_name in ("app", "application"):
        app = getattr(module, attr_name, None)

        if isinstance(app, Djask):
            return app

    # Otherwise find the only object that is a Djask instance.
    matches = [v for v in module.__dict__.values() if isinstance(v, Djask)]

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise NoAppException(
            "Detected multiple Djask applications in module"
            f" {module.__name__!r}. Use 'DJASK_APP={module.__name__}:name'"
            f" to specify the correct one."
        )

    # Search for app factory functions.
    for attr_name in ("create_app", "make_app"):
        app_factory = getattr(module, attr_name, None)

        if inspect.isfunction(app_factory):
            try:
                app = app_factory()

                if isinstance(app, Djask):
                    return app
            except TypeError as e:
                if not _called_with_wrong_args(app_factory):
                    raise

                raise NoAppException(
                    f"Detected factory {attr_name!r} in module {module.__name__!r},"
                    " but could not call it without arguments. Use"
                    f" \"DJASK_APP='{module.__name__}:{attr_name}(args)'\""
                    " to specify arguments."
                ) from e

    raise NoAppException(
        "Failed to find Djask application or factory in module"
        f" {module.__name__!r}. Use 'DJASK_APP={module.__name__}:name'"
        " to specify one."
    )


def find_app_by_string(module, app_name):
    """Check if the given string is a variable name or a function. Call
    a function to get the app instance, or return the variable directly.
    """
    from . import Djask

    # Parse app_name as a single expression to determine if it's a valid
    # attribute name or function call.
    try:
        expr = ast.parse(app_name.strip(), mode="eval").body
    except SyntaxError:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        ) from None

    if isinstance(expr, ast.Name):
        name = expr.id
        args = []
        kwargs = {}
    elif isinstance(expr, ast.Call):
        # Ensure the function name is an attribute name only.
        if not isinstance(expr.func, ast.Name):
            raise NoAppException(
                f"Function reference must be a simple name: {app_name!r}."
            )

        name = expr.func.id

        # Parse the positional and keyword arguments as literals.
        try:
            args = [ast.literal_eval(arg) for arg in expr.args]
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in expr.keywords}
        except ValueError:
            # literal_eval gives cryptic error messages, show a generic
            # message with the full expression instead.
            raise NoAppException(
                f"Failed to parse arguments as literal values: {app_name!r}."
            ) from None
    else:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        )

    try:
        attr = getattr(module, name)
    except AttributeError as e:
        raise NoAppException(
            f"Failed to find attribute {name!r} in {module.__name__!r}."
        ) from e

    # If the attribute is a function, call it with any args and kwargs
    # to get the real application.
    if inspect.isfunction(attr):
        try:
            app = attr(*args, **kwargs)
        except TypeError as e:
            if not _called_with_wrong_args(attr):
                raise

            raise NoAppException(
                f"The factory {app_name!r} in module"
                f" {module.__name__!r} could not be called with the"
                " specified arguments."
            ) from e
    else:
        app = attr

    if isinstance(app, Djask):
        return app

    raise NoAppException(
        "A valid Djask application was not obtained from"
        f" '{module.__name__}:{app_name}'."
    )


def get_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    import werkzeug
    from . import __version__

    click.echo(
        f"Python {platform.python_version()}\n"
        f"Werkzeug {werkzeug.__version__}\n"
        f"Flask {flask.__version__}\n"
        f"Djask {__version__}\n",
        color=ctx.color,
    )
    ctx.exit()


version_option = click.Option(
    ["--version"],
    help="Show the djask version",
    expose_value=False,
    callback=get_version,
    is_flag=True,
    is_eager=True,
)


class ScriptInfo(FlaskScriptInfo):
    """Helper object to deal with Djask applications.  This is usually not
    necessary to interface with as it's used internally in the dispatching
    to click.  In future versions of Flask this object will most likely play
    a bigger role.  Typically it's created automatically by the
    :class:`DjaskGroup` but you can also manually create it and pass it
    onwards as click object.
    """

    def __init__(self, *args, **kwargs):
        os.environ["FLASK_APP"] = (
            os.environ.get("DJASK_APP") or os.environ.get("FLASK_APP") or ""
        )
        super().__init__(*args, **kwargs)

    def load_app(self):
        """Loads the Djask app (if not yet loaded) and returns it.  Calling
        this multiple times will just result in the already loaded app to
        be returned.
        """
        __traceback_hide__ = True  # noqa: F841

        if self._loaded_app is not None:
            return self._loaded_app

        if self.create_app is not None:
            app = self.create_app()
        else:
            if self.app_import_path:
                path, name = (
                    re.split(r":(?![\\/])", self.app_import_path, 1) + [None]
                )[:2]
                import_name = prepare_import(path)
                app = locate_app(import_name, name)
            else:
                for path in ("wsgi.py", "app.py"):
                    import_name = prepare_import(path)
                    app = locate_app(import_name, None, raise_if_not_found=False)

                    if app:
                        break

        if not app:
            raise NoAppException(
                "Could not locate a Djask application. You did not provide "
                'the "DJASK_APP" environment variable, and a "wsgi.py" or '
                '"app.py" module was not found in the current directory.'
            )

        if self.set_debug_flag:
            # Update the app's debug flag through the descriptor so that
            # other values repopulate as well.
            app.debug = get_debug_flag()

        self._loaded_app = app
        return app

    def list_commands(self, ctx):
        self._load_plugin_commands()
        # Start with the built-in and plugin commands.
        rv = set(super().list_commands(ctx))
        info = ctx.ensure_object(ScriptInfo)

        # Add commands provided by the app, showing an error and
        # continuing if the app couldn't be loaded.
        try:
            rv.update(info.load_app().cli.list_commands(ctx))
        except NoAppException as e:
            # When an app couldn't be loaded, show the error message
            # without the traceback.
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")
        except Exception:
            # When any other errors occurred during loading, show the
            # full traceback.
            click.secho(f"{traceback.format_exc()}\n", err=True, fg="red")

        return sorted(rv)

    def main(self, *args, **kwargs):
        # Set a global flag that indicates that we were invoked from the
        # command line interface. This is detected by Flask.run to make the
        # call into a no-op. This is necessary to avoid ugly errors when the
        # script that is loaded here also attempts to start a server.
        os.environ["FLASK_RUN_FROM_CLI"] = "true"
        os.environ["DJASK_RUN_FROM_CLI"] = "true"

        if get_load_dotenv(self.load_dotenv):
            load_dotenv()

        obj = kwargs.get("obj")

        if obj is None:
            obj = ScriptInfo(
                create_app=self.create_app, set_debug_flag=self.set_debug_flag
            )

        kwargs["obj"] = obj
        kwargs.setdefault("auto_envvar_prefix", "DJASK")
        return super().main(*args, **kwargs)


pass_script_info = click.make_pass_decorator(ScriptInfo, ensure=True)


def with_appcontext(f):
    """Wraps a callback so that it's guaranteed to be executed with the
    script's application context.  If callbacks are registered directly
    to the ``app.cli`` object then they are wrapped with this function
    by default unless it's disabled.
    """

    @click.pass_context
    def decorator(__ctx, *args, **kwargs):
        with __ctx.ensure_object(ScriptInfo).load_app().app_context():
            return __ctx.invoke(f, *args, **kwargs)

    return update_wrapper(decorator, f)


class DjaskGroup(FlaskGroup):
    """Special subclass of the :class:`AppGroup` group that supports
    loading more commands from the configured Djask app.  Normally a
    developer does not have to interface with this class but there are
    some very advanced use cases for which it makes sense to create an
    instance of this.

    :param add_default_commands: if this is True then the default run and
        shell commands will be added.
    :param add_version_option: adds the ``--version`` option.
    :param create_app: an optional callback that is passed the script info and
        returns the loaded app.
    :param load_dotenv: Load the nearest :file:`.env`, :file:`.flaskenv` and :file:`.djaskenv`
        files to set environment variables. Will also change the working
        directory to the directory containing the first file found.
    :param set_debug_flag: Set the app's debug flag based on the active
        environment
    """

    def __init__(
        self,
        add_default_commands=True,
        create_app=None,
        add_version_option=True,
        load_dotenv=True,
        set_debug_flag=True,
        **extra,
    ):
        params = list(extra.pop("params", None) or ())

        if add_version_option:
            params.append(version_option)

        AppGroup.__init__(self, params=params, **extra)
        self.create_app = create_app
        self.load_dotenv = load_dotenv
        self.set_debug_flag = set_debug_flag

        if add_default_commands:
            self.add_command(run_command)
            self.add_command(shell_command)
            self.add_command(routes_command)
            self.add_command(create_app_command)

        self._loaded_plugin_commands = False

    def _load_plugin_commands(self):
        if self._loaded_plugin_commands:
            return
        try:
            import pkg_resources
        except ImportError:
            self._loaded_plugin_commands = True
            return

        for ep in pkg_resources.iter_entry_points("djask.commands"):
            self.add_command(ep.load(), ep.name)
        self._loaded_plugin_commands = True

    def get_command(self, ctx, name):
        self._load_plugin_commands()
        # Look up built-in and plugin commands, which should be
        # available even if the app fails to load.
        rv = super().get_command(ctx, name)

        if rv is not None:
            return rv

        info = ctx.ensure_object(ScriptInfo)

        # Look up commands provided by the app, showing an error and
        # continuing if the app couldn't be loaded.
        try:
            return info.load_app().cli.get_command(ctx, name)
        except NoAppException as e:
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")

    def main(self, *args, **kwargs):
        # Set a global flag that indicates that we were invoked from the
        # command line interface. This is detected by Flask.run to make the
        # call into a no-op. This is necessary to avoid ugly errors when the
        # script that is loaded here also attempts to start a server.
        os.environ["DJASK_RUN_FROM_CLI"] = "true"

        if get_load_dotenv(self.load_dotenv):
            load_dotenv()

        obj = kwargs.get("obj")

        if obj is None:
            obj = ScriptInfo(
                create_app=self.create_app, set_debug_flag=self.set_debug_flag
            )

        kwargs["obj"] = obj
        kwargs.setdefault("auto_envvar_prefix", "DJASK")
        return super().main(*args, **kwargs)


def load_dotenv(path=None):
    """Load "dotenv" files in order of precedence to set environment variables.

    If an env var is already set it is not overwritten, so earlier files in the
    list are preferred over later files.

    This is a no-op if `python-dotenv`_ is not installed.

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    :param path: Load the file at this location instead of searching.
    :return: ``True`` if a file was loaded.
    """
    if dotenv is None:
        if (
            path
            or os.path.isfile(".env")
            or os.path.isfile(".flaskenv")
            or os.path.isfile(".djaskenv")
        ):
            click.secho(
                " * Tip: There are .env, .flaskenv or .djaskenv files present."
                ' Do "pip install python-dotenv" to use them.',
                fg="yellow",
                err=True,
            )

        return False

    # if the given path specifies the actual file then return True,
    # else False
    if path is not None:
        if os.path.isfile(path):
            return dotenv.load_dotenv(path, encoding="utf-8")

        return False

    new_dir = None

    for name in (".env", ".flaskenv", ".djaskenv"):
        path = dotenv.find_dotenv(name, usecwd=True)

        if not path:
            continue

        if new_dir is None:
            new_dir = os.path.dirname(path)

        dotenv.load_dotenv(path, encoding="utf-8")

    return new_dir is not None  # at least one file was located and loaded


def show_server_banner(env, debug, app_import_path, eager_loading):
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return

    if app_import_path is not None:
        message = f" * Serving Djask app {app_import_path!r}"

        if not eager_loading:
            message += " (lazy loading)"

        click.echo(message)

    click.echo(f" * Environment: {env}")

    if env == "production":
        click.secho(
            "   WARNING: This is a development server. Do not use it in"
            " a production deployment.",
            fg="red",
        )
        click.secho("   Use a production WSGI server instead.", dim=True)

    if debug is not None:
        click.echo(f" * Debug mode: {'on' if debug else 'off'}")


@click.command("run", short_help="Run a development server.")
@click.option("--host", "-h", default="127.0.0.1", help="The interface to bind to.")
@click.option("--port", "-p", default=5000, help="The port to bind to.")
@click.option(
    "--cert", type=CertParamType(), help="Specify a certificate file to use HTTPS."
)
@click.option(
    "--key",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    callback=_validate_key,
    expose_value=False,
    help="The key file to use when specifying a certificate.",
)
@click.option(
    "--reload/--no-reload",
    default=None,
    help="Enable or disable the reloader. By default the reloader "
    "is active if debug is enabled.",
)
@click.option(
    "--debugger/--no-debugger",
    default=None,
    help="Enable or disable the debugger. By default the debugger "
    "is active if debug is enabled.",
)
@click.option(
    "--eager-loading/--lazy-loading",
    default=None,
    help="Enable or disable eager loading. By default eager "
    "loading is enabled if the reloader is disabled.",
)
@click.option(
    "--with-threads/--without-threads",
    default=True,
    help="Enable or disable multithreading.",
)
@click.option(
    "--extra-files",
    default=None,
    type=SeparatedPathType(),
    help=(
        "Extra files that trigger a reload on change. Multiple paths"
        f" are separated by {os.path.pathsep!r}."
    ),
)
@pass_script_info
def run_command(
    info, host, port, reload, debugger, eager_loading, with_threads, cert, extra_files
):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    DJASK_ENV=development or DJASK_DEBUG=1.
    """
    debug = get_debug_flag()

    if reload is None:
        reload = debug

    if debugger is None:
        debugger = debug

    show_server_banner(get_env(), debug, info.app_import_path, eager_loading)
    app = DispatchingApp(info.load_app, use_eager_loading=eager_loading)

    from werkzeug.serving import run_simple

    run_simple(
        host,
        port,
        app,
        use_reloader=reload,
        use_debugger=debugger,
        threaded=with_threads,
        ssl_context=cert,
        extra_files=extra_files,
    )


@click.command("shell", short_help="Run a shell in the app context.")
@with_appcontext
def shell_command() -> None:
    """Run an interactive Python shell in the context of a given
    Djask application.  The application will populate the default
    namespace of this shell according to its configuration.

    This is useful for executing small snippets of management code
    without having to manually configure the application.
    """
    import code
    from flask.globals import _app_ctx_stack

    app = _app_ctx_stack.top.app
    banner = (
        f"Python {sys.version} on {sys.platform}\n"
        f"App: {app.import_name} [{app.env}]\n"
        f"Instance: {app.instance_path}"
    )
    ctx: dict = {}

    # Support the regular Python interpreter startup script if someone
    # is using it.
    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup) as f:
            eval(compile(f.read(), startup, "exec"), ctx)

    ctx.update(app.make_shell_context())

    # Site, customize, or startup script can set a hook to call when
    # entering interactive mode. The default one sets up readline with
    # tab and history completion.
    interactive_hook = getattr(sys, "__interactivehook__", None)

    if interactive_hook is not None:
        try:
            import readline
            from rlcompleter import Completer
        except ImportError:
            pass
        else:
            # rlcompleter uses __main__.__dict__ by default, which is
            # flask.__main__. Use the shell context instead.
            readline.set_completer(Completer(ctx).complete)

        interactive_hook()

    code.interact(banner=banner, local=ctx)


cli = DjaskGroup(
    help="""\
A general utility script for Djask applications.

Provides commands from Flask, Djask, extensions, and the application. Loads the
application defined in the DJASK_APP environment variable, or from a wsgi.py
file. Setting the DJASK_ENV environment variable to 'development' will enable
debug mode.

Djask provides full compatibility with Flask so your existing flask applications
and environment variables will just work fine.

\b
  {prefix}{cmd} DJASK_APP=hello.py
  {prefix}{cmd} DJASK_ENV=development
  {prefix}djask run
""".format(
        cmd="export" if os.name == "posix" else "set",
        prefix="$ " if os.name == "posix" else "> ",
    )
)


def main() -> None:
    cli.main()


if __name__ == "__main__":
    main()
