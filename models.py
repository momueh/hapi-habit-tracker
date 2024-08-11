from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    periodicity = Column(String, nullable=False)  # 'daily' or 'weekly'
    created_at = Column(DateTime, default=datetime.utcnow)
    completions = relationship("Completion", back_populates="habit")
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)

    def complete(self, session: Session, completion_time=None):
        completion_time = completion_time or datetime.utcnow()
        
        if self._is_within_period(completion_time):
            self.current_streak += 1
            self.max_streak = max(self.max_streak, self.current_streak)
        else:
            self.break_streak()
        
        new_completion = Completion(habit=self, completed_at=completion_time)
        session.add(new_completion)
        return new_completion

    def break_streak(self):
        self.current_streak = 0

    def _is_within_period(self, completion_time):
        last_completion = self.completions[0] if self.completions else None
        if not last_completion:
            return True
        
        if self.periodicity == 'daily':
            return (completion_time - last_completion.completed_at) <= timedelta(days=1)
        elif self.periodicity == 'weekly':
            return (completion_time - last_completion.completed_at) <= timedelta(weeks=1)
        else:
            raise ValueError(f"Invalid periodicity: {self.periodicity}")

    def check_streak(self, current_time=None):
        current_time = current_time or datetime.utcnow()
        if self.completions and not self._is_within_period(current_time):
            self.break_streak()

    def __repr__(self):
        return f"<Habit(name='{self.name}', periodicity='{self.periodicity}', current_streak={self.current_streak}, max_streak={self.max_streak})>"

class Completion(Base):
    __tablename__ = 'completions'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    completed_at = Column(DateTime, default=datetime.utcnow)
    habit = relationship("Habit", back_populates="completions")

    def __repr__(self):
        return f"<Completion(habit_id={self.habit_id}, completed_at='{self.completed_at}')>"