from rich.console import Console

from nova_api_core.cli.app import app

console = Console()


def main() -> None:
    try:
        app()
    except Exception as e:
        console.print(f"[bold red]Exécution interrompue :[/bold red] {e}")
        # On peut ajouter un raise ici en mode DEBUG si nécessaire
