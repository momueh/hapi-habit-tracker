import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Habit, Completion
from datetime import datetime, timedelta
import random
from rich import print

DB_FILE = "habits.db"

def get_db_session():
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Session = sessionmaker(bind=engine)
    return Session()

def create_db():
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Base.metadata.create_all(engine)

def seed_predefined_habits():
    session = get_db_session()
    default_habits = [
        Habit(name="Exercise", description="30 minutes of exercise", periodicity="daily"),
        Habit(name="Read", description="Read for 30 minutes", periodicity="daily"),
        Habit(name="Meditate", description="Meditate for 10 minutes", periodicity="daily"),
        Habit(name="Clean kitchen", description="Deep clean the kitchen", periodicity="weekly"),
        Habit(name="Walk dog", description="Walk the dog for 30 minutes", periodicity="weekly"),
    ]
    session.add_all(default_habits)
    session.commit()

    start_date = datetime.now() - timedelta(weeks=4)

    for habit in default_habits:
        current_date = start_date
        current_streak = 0
        max_streak = 0

        while current_date < datetime.now():
            if habit.periodicity == "daily":
                if random.random() < 0.8:  # 80% chance of completing the habit
                    completion = Completion(habit_id=habit.id, completed_at=current_date)
                    session.add(completion)
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 0  # Break the streak
                current_date += timedelta(days=1)
            
            elif habit.periodicity == "weekly":
                if random.random() < 0.9:  # 90% chance of completing the habit
                    completion_date = current_date + timedelta(days=random.randint(0, 6))
                    completion = Completion(habit_id=habit.id, completed_at=completion_date)
                    session.add(completion)
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 0  # Break the streak
                current_date += timedelta(weeks=1)

        habit.current_streak = current_streak
        habit.max_streak = max_streak
        session.add(habit)

    session.commit()
    session.close()

def ensure_db_exists():
    if not os.path.exists(DB_FILE):
        create_db()
        seed_default_habits()
        print(f"[green]Created database and seeded with default habits.[/green]")
    else:
        print(f"[green]Using existing database.[/green]")