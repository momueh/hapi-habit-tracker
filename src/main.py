import typer
from rich import print
from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Habit
import os

app = typer.Typer(name="hapi")
console = Console()

@app.callback()
def main(ctx: typer.Context):
    """
    Hapi: Manage and analyze your habits
    """
    print("[bold green]Welcome to Hapi![/bold green]")
    ensure_db_exists()

    # Check if no command was provided
    if ctx.invoked_subcommand is None:
        print("Type 'python src/main.py --help' for usage information.")



@app.command()
def create_habit(name: str, description: str, periodicity: str):
    """Create a new habit"""
    session = get_db_session()
    new_habit = Habit(name=name, description=description, periodicity=periodicity)
    session.add(new_habit)
    session.commit()
    print(f"[green]Created new habit: {name}[/green]")
    session.close()

if __name__ == "__main__":
    app(prog_name="hapi")