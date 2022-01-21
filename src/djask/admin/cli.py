import click

from .views import admin_bp
from ..globals import current_app


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
def create_superuser(username, password):
    User = current_app.config["AUTH_MODEL"]
    user = User(username=username, is_admin=True)
    user.set_password(password)
    current_app.db.session.add(user)
    current_app.db.session.commit()
    click.echo(f"Superuser {username} created!")
