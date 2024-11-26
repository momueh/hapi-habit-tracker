import pytest
from datetime import datetime, timedelta, UTC
from models import Habit, DailyCompletion, WeeklyCompletion
from analytics import (
    get_all_habits,
    get_habits_by_periodicity,
    get_longest_run_streak,
    get_longest_run_streak_for_habit,
    get_days_since_last_completion,
)

def test_get_all_habits(db_session):
    """Verifies that all habits can be retrieved from the database"""
    habits = [
        Habit(name="Habit 1", periodicity="daily"),
        Habit(name="Habit 2", periodicity="weekly"),
        Habit(name="Habit 3", periodicity="daily")
    ]
    for habit in habits:
        db_session.add(habit)
    db_session.commit()

    retrieved_habits = get_all_habits(db_session)
    assert len(retrieved_habits) == 3
    assert {h.name for h in retrieved_habits} == {"Habit 1", "Habit 2", "Habit 3"}

def test_get_habits_by_periodicity(db_session):
    """Tests filtering habits by their periodicity (daily/weekly)."""
    habits = [
        Habit(name="Daily 1", periodicity="daily"),
        Habit(name="Weekly 1", periodicity="weekly"),
        Habit(name="Daily 2", periodicity="daily"),
        Habit(name="Weekly 2", periodicity="weekly")
    ]
    for habit in habits:
        db_session.add(habit)
    db_session.commit()

    daily_habits = get_habits_by_periodicity(db_session, "daily")
    weekly_habits = get_habits_by_periodicity(db_session, "weekly")
    
    assert len(daily_habits) == 2
    assert len(weekly_habits) == 2
    assert all(h.periodicity == "daily" for h in daily_habits)
    assert all(h.periodicity == "weekly" for h in weekly_habits)

def test_get_longest_run_streak(db_session):
    """Tests finding the longest streak across all habits in the database."""
    base_time = datetime.now(UTC)
    
    # Habit with 5-day streak
    habit1 = Habit(name="Habit 1", periodicity="daily")
    db_session.add(habit1)
    for i in range(5):
        completion = DailyCompletion(
            habit=habit1,
            completed_at=base_time - timedelta(days=i)
        )
        db_session.add(completion)

    # Habit with 3-day streak
    habit2 = Habit(name="Habit 2", periodicity="daily")
    db_session.add(habit2)
    for i in range(3):
        completion = DailyCompletion(
            habit=habit2,
            completed_at=base_time - timedelta(days=i)
        )
        db_session.add(completion)

    db_session.commit()

    # Update max streaks for both habits
    habit1.max_streak = habit1.calculate_max_streak()
    habit2.max_streak = habit2.calculate_max_streak()
    db_session.commit()

    # Verify longest streak
    longest_streak = get_longest_run_streak(db_session)
    assert longest_streak == 5

def test_get_longest_run_streak_for_habit(db_session):
    """Verifies max streak calculation for a habit with multiple streak periods."""
    habit = Habit(name="Test Habit", periodicity="daily")
    db_session.add(habit)
    
    base_time = datetime.now(UTC)
    
    # Create a 3-day streak, gap, then 5-day streak
    # First streak (3 days)
    for i in range(10, 13):
        completion = DailyCompletion(
            habit=habit,
            completed_at=base_time - timedelta(days=i)
        )
        db_session.add(completion)
    
    # Second streak (5 days)
    for i in range(0, 5):
        completion = DailyCompletion(
            habit=habit,
            completed_at=base_time - timedelta(days=i)
        )
        db_session.add(completion)
    
    db_session.commit()

    # Update max streak
    habit.max_streak = habit.calculate_max_streak()
    db_session.commit()

    # Verify max streak
    longest_streak = get_longest_run_streak_for_habit(db_session, habit.id)
    assert longest_streak == 5

def test_get_days_since_last_completion(db_session):
    """Tests calculation of days elapsed since the last habit completion."""
    habit = Habit(name="Test Habit", periodicity="daily")
    db_session.add(habit)
    
    # Add completion 3 days ago
    completion_time = datetime.now(UTC) - timedelta(days=3)
    completion = DailyCompletion(
        habit=habit,
        completed_at=completion_time
    )
    db_session.add(completion)
    db_session.commit()

    # Test days since completion
    days_since = get_days_since_last_completion(db_session, habit.id)
    assert days_since == 3

def test_get_days_since_last_completion_never_completed(db_session):
    """Verifies handling of habits that have never been completed."""
    habit = Habit(name="Test Habit", periodicity="daily")
    db_session.add(habit)
    db_session.commit()

    days_since = get_days_since_last_completion(db_session, habit.id)
    assert days_since is None

def test_get_days_since_last_completion_nonexistent_habit(db_session):
    """Ensures proper handling when querying non-existent habit IDs."""
    days_since = get_days_since_last_completion(db_session, 999)
    assert days_since is None