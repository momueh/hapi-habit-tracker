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
    """
    Create and return a new database session.

    Args:
        test (bool): If True, uses test database file instead of production

    Returns:
        Session: SQLAlchemy database session
    """
    db_file = TEST_DB_FILE if test else DB_FILE
    engine = create_engine(f"sqlite:///{db_file}")
    Session = sessionmaker(bind=engine)
    return Session()


def create_db(test=False):
    """
    Create database tables based on SQLAlchemy models.

    Args:
        test (bool): If True, creates test database instead of production
    """
    db_file = TEST_DB_FILE if test else DB_FILE
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)

def create_completion_date(base_date: datetime, days_ago: int, time_of_day: datetime.time = datetime.min.time()) -> datetime:
    """
    Create a completion date relative to a base date.
    
    Args:
        base_date (datetime): The reference date to count back from
        days_ago (int): Number of days to subtract
        time_of_day (datetime.time, optional): Time of day for the completion. Defaults to midnight.
    
    Returns:
        datetime: UTC-aware completion datetime
    """
    completion_date = base_date - timedelta(days=days_ago)
    return datetime.combine(completion_date.date(), time_of_day, tzinfo=UTC)

def get_week_start(date):
        """
        Calculate the Monday date for the week containing the given date.

        Args:
            date (date): Any date within the desired week

        Returns:
            date: The Monday of that week
        """
        return date - timedelta(days=date.weekday())


def seed_predefined_habits(session):
    """
    Populate database with predefined habits and their completion history.
    Creates a 30-day history of completions with various patterns for each habit.

    Args:
        session (Session): SQLAlchemy database session
    """
    # Get the current time in UTC for our base date
    now = datetime.now(UTC)
    base_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Create habits with correct created_at date
    created_at_date = base_date - timedelta(days=30)

    habits = [
        Habit(
            id=1,
            name="Exercise",
            description="30 minutes of exercise",
            periodicity="daily",
            created_at=created_at_date,
        ),
        Habit(
            id=2,
            name="Read",
            description="Read for 30 minutes",
            periodicity="daily",
            created_at=created_at_date,
        ),
        Habit(
            id=3,
            name="Meditate",
            description="Meditate for 10 minutes",
            periodicity="daily",
            created_at=created_at_date,
        ),
        Habit(
            id=4,
            name="Clean kitchen",
            description="Deep clean the kitchen",
            periodicity="weekly",
            created_at=created_at_date,
        ),
        Habit(
            id=5,
            name="Walk dog",
            description="Walk the dog for 30 minutes",
            periodicity="daily",
            created_at=created_at_date,
        ),
    ]
    session.add_all(habits)
    session.flush()  # Ensure all habits have IDs before creating completions

    # Create predefined completions
    today = datetime.now(UTC).date()

    # Exercise: Consistent with a break in the middle
    for i in range(30):
        if i not in range(10, 18):  # 8-day break from day 10 to 17
            session.add(
                DailyCompletion(
                    habit_id=1,
                    completed_at=create_completion_date(base_date, i)
                )
            )

    # Read: Perfect streak for the whole month
    for i in range(30):
        session.add(
            DailyCompletion(
                habit_id=2,
                completed_at=create_completion_date(base_date, i)
            )
        )

    # Meditate: Inconsistent with multiple breaks
    for i in range(30):
        if i % 3 != 0 and i % 7 != 0:  # Skip every 3rd and 7th day
            session.add(
                DailyCompletion(
                    habit_id=3,
                    completed_at=create_completion_date(base_date, i)
                )
            )

    # Clean kitchen: Weekly habit, missed once, with multiple completions in some weeks
    for i in range(0, 30, 7):
        week_start = get_week_start(base_date.date() - timedelta(days=i))
        if i != 14:  # Missed on the 3rd week
            # First completion of the week
            session.add(
                WeeklyCompletion(
                    habit_id=4,
                    week_start=week_start,
                    completed_at=create_completion_date(base_date, i, datetime.strptime("10:00", "%H:%M").time())
                )
            )
            # Add a second completion in the first and fourth weeks
            if i in [0, 28]:
                session.add(
                    WeeklyCompletion(
                        habit_id=4,
                        week_start=week_start,
                        completed_at=create_completion_date(base_date, i, datetime.strptime("15:00", "%H:%M").time())
                    )
                )

    # Walk dog: Very consistent with just a couple misses
    for i in range(30):
        if i not in [7, 23, 30]:  # Missed only on day 7 and 23, 30
            session.add(
                DailyCompletion(
                    habit_id=5,
                    completed_at=create_completion_date(base_date, i)
                )
            )
    
    # After all completions are added, but before commit, calculate streaks
    for habit in habits:
        habit.current_streak = habit.calculate_streak(now)
        habit.max_streak = habit.calculate_max_streak()

    session.commit()
    session.close()


def clear_test_data(session):
    """
    Remove all data from Habit, DailyCompletion, and WeeklyCompletion tables.

    Args:
        session (Session): SQLAlchemy database session
    """
    session.query(Habit).delete()
    session.query(DailyCompletion).delete()
    session.query(WeeklyCompletion).delete()
    session.commit()


def setup_test_db():
    """
    Initialize test database.
    Creates a new database file if it doesn't exist.
    """
    if not os.path.exists(TEST_DB_FILE):
        create_db(test=True)
    session = get_db_session(test=True)
    clear_test_data(session)
    session.close()


def ensure_prod_db_exists():
    """
    Ensure production database exists and is seeded with initial data.
    Creates a new database file with default habits if it doesn't exist.
    """
    if not os.path.exists(DB_FILE):
        create_db()
        session = get_db_session()
        seed_predefined_habits(session)
        session.close()
        print(f"[green]Created database and seeded with default habits.[/green]")
    else:
        print(f"[green]Using existing database.[/green]")
