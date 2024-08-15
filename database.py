import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Habit, DailyCompletion, WeeklyCompletion
from datetime import datetime, timedelta, UTC
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
    created_at_date = datetime.now() - timedelta(days=30)
    habits = [
        Habit(
            id=1,
            name="Exercise",
            description="30 minutes of exercise",
            periodicity="daily",
            created_at=created_at_date,
            current_streak=12,
            max_streak=20,
        ),
        Habit(
            id=2,
            name="Read",
            description="Read for 30 minutes",
            periodicity="daily",
            created_at=created_at_date,
            current_streak=30,
            max_streak=30,
        ),
        Habit(
            id=3,
            name="Meditate",
            description="Meditate for 10 minutes",
            periodicity="daily",
            created_at=created_at_date,
            current_streak=5,
            max_streak=15,
        ),
        Habit(
            id=4,
            name="Clean kitchen",
            description="Deep clean the kitchen",
            periodicity="weekly",
            created_at=created_at_date,
            current_streak=3,
            max_streak=4,
        ),
        Habit(
            id=5,
            name="Walk dog",
            description="Walk the dog for 30 minutes",
            periodicity="daily",
            created_at=created_at_date,
            current_streak=25,
            max_streak=25,
        ),
    ]
    session.add_all(habits)
    session.flush()  # Ensure all habits have IDs before creating completions

    # Create predefined completions
    today = datetime.now().date()
    completions = []

    # Helper function to get the Monday of a given date's week
    def get_week_start(date):
        return date - timedelta(days=date.weekday())

    # Exercise: Consistent with a break in the middle
    for i in range(30):
        if i not in range(10, 18):  # 8-day break from day 10 to 17
            session.add(
                DailyCompletion(
                    habit_id=1,
                    completed_at=datetime.combine(
                        today - timedelta(days=i), datetime.min.time()
                    ).replace(tzinfo=UTC),
                )
            )

    # Read: Perfect streak for the whole month
    for i in range(30):
        session.add(
            DailyCompletion(
                habit_id=2,
                completed_at=datetime.combine(
                    today - timedelta(days=i), datetime.min.time()
                ).replace(tzinfo=UTC),
            )
        )

    # Meditate: Inconsistent with multiple breaks
    for i in range(30):
        if i % 3 != 0 and i % 7 != 0:  # Skip every 3rd and 7th day
            session.add(
                DailyCompletion(
                    habit_id=3,
                    completed_at=datetime.combine(
                        today - timedelta(days=i), datetime.min.time()
                    ).replace(tzinfo=UTC),
                )
            )

    # Clean kitchen: Weekly habit, missed once, with multiple completions in some weeks
    for i in range(0, 30, 7):
        week_start = get_week_start(today - timedelta(days=i))
        if i != 14:  # Missed on the 3rd week
            session.add(
                WeeklyCompletion(
                    habit_id=4,
                    week_start=week_start,
                    completed_at=datetime.combine(
                        week_start + timedelta(days=2), datetime.min.time()
                    ).replace(tzinfo=UTC),
                )
            )
            # Add a second completion in the first and fourth weeks
            if i in [0, 28]:
                session.add(
                    WeeklyCompletion(
                        habit_id=4,
                        week_start=week_start,
                        completed_at=datetime.combine(
                            week_start + timedelta(days=5), datetime.min.time()
                        ).replace(tzinfo=UTC),
                    )
                )

    # Walk dog: Very consistent with just a couple misses
    for i in range(30):
        if i not in [7, 23]:  # Missed only on day 7 and 23
            session.add(
                DailyCompletion(
                    habit_id=5,
                    completed_at=datetime.combine(
                        today - timedelta(days=i), datetime.min.time()
                    ).replace(tzinfo=UTC),
                )
            )

    session.commit()
    session.close()


def clear_test_data(session):
    session.query(Habit).delete()
    session.query(DailyCompletion).delete()
    session.query(WeeklyCompletion).delete()
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
