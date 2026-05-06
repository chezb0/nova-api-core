import typer

from nova_api_core.cli.commands.init import init_command

# Create main CLI app
app = typer.Typer(help="Nova Framework CLI")


# Callback for the main app
@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """Nova Framework CLI"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


# Register commands
@app.command()
def init(name: str = typer.Argument(..., help="Project name")) -> None:
    """Initialize a clean Nova project structure."""
    init_command(name)
