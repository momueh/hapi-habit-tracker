import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Habit, Completion
from datetime import datetime, timedelta
import random
from rich import print

DB_FILE = "habits.db"
TEST_DB_FILE = "test_habits.db"

def get_db_session(test=False):
    db_file = TEST_DB_FILE if test else DB_FILE
    engine = create_engine(f"sqlite:///{db_file}")
    Session = sessionmaker(bind=engine)
    return Session()

def create_db(test=False):
    db_file = TEST_DB_FILE if test else DB_FILE
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)

def seed_predefined_habits(session):
     # Create predefined habits
    habits = [
        Habit(id=1, name="Exercise", description="30 minutes of exercise", periodicity="daily", current_streak=12, max_streak=20),
        Habit(id=2, name="Read", description="Read for 30 minutes", periodicity="daily", current_streak=30, max_streak=30),
        Habit(id=3, name="Meditate", description="Meditate for 10 minutes", periodicity="daily", current_streak=5, max_streak=15),
        Habit(id=4, name="Clean kitchen", description="Deep clean the kitchen", periodicity="weekly", current_streak=3, max_streak=4),
        Habit(id=5, name="Walk dog", description="Walk the dog for 30 minutes", periodicity="daily", current_streak=25, max_streak=25),
    ]
    session.add_all(habits)
    
    # Create predefined completions
    today = datetime.now().date()
    completions = []
    
    # Exercise: Consistent with a break in the middle
    for i in range(30):
        if i not in range(10, 18):  # 8-day break from day 10 to 17
            completions.append(Completion(habit_id=1, completed_at=today - timedelta(days=i)))
    
    # Read: Perfect streak for the whole month
    for i in range(30):
        completions.append(Completion(habit_id=2, completed_at=today - timedelta(days=i)))
    
    # Meditate: Inconsistent with multiple breaks
    for i in range(30):
        if i % 3 != 0 and i % 7 != 0:  # Skip every 3rd and 7th day
            completions.append(Completion(habit_id=3, completed_at=today - timedelta(days=i)))
    
    # Clean kitchen: Weekly habit, missed once
    for i in range(0, 30, 7):
        if i != 14:  # Missed on the 3rd week
            completions.append(Completion(habit_id=4, completed_at=today - timedelta(days=i)))
    
    # Walk dog: Very consistent with just a couple misses
    for i in range(30):
        if i not in [7, 23]:  # Missed only on day 7 and 23
            completions.append(Completion(habit_id=5, completed_at=today - timedelta(days=i)))
    
    session.add_all(completions)
    
    session.commit()
    session.close()

def clear_test_data(session):
    session.query(Habit).delete()
    session.query(Completion).delete()
    session.commit()

def setup_test_db():
    if not os.path.exists(TEST_DB_FILE):
        create_db(test=True)
    session = get_db_session(test=True)
    clear_test_data(session)
    seed_predefined_habits(session)
    session.close()

def ensure_prod_db_exists():
    if not os.path.exists(DB_FILE):
        create_db()
        session = get_db_session()
        seed_predefined_habits(session)
        session.close()
        print(f"[green]Created database and seeded with default habits.[/green]")
    else:
        print(f"[green]Using existing database.[/green]")