from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, Session, declarative_base
from datetime import datetime, timedelta, UTC

Base = declarative_base()

class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    periodicity = Column(String, nullable=False)  # 'daily' or 'weekly'
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    daily_completions = relationship("DailyCompletion", back_populates="habit")
    weekly_completions = relationship("WeeklyCompletion", back_populates="habit")

    def complete(self, session: Session, completion_time=None):
        completion_time = completion_time or datetime.now(UTC)
        
        if self.periodicity == 'daily':
            new_completion = DailyCompletion(habit=self, completed_at=completion_time)
            session.add(new_completion)
            self._update_streak(completion_time)
        elif self.periodicity == 'weekly':
            week_start = self._get_week_start(completion_time)
            existing_completion = session.query(WeeklyCompletion).filter(
                WeeklyCompletion.habit_id == self.id,
                WeeklyCompletion.week_start == week_start
            ).first()
            
            if existing_completion:
                # Update existing completion if it's earlier than the new one
                if completion_time > existing_completion.completed_at:
                    existing_completion.completed_at = completion_time
            else:
                new_completion = WeeklyCompletion(habit=self, week_start=week_start, completed_at=completion_time)
                session.add(new_completion)
                self._update_streak(completion_time)
        else:
            raise ValueError(f"Invalid periodicity: {self.periodicity}")

    def _update_streak(self, completion_time):
        if self._is_within_period(completion_time):
            self.current_streak += 1
            self.max_streak = max(self.max_streak, self.current_streak)
        else:
            self.break_streak()

    def break_streak(self):
        self.current_streak = 0

    def _is_within_period(self, completion_time):
        if self.periodicity == 'daily':
            last_completion = self.daily_completions[-1] if self.daily_completions else None
            if not last_completion:
                return True
            return (completion_time.date() - last_completion.completed_at.date()) <= timedelta(days=1)
        elif self.periodicity == 'weekly':
            last_completion = self.weekly_completions[-1] if self.weekly_completions else None
            if not last_completion:
                return True
            current_week_start = self._get_week_start(completion_time)
            last_week_start = self._get_week_start(last_completion.completed_at)
            return (current_week_start - last_week_start) <= timedelta(weeks=1)
        else:
            raise ValueError(f"Invalid periodicity: {self.periodicity}")

    @staticmethod
    def _get_week_start(date):
        return date.date() - timedelta(days=date.weekday())

class DailyCompletion(Base):
    __tablename__ = 'daily_completions'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    completed_at = Column(DateTime, default=lambda: datetime.now(UTC))
    habit = relationship("Habit", back_populates="daily_completions")

class WeeklyCompletion(Base):
    __tablename__ = 'weekly_completions'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    week_start = Column(Date, nullable=False)
    completed_at = Column(DateTime, default=lambda: datetime.now(UTC))
    habit = relationship("Habit", back_populates="weekly_completions")
