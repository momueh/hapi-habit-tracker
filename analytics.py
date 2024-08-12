from typing import List, Dict
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from models import Habit, DailyCompletion, WeeklyCompletion
from database import get_db_session

def get_all_habits(session: Session) -> List[Habit]:
    return session.query(Habit).all()

def get_habits_by_periodicity(session: Session, periodicity: str) -> List[Habit]:
    return session.query(Habit).filter(Habit.periodicity == periodicity).all()

def get_longest_run_streak(session: Session) -> int:
    return session.query(Habit).order_by(Habit.max_streak.desc()).first().max_streak

def get_longest_run_streak_for_habit(session: Session, habit_id: int) -> int:
    habit = session.get(Habit, habit_id)
    return habit.max_streak if habit else 0

def get_days_since_last_completion(session: Session, habit_id: int) -> int:
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

