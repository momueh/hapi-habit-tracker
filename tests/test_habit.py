import pytest
from datetime import datetime, timedelta, UTC
from models import Habit, DailyCompletion, WeeklyCompletion

def test_create_habit(db_session):
    """Verifies habit creation with default values and basic attributes."""
    habit = Habit(
        name="Test Habit",
        description="Test description",
        periodicity="daily"
    )
    db_session.add(habit)
    db_session.commit()
    
    assert habit.id is not None
    assert habit.name == "Test Habit"
    assert habit.description == "Test description"
    assert habit.periodicity == "daily"
    assert habit.current_streak == 0
    assert habit.max_streak == 0

def test_update_habit(db_session):
    """Tests updating basic habit properties while preserving other attributes."""
    habit = Habit(name="Original", description="Original desc", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    habit.name = "Updated"
    habit.description = "Updated desc"
    db_session.commit()
    
    updated_habit = db_session.get(Habit, habit.id)
    assert updated_habit.name == "Updated"
    assert updated_habit.description == "Updated desc"

def test_delete_habit(db_session):
    """Ensures habits can be completely removed from the database."""
    habit = Habit(name="To Delete", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    db_session.delete(habit)
    db_session.commit()
    
    deleted_habit = db_session.get(Habit, habit.id)
    assert deleted_habit is None

def test_complete_daily_habit(db_session):
    """Verifies daily habit completion creates appropriate completion record."""
    habit = Habit(name="Daily Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    completion_time = datetime.now(UTC)
    habit.complete(db_session, completion_time)
    
    assert len(habit.daily_completions) == 1
    assert habit.daily_completions[0].completed_at == completion_time

def test_complete_weekly_habit(db_session):
    """Verifies weekly habit completion creates appropriate completion record."""
    habit = Habit(name="Weekly Test", periodicity="weekly")
    db_session.add(habit)
    db_session.commit()
    
    completion_time = datetime.now(UTC)
    habit.complete(db_session, completion_time)
    
    assert len(habit.weekly_completions) == 1
    assert habit.weekly_completions[0].completed_at == completion_time
    assert habit.weekly_completions[0].week_start == habit._get_week_start(completion_time)

def test_multiple_completions_same_day(db_session):
    """Confirms multiple completions are allowed within the same day."""
    habit = Habit(name="Multiple Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    habit.complete(db_session, base_time + timedelta(hours=2))
    
    assert len(habit.daily_completions) == 2

def test_invalid_periodicity(db_session):
    """Ensures habit creation fails with unsupported periodicity values."""
    with pytest.raises(ValueError):
        Habit(name="Invalid", periodicity="monthly")

def test_daily_is_within_period_same_day(db_session):
    """Verifies same-day completions maintain daily streak."""
    habit = Habit(name="Daily Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    
    # Same day completion should maintain streak
    assert habit._is_within_period(base_time + timedelta(hours=2))

def test_daily_is_within_period_next_day(db_session):
    """Verifies next-day completions maintain daily streak."""
    habit = Habit(name="Daily Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    
    # Next day completion should maintain streak
    assert habit._is_within_period(base_time + timedelta(days=1))

def test_daily_is_within_period_breaks_streak(db_session):
    """Verifies that skipping a day breaks daily streak."""
    habit = Habit(name="Daily Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    
    # Two days later should break streak
    assert not habit._is_within_period(base_time + timedelta(days=2))

def test_weekly_is_within_period_same_week(db_session):
    """Verifies same-week completions maintain weekly streak."""
    habit = Habit(name="Weekly Test", periodicity="weekly")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    
    # Same week completion should maintain streak
    assert habit._is_within_period(base_time + timedelta(days=2))

def test_weekly_is_within_period_next_week(db_session):
    """Verifies next-week completions maintain weekly streak."""
    habit = Habit(name="Weekly Test", periodicity="weekly")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    
    # Next week completion should maintain streak
    assert habit._is_within_period(base_time + timedelta(days=7))

def test_weekly_is_within_period_breaks_streak(db_session):
    """Verifies that skipping a week breaks weekly streak."""
    habit = Habit(name="Weekly Test", periodicity="weekly")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    
    # Two weeks later should break streak
    assert not habit._is_within_period(base_time + timedelta(days=14))

def test_is_within_period_no_completions(db_session):
    """Verifies that first completion always returns True for streak maintenance."""
    habit = Habit(name="First Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    # First completion should always maintain streak
    assert habit._is_within_period(datetime.now(UTC))