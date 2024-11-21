import pytest
from datetime import datetime, timedelta, UTC
from models import Habit
from database import setup_test_db, get_db_session

@pytest.fixture(scope="function")
def db_session():
    setup_test_db()
    session = get_db_session(test=True)
    yield session
    session.close()

def test_habit_attributes(db_session):
    # Test existing habit from seed data
    habit = db_session.query(Habit).filter_by(name="Exercise").first()
    assert habit.name == "Exercise"
    assert habit.periodicity == "daily"
    assert isinstance(habit.created_at, datetime)
    assert isinstance(habit.current_streak, int)
    assert isinstance(habit.max_streak, int)

def test_create_new_habit(db_session):
    new_habit = Habit(
        name="Test Habit",
        description="Test Description",
        periodicity="daily"
    )
    db_session.add(new_habit)
    db_session.commit()

    saved_habit = db_session.query(Habit).filter_by(name="Test Habit").first()
    assert saved_habit is not None
    assert saved_habit.description == "Test Description"
    assert saved_habit.periodicity == "daily"
    assert saved_habit.current_streak == 0
    assert saved_habit.max_streak == 0

def test_invalid_periodicity(db_session):
    with pytest.raises(ValueError):
        habit = Habit(
            name="Invalid Habit",
            periodicity="monthly"  # Only daily/weekly should be allowed
        )
        db_session.add(habit)
        db_session.commit()



def test_streak_calculation(db_session):
    # Get the "Read" habit which we know has a 30-day streak in seed data
    habit = db_session.query(Habit).filter_by(name="Read").first()
    assert habit.max_streak == 30
    
    # Break the streak by not completing it
    one_day = timedelta(days=1)
    two_days = timedelta(days=2)
    
    # Complete it a day later (breaking streak)
    habit.complete(db_session, datetime.now(UTC) + two_days)
    assert habit.current_streak == 1  # New streak started


def test_habit_completion(db_session):
    # Get the "Walk dog" habit which we know exists in seed data
    habit = db_session.query(Habit).filter_by(name="Walk dog").first()
    initial_streak = habit.current_streak
    
    # Complete the habit
    completion_time = datetime.now(UTC)
    habit.complete(db_session, completion_time)
    
    # Verify completion was recorded
    if habit.periodicity == "daily":
        completion = db_session.query(habit.daily_completions).first()
    else:
        completion = db_session.query(habit.weekly_completions).first()
    
    assert completion is not None
    assert completion.completed_at == completion_time
    assert habit.current_streak == initial_streak + 1

def test_weekly_habit_completion(db_session):
    # Get the "Clean kitchen" habit which is weekly in seed data
    habit = db_session.query(Habit).filter_by(name="Clean kitchen").first()
    assert habit.periodicity == "weekly"
    
    # Complete it for this week
    habit.complete(db_session, datetime.now(UTC))
    
    # Verify weekly completion
    latest_completion = db_session.query(habit.weekly_completions)\
        .order_by(habit.weekly_completions.completed_at.desc())\
        .first()
    assert latest_completion is not None