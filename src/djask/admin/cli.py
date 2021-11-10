import click

from .views import admin_bp
from ..auth.models import User
from ..globals import current_app


@admin_bp.cli.command("create")
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_superuser(username, password):
    user = User(username=username, is_admin=True)
    user.set_password(password)
    current_app.db.session.add(user)
    current_app.db.session.commit()
    click.echo(f"Superuser {username} created!")
