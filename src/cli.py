import typer
from rich import print
from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Habit
import os

app = typer.Typer()
console = Console()

DB_FILE = "habits.db"

def get_db_session():
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Session = sessionmaker(bind=engine)
    return Session()

def create_db():
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Base.metadata.create_all(engine)

def seed_default_habits():
    session = get_db_session()
    default_habits = [
        Habit(name="Exercise", description="30 minutes of exercise", periodicity="daily"),
        Habit(name="Read", description="Read for 30 minutes", periodicity="daily"),
        Habit(name="Meditate", description="Meditate for 10 minutes", periodicity="daily"),
        Habit(name="Clean house", description="Deep clean the house", periodicity="weekly"),
        Habit(name="Call family", description="Call parents or siblings", periodicity="weekly"),
    ]
    session.add_all(default_habits)
    session.commit()
    session.close()


@app.callback()
def main():
    """
    Habit Tracker: Manage and analyze your habits
    """
    print("[bold green]Welcome to Habit Tracker![/bold green]")
    
    if not os.path.exists(DB_FILE):
        create_db()
        seed_default_habits()
        print(f"[green]Created database and seeded with default habits.[/green]")
    else:
        print(f"[green]Using existing database.[/green]")



@app.command()
def create_habit(name: str, description: str, periodicity: str):
    """Create a new habit"""
    session = get_db_session()
    new_habit = Habit(name=name, description=description, periodicity=periodicity)
    session.add(new_habit)
    session.commit()
    print(f"[green]Created new habit: {name}[/green]")
    session.close()