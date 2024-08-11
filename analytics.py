from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Habit
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
    if habit and habit.completions:
        last_completion = max(completion.completed_at for completion in habit.completions)
        return (datetime.now() - last_completion).days
    return None

def get_completion_rate_for_habit(session: Session, habit_id: int, days: int) -> float:
    habit = session.get(Habit, habit_id)
    if not habit:
        return 0.0
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    completions = [c for c in habit.completions if start_date <= c.completed_at <= end_date]
    expected_completions = days if habit.periodicity == 'daily' else days // 7
    return len(completions) / expected_completions if expected_completions > 0 else 0.0

def get_all_habits_completion_rates(session: Session, days: int) -> Dict[str, float]:
    habits = get_all_habits(session)
    return {habit.name: get_completion_rate_for_habit(session, habit.id, days) for habit in habits}

def get_overall_completion_rate(session: Session, days: int) -> float:
    habits = get_all_habits(session)
    total_completions = 0
    total_expected_completions = 0
    
    for habit in habits:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        completions = [c for c in habit.completions if start_date <= c.completed_at <= end_date]
        total_completions += len(completions)
        total_expected_completions += days if habit.periodicity == 'daily' else days // 7
    
    return total_completions / total_expected_completions if total_expected_completions > 0 else 0.0