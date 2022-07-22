import os
import pathlib

import click
import colorama
from colorama import Fore
from colorama import Style
from cookiecutter.main import cookiecutter

from .exceptions import AppDirectoryNotFoundError


@click.command(
    "create-app",
    short_help="Start a new project with a template.",
)
@click.argument("app_name")
def create_app_command(app_name: str) -> None:
    """Generate a new project from
    `cookiecutter-djask <https://github.com/z-t-y/cookiecutter-djask>`_
    """
    colorama.init()
    template_path = (
        pathlib.Path(__file__).parent / "project_template" / "cookiecutter-djask"
    )
    cookiecutter(
        str(template_path.absolute()),
        no_input=True,
        extra_context={"app_name": app_name},
    )
    print(Fore.GREEN + f"Djask app '{app_name}' created ✔" + Style.RESET_ALL)


@click.command("create-bp", short_help="Create a new Blueprint.")
@click.argument("bp_name")
@click.option(
    "--api",
    is_flag=True,
    show_default=True,
    default=False,
    help="Create a new APIBlueprint.",
)
def create_bp_command(bp_name: str, api: bool):
    """Generate a new blueprint from
    `cookiecutter-djask-bp <https://github.com/z-t-y/cookiecutter-djask-bp>`_
    """
    colorama.init()
    template_path = (
        pathlib.Path(__file__).parent / "project_template" / "cookiecutter-djask-bp"
    )
    dir_name = os.path.basename(os.getcwd())
    if pathlib.Path("wsgi.py").exists():
        try:
            os.chdir(dir_name)
        except FileNotFoundError:
            raise AppDirectoryNotFoundError(dir_name)
    else:
        raise FileNotFoundError(
            "wsgi.py not found, "
            "you should run this command in "
            "the same directory as wsgi.py"
        )

    cookiecutter(
        str(template_path.absolute()),
        no_input=True,
        extra_context={"bp_name": bp_name, "type": ("api" if api else "normal")},
    )
    os.chdir("..")
    print(
        Fore.GREEN
        + ("APIBlueprint" if api else "Blueprint")
        + f" '{bp_name}' "
        + "created ✔"
        + Style.RESET_ALL
    )
