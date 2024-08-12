import pytest
from datetime import datetime, timedelta, UTC
from database import setup_test_db, get_db_session
from analytics import (
    get_all_habits,
    get_habits_by_periodicity,
    get_longest_run_streak,
    get_longest_run_streak_for_habit,
    get_days_since_last_completion,
)


@pytest.fixture(scope="module")
def db_session():
    setup_test_db()
    session = get_db_session(test=True)
    yield session
    session.close()

def test_get_all_habits(db_session):
    habits = get_all_habits(db_session)
    assert len(habits) == 5
    assert all(habit.name in ["Exercise", "Read", "Meditate", "Clean kitchen", "Walk dog"] for habit in habits)

def test_get_habits_by_periodicity(db_session):
    daily_habits = get_habits_by_periodicity(db_session, "daily")
    weekly_habits = get_habits_by_periodicity(db_session, "weekly")
    assert len(daily_habits) == 4
    assert len(weekly_habits) == 1
    assert weekly_habits[0].name == "Clean kitchen"

def test_get_longest_run_streak(db_session):
    longest_streak = get_longest_run_streak(db_session)
    assert longest_streak == 30  # "Read" habit has the longest streak

def test_get_longest_run_streak_for_habit(db_session):
    longest_streak = get_longest_run_streak_for_habit(db_session, 2)  # "Read" habit
    assert longest_streak == 30

def test_get_days_since_last_completion(db_session):
    days_since_completion = get_days_since_last_completion(db_session, 1)  # "Exercise" habit
    assert days_since_completion == 0  # Completed today
    # Todo add the other cases

