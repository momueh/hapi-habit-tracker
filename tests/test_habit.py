import pytest
from datetime import datetime, timedelta, UTC
from models import Habit, DailyCompletion, WeeklyCompletion

def test_create_habit(db_session):
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
    habit = Habit(name="To Delete", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    db_session.delete(habit)
    db_session.commit()
    
    deleted_habit = db_session.get(Habit, habit.id)
    assert deleted_habit is None

def test_complete_daily_habit(db_session):
    habit = Habit(name="Daily Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    completion_time = datetime.now(UTC)
    habit.complete(db_session, completion_time)
    
    assert len(habit.daily_completions) == 1
    assert habit.daily_completions[0].completed_at == completion_time

def test_complete_weekly_habit(db_session):
    habit = Habit(name="Weekly Test", periodicity="weekly")
    db_session.add(habit)
    db_session.commit()
    
    completion_time = datetime.now(UTC)
    habit.complete(db_session, completion_time)
    
    assert len(habit.weekly_completions) == 1
    assert habit.weekly_completions[0].completed_at == completion_time
    assert habit.weekly_completions[0].week_start == habit._get_week_start(completion_time)

def test_multiple_completions_same_day(db_session):
    habit = Habit(name="Multiple Test", periodicity="daily")
    db_session.add(habit)
    db_session.commit()
    
    base_time = datetime.now(UTC)
    habit.complete(db_session, base_time)
    habit.complete(db_session, base_time + timedelta(hours=2))
    
    assert len(habit.daily_completions) == 2

def test_invalid_periodicity(db_session):
    with pytest.raises(ValueError):
        Habit(name="Invalid", periodicity="monthly")