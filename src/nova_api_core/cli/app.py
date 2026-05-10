import typer
from typing import Optional

from nova_api_core.cli.commands.init import init_command
from nova_api_core.core.types.database_type import DatabaseType

# On initialise l'application Typer
app = typer.Typer(
    help="Nova Framework CLI - Un générateur de microservices propre et robuste.",
    rich_markup_mode="rich"
)


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """Bienvenue dans le CLI du Nova Framework."""
    if ctx.invoked_subcommand is None:
        # Si aucune commande n'est passée (ex: juste 'nova'), on affiche l'aide
        typer.echo(ctx.get_help())


@app.command()
def init(
    name: str = typer.Argument(
        ..., 
        help="Le nom du dossier de votre nouveau projet."
    ),
    db: DatabaseType = typer.Option(
        DatabaseType.NONE, 
        "--db", "-d", 
        help="Le moteur de base de données à configurer par défaut."
    )
) -> None:
    """
    Génère la structure complète d'un nouveau projet Nova.
    """
    # Ici on passe bien 'name' et 'db' à la commande d'initialisation
    init_command(name, db)


if __name__ == "__main__":
    app()