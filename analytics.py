from typing import List, Dict
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from models import Habit, DailyCompletion, WeeklyCompletion
from database import get_db_session

def get_all_habits(session: Session) -> List[Habit]:
    """
    Retrieve all habits from the database.

    Args:
        session (Session): SQLAlchemy database session

    Returns:
        List[Habit]: List of all habit objects
    """
    return session.query(Habit).all()

def get_habits_by_periodicity(session: Session, periodicity: str) -> List[Habit]:
    """
    Retrieve habits filtered by their periodicity (daily/weekly).

    Args:
        session (Session): SQLAlchemy database session
        periodicity (str): The periodicity to filter by ('daily' or 'weekly')

    Returns:
        List[Habit]: List of filtered habit objects
    """
    return session.query(Habit).filter(Habit.periodicity == periodicity).all()

def get_longest_run_streak(session: Session) -> int:
    """
    Get the longest streak across all habits.

    Args:
        session (Session): SQLAlchemy database session

    Returns:
        int: Maximum streak value across all habits
    """
    return session.query(Habit).order_by(Habit.max_streak.desc()).first().max_streak

def get_longest_run_streak_for_habit(session: Session, habit_id: int) -> int:
    """
    Get the longest streak for a specific habit.

    Args:
        session (Session): SQLAlchemy database session
        habit_id (int): ID of the habit

    Returns:
        int: Maximum streak value for the specified habit, 0 if habit not found
    """
    habit = session.get(Habit, habit_id)
    return habit.max_streak if habit else 0

def get_days_since_last_completion(session: Session, habit_id: int) -> int:
    """
    Calculate days elapsed since the last completion of a habit.

    Args:
        session (Session): SQLAlchemy database session
        habit_id (int): ID of the habit

    Returns:
        int: Number of days since last completion, None if habit not found or never completed
    """
    habit = session.get(Habit, habit_id)
    if not habit:
        return None
    
    if habit.periodicity == 'daily':
        last_completion = session.query(DailyCompletion).filter(DailyCompletion.habit_id == habit_id).order_by(DailyCompletion.completed_at.desc()).first()
    else:
        last_completion = session.query(WeeklyCompletion).filter(WeeklyCompletion.habit_id == habit_id).order_by(WeeklyCompletion.completed_at.desc()).first()
    
    if last_completion:
        # Ensure last_completion.completed_at is UTC-aware
        last_completion_time = last_completion.completed_at.replace(tzinfo=UTC)
        return (datetime.now(UTC) - last_completion_time).days
    return None

