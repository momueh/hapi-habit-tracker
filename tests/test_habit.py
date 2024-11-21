import pytest
from datetime import datetime, timedelta, UTC
from models import Habit, DailyCompletion, WeeklyCompletion

def test_streak_calculation_daily(db_session):
    # Create a new habit with known completion pattern
    habit = Habit(
        name="Test Daily Habit",
        description="Test habit",
        periodicity="daily"
    )
    db_session.add(habit)
    db_session.flush()

    base_time = datetime.now(UTC)
    
    # Create 3 consecutive daily completions
    for days_ago in [2, 1, 0]:  # Adding in reverse order
        completion = DailyCompletion(
            habit=habit,
            completed_at=base_time - timedelta(days=days_ago)
        )
        db_session.add(completion)
    
    db_session.commit()
    
    # Verify initial streak
    assert habit.calculate_streak() == 3
    assert habit.calculate_max_streak() == 3
    
    # Break the streak with a gap
    new_completion_time = base_time + timedelta(days=2)
    habit.complete(db_session, new_completion_time)
    
    # Verify streak is broken
    assert habit.current_streak == 1
    assert habit.max_streak == 3

def test_streak_calculation_weekly(db_session):
    # Create a new weekly habit
    habit = Habit(
        name="Test Weekly Habit",
        description="Test habit",
        periodicity="weekly"
    )
    db_session.add(habit)
    db_session.flush()

    base_time = datetime.now(UTC)
    
    # Create completions for 3 consecutive weeks
    for weeks_ago in [2, 1, 0]:
        completion_time = base_time - timedelta(weeks=weeks_ago)
        week_start = habit._get_week_start(completion_time)
        completion = WeeklyCompletion(
            habit=habit,
            completed_at=completion_time,
            week_start=week_start
        )
        db_session.add(completion)
    
    db_session.commit()
    
    # Verify initial streak
    assert habit.calculate_streak() == 3
    assert habit.calculate_max_streak() == 3
    
    # Break the streak with a gap
    new_completion_time = base_time + timedelta(weeks=2)
    habit.complete(db_session, new_completion_time)
    
    # Verify streak is broken
    assert habit.current_streak == 1
    assert habit.max_streak == 3

def test_multiple_completions_same_period(db_session):
    habit = Habit(
        name="Test Habit",
        description="Test habit",
        periodicity="daily"
    )
    db_session.add(habit)
    db_session.flush()

    base_time = datetime.now(UTC)
    
    # Add two completions on the same day
    habit.complete(db_session, base_time)
    habit.complete(db_session, base_time + timedelta(hours=2))
    
    # Should still count as streak of 1
    assert habit.current_streak == 1
    assert habit.max_streak == 1

def test_habit_completion_recording(db_session):
    habit = Habit(
        name="Test Habit",
        description="Test habit",
        periodicity="daily"
    )
    db_session.add(habit)
    db_session.flush()

    completion_time = datetime.now(UTC)
    habit.complete(db_session, completion_time)
    
    # Verify completion was recorded
    if habit.periodicity == "daily":
        completion = habit.daily_completions[0]
    else:
        completion = habit.weekly_completions[0]
    
    assert completion is not None
    assert completion.completed_at == completion_time
    assert habit.current_streak == 1
    assert habit.max_streak == 1