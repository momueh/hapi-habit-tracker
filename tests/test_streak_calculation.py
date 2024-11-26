import pytest
from datetime import datetime, timedelta, UTC
from models import Habit, DailyCompletion, WeeklyCompletion

def test_daily_streak_four_weeks_continuous(db_session):
    habit = Habit(
        name="Daily Streak Test",
        description="Test habit",
        periodicity="daily"
    )
    db_session.add(habit)
    db_session.flush()

    base_time = datetime.now(UTC)
    # Create 28 consecutive daily completions (4 weeks)
    for days_ago in range(27, -1, -1):
        completion = DailyCompletion(
            habit=habit,
            completed_at=base_time - timedelta(days=days_ago)
        )
        db_session.add(completion)
    
    db_session.commit()
    
    assert habit.calculate_streak() == 28
    assert habit.calculate_max_streak() == 28

def test_daily_streak_with_gaps(db_session):
    habit = Habit(
        name="Daily Streak Gap Test",
        description="Test habit",
        periodicity="daily"
    )
    db_session.add(habit)
    db_session.flush()

    base_time = datetime.now(UTC)
    
    # Pattern: 10 days, 2 day gap, 5 days, 1 day gap, 3 days
    completion_days = (
        list(range(27, 17, -1)) +  # 10 days
        list(range(15, 10, -1)) +  # 5 days
        list(range(8, 5, -1))      # 3 days
    )
    
    for days_ago in completion_days:
        completion = DailyCompletion(
            habit=habit,
            completed_at=base_time - timedelta(days=days_ago)
        )
        db_session.add(completion)
    
    db_session.commit()
    
    assert habit.calculate_streak() == 0  # Current streak is 0 (no recent completions)
    assert habit.calculate_max_streak() == 10  # Longest streak was 10 days

def test_weekly_streak_four_weeks_continuous(db_session):
    habit = Habit(
        name="Weekly Streak Test",
        description="Test habit",
        periodicity="weekly"
    )
    db_session.add(habit)
    db_session.flush()

    base_time = datetime.now(UTC)
    
    # Create completions for 4 consecutive weeks
    for weeks_ago in range(3, -1, -1):
        completion_time = base_time - timedelta(weeks=weeks_ago)
        week_start = habit._get_week_start(completion_time)
        completion = WeeklyCompletion(
            habit=habit,
            completed_at=completion_time,
            week_start=week_start
        )
        db_session.add(completion)
    
    db_session.commit()
    
    assert habit.calculate_streak() == 4
    assert habit.calculate_max_streak() == 4

def test_weekly_streak_with_gaps(db_session):
    habit = Habit(
        name="Weekly Streak Gap Test",
        description="Test habit",
        periodicity="weekly"
    )
    db_session.add(habit)
    db_session.flush()

    base_time = datetime.now(UTC)
    
    # Pattern: 3 weeks, 2 week gap, 2 weeks, 1 week gap, 2 weeks
    completion_weeks = (
        list(range(8, 5, -1)) +    # 3 weeks
        list(range(3, 1, -1)) +    # 2 weeks
        list(range(0, -2, -1))     # 2 recent weeks
    )
    
    for weeks_ago in completion_weeks:
        completion_time = base_time - timedelta(weeks=weeks_ago)
        week_start = habit._get_week_start(completion_time)
        completion = WeeklyCompletion(
            habit=habit,
            completed_at=completion_time,
            week_start=week_start
        )
        db_session.add(completion)
    
    db_session.commit()
    
    assert habit.calculate_streak() == 2  # Current streak is 2 weeks
    assert habit.calculate_max_streak() == 3  # Longest streak was 3 weeks
