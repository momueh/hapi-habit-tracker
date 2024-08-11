from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    periodicity = Column(String, nullable=False)  # 'daily' or 'weekly' TODO (no enums in sqlite), add monthly, quarterly
    created_at = Column(DateTime, default=datetime.utcnow)
    completions = relationship("Completion", back_populates="habit")

    def __repr__(self):
        return f"<Habit(name='{self.name}', periodicity='{self.periodicity}')>"

class Completion(Base):
    __tablename__ = 'completions'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    completed_at = Column(DateTime, default=datetime.utcnow)
    habit = relationship("Habit", back_populates="completions")

    def __repr__(self):
        return f"<Completion(habit_id={self.habit_id}, completed_at='{self.completed_at}')>"