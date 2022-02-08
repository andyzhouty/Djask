import pathlib

import click
from cookiecutter.main import cookiecutter


@click.command(
    "createapp",
    short_help="Start a new project with a template.",
)
@click.argument("app_name")
def create_app_command(app_name: str) -> None:
    """Generate a new project from
    `cookiecutter-djask <https://github.com/z-t-y/cookiecutter-djask>`_
    """
    p = pathlib.Path(__file__).parent / "project_template" / "cookiecutter-djask"
    cookiecutter(str(p.absolute()), no_input=True, extra_context={"app_name": app_name})
