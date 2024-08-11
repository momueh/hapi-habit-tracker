import pytest
from datetime import datetime, timedelta
from database import setup_test_db, get_db_session
from analytics import (
    get_all_habits,
    get_habits_by_periodicity,
    get_longest_run_streak,
    get_longest_run_streak_for_habit,
    get_days_since_last_completion,
    get_completion_rate_for_habit,
    get_all_habits_completion_rates,
    get_overall_completion_rate
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
    read_streak = get_longest_run_streak_for_habit(db_session, 2)  # "Read" habit
    assert read_streak == 30

def test_get_days_since_last_completion(db_session):
    days_exercise = get_days_since_last_completion(db_session, 1)  # "Exercise" habit
    assert days_exercise == 0  # Completed today

def test_get_completion_rate_for_habit(db_session):
    rate_read = get_completion_rate_for_habit(db_session, 2, 30)  # "Read" habit, last 30 days
    assert rate_read == 1.0  # Perfect streak

    rate_exercise = get_completion_rate_for_habit(db_session, 1, 30)  # "Exercise" habit, last 30 days
    assert rate_exercise == 22/30  # 22 completions out of 30 days

def test_get_all_habits_completion_rates(db_session):
    rates = get_all_habits_completion_rates(db_session, 30)
    assert len(rates) == 5
    assert rates["Read"] == 1.0
    assert rates["Exercise"] == 22/30
    assert 0.6 < rates["Meditate"] < 0.7  # Approximately 20 out of 30 days

def test_get_overall_completion_rate(db_session):
    rate = get_overall_completion_rate(db_session, 30)
    # Expected completions: 22 (Exercise) + 30 (Read) + 20 (Meditate) + 28 (Walk dog) + 3 (Clean kitchen)
    # Total possible: 30 * 4 (daily habits) + 4 (weekly habit) = 124
    expected_rate = (22 + 30 + 20 + 28 + 3) / 124
    assert rate == pytest.approx(expected_rate, rel=1e-2)