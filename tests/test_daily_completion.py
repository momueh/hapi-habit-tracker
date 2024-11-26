import pytest
from datetime import datetime, UTC
from models import Habit, DailyCompletion

def test_create_daily_completion(db_session):
    habit = Habit(name="Test Habit", periodicity="daily")
    db_session.add(habit)
    db_session.flush()
    
    completion = DailyCompletion(
        habit=habit,
        completed_at=datetime.now(UTC)
    )
    db_session.add(completion)
    db_session.commit()
    
    assert completion.id is not None
    assert completion.habit_id == habit.id

def test_delete_daily_completion(db_session):
    habit = Habit(name="Test Habit", periodicity="daily")
    db_session.add(habit)
    db_session.flush()
    
    completion = DailyCompletion(
        habit=habit,
        completed_at=datetime.now(UTC)
    )
    db_session.add(completion)
    db_session.commit()
    
    db_session.delete(completion)
    db_session.commit()
    
    assert len(habit.daily_completions) == 0

def test_cascade_delete_completions(db_session):
    habit = Habit(name="Test Habit", periodicity="daily")
    db_session.add(habit)
    db_session.flush()
    
    completion = DailyCompletion(
        habit=habit,
        completed_at=datetime.now(UTC)
    )
    db_session.add(completion)
    db_session.commit()
    
    db_session.delete(habit)
    db_session.commit()
    
    # Check that completion was cascade deleted
    assert db_session.query(DailyCompletion).count() == 0