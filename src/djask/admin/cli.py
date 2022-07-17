import click

from ..globals import current_app
from .ui.views import admin_bp


admin_bp.cli.help = "Create a super user."


@admin_bp.cli.command("create", help="Create a super user.")
@click.option("--username", prompt=True, help="The username for the admin.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="The password for the admin",
)
def create_superuser(username: str, password: str):
    User = current_app.config["AUTH_MODEL"]
    user = User(username=username, is_admin=True)
    user.set_password(password)
    current_app.db.session.add(user)  # type: ignore
    current_app.db.session.commit()  # type: ignore
    click.echo(f"Superuser {username} created!")
