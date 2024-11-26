import pytest
from datetime import datetime, UTC
from models import Habit, WeeklyCompletion

def test_create_weekly_completion(db_session):
    habit = Habit(name="Test Habit", periodicity="weekly")
    db_session.add(habit)
    db_session.flush()
    
    completion_time = datetime.now(UTC)
    completion = WeeklyCompletion(
        habit=habit,
        completed_at=completion_time,
        week_start=habit._get_week_start(completion_time)
    )
    db_session.add(completion)
    db_session.commit()
    
    assert completion.id is not None
    assert completion.habit_id == habit.id
    assert completion.week_start == habit._get_week_start(completion_time)

def test_delete_weekly_completion(db_session):
    habit = Habit(name="Test Habit", periodicity="weekly")
    db_session.add(habit)
    db_session.flush()
    
    completion_time = datetime.now(UTC)
    completion = WeeklyCompletion(
        habit=habit,
        completed_at=completion_time,
        week_start=habit._get_week_start(completion_time)
    )
    db_session.add(completion)
    db_session.commit()
    
    db_session.delete(completion)
    db_session.commit()
    
    assert len(habit.weekly_completions) == 0

def test_cascade_delete_weekly_completions(db_session):
    habit = Habit(name="Test Habit", periodicity="weekly")
    db_session.add(habit)
    db_session.flush()
    
    completion_time = datetime.now(UTC)
    completion = WeeklyCompletion(
        habit=habit,
        completed_at=completion_time,
        week_start=habit._get_week_start(completion_time)
    )
    db_session.add(completion)
    db_session.commit()
    
    db_session.delete(habit)
    db_session.commit()
    
    # Check that completion was cascade deleted
    assert db_session.query(WeeklyCompletion).count() == 0