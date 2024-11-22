import typer
from rich import print
from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Habit
import os
from database import get_db_session, ensure_prod_db_exists
import analytics

app = typer.Typer(name="hapi")
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Hapi: Manage and analyze your habits
    """
    print("\n")
    print("[bold green]Welcome to HAPI - Your Personal Habit Tracker![/bold green]")
    ensure_prod_db_exists()

    if ctx.invoked_subcommand is None:
        show_main_menu()


def show_main_menu():
    while True:
        display_habits()
        choice = typer.prompt(
            "\nWhat would you like to do?\n"
            "1. Complete a Habit\n"
            "2. Add a Habit\n"
            "3. Edit a Habit\n"
            "4. Delete a Habit\n"
            "5. Analytics\n"
            "6. Exit\n"
            "Enter your choice"
        )

        if choice == "1":
            complete_habit()
        elif choice == "2":
            create_habit_interactive()
        elif choice == "3":
            edit_habit()
        elif choice == "4":
            delete_habit()
        elif choice == "5":
            show_analytics_menu()
        elif choice == "6":
            print("Goodbye!")
            raise typer.Exit()
        else:
            print("Invalid choice. Please try again.")


def display_habits():
    session = get_db_session()
    habits = session.query(Habit).all()

    table = Table(title="Your Habits")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Start Date", style="blue")
    table.add_column("Periodicity", style="green")
    table.add_column("Current Streak", style="red")
    table.add_column("Record Streak", style="yellow")
    table.add_column("Last Completion", style="blue")
    

    for habit in habits:
        streak_icon = "🔥" if habit.current_streak > 0 else ""
        trophy_icon = "🏆" if habit.max_streak > 0 else ""
        formatted_start_date = habit.created_at.strftime("%m-%d-%Y")

        # Format last completion time
        last_completion = habit.get_last_completion()
        formatted_last_completion = (last_completion.strftime("%m-%d-%Y %H:%M") 
                             if last_completion 
                             else "Never")
        table.add_row(
            str(habit.id),
            habit.name,
            formatted_start_date,
            habit.periodicity,
            f"{streak_icon} {habit.current_streak}",
            f"{trophy_icon} {habit.max_streak}",
            formatted_last_completion,
        )

    console.print(table)
    session.close()


def complete_habit():
    session = get_db_session()
    habits = session.query(Habit).all()

    habit_id = typer.prompt("Enter the ID of the habit you want to complete")
    habit = session.get(Habit, habit_id)

    if habit:
        habit.complete(session)
        session.commit()
        print(f"[green]Habit '{habit.name}' completed![/green]")
    else:
        print("[red]Habit not found.[/red]")

    session.close()


def create_habit_interactive():
    name = typer.prompt("Enter habit name")
    description = typer.prompt("Enter habit description")
    periodicity = typer.prompt("Enter habit periodicity (daily/weekly)")
    create_habit(name, description, periodicity)


def edit_habit():
    session = get_db_session()
    habit_id = typer.prompt("Enter the ID of the habit you want to edit")
    habit = session.get(Habit, habit_id)

    if habit:
        name = typer.prompt(
            "Enter new name (or press Enter to keep current)", default=habit.name
        )
        description = typer.prompt(
            "Enter new description (or press Enter to keep current)",
            default=habit.description,
        )

        habit.name = name
        habit.description = description
        session.commit()
        print(f"[green]Habit '{habit.name}' updated![/green]")
    else:
        print("[red]Habit not found.[/red]")

    session.close()


def delete_habit():
    session = get_db_session()
    habit_id = typer.prompt("Enter the ID of the habit you want to delete")
    habit = session.get(Habit, habit_id)

    if habit:
        session.delete(habit)
        session.commit()
        print(f"[green]Habit '{habit.name}' deleted![/green]")
    else:
        print("[red]Habit not found.[/red]")

    session.close()


def show_analytics_menu():
    while True:
        choice = typer.prompt(
            "\nAnalytics Menu:\n"
            "1. Get all habits\n"
            "2. Get habits by periodicity\n"
            "3. Get longest run streak\n"
            "4. Get longest run streak for a habit\n"
            "5. Get days since last completion\n"
            "6. Back to main menu\n"
            "Enter your choice"
        )

        if choice == "1":
            display_habits()
        elif choice == "2":
            periodicity = typer.prompt("Enter periodicity (daily/weekly)")
            habits = analytics.get_habits_by_periodicity(get_db_session(), periodicity)
            display_habits_list(habits)
        elif choice == "3":
            streak = analytics.get_longest_run_streak(get_db_session())
            print(f"Longest run streak: {streak}")
        elif choice == "4":
            habit_id = typer.prompt("Enter habit ID")
            streak = analytics.get_longest_run_streak_for_habit(
                get_db_session(), int(habit_id)
            )
            print(f"Longest run streak for habit: {streak}")
        elif choice == "5":
            habit_id = typer.prompt("Enter habit ID")
            days = analytics.get_days_since_last_completion(
                get_db_session(), int(habit_id)
            )
            print(f"Days since last completion: {days}")
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")


def display_habits_list(habits):
    table = Table(title="Habits")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Periodicity", style="green")

    for habit in habits:
        table.add_row(str(habit.id), habit.name, habit.periodicity)

    console.print("\n")
    console.print(table)


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
