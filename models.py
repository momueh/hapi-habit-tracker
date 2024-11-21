from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, Session, declarative_base, validates
from datetime import datetime, timedelta, UTC

Base = declarative_base()

class Habit(Base):
    """
    Represents a trackable habit with daily or weekly periodicity.

    Attributes:
        id (int): Primary key
        name (str): Name of the habit
        description (str): Optional description of the habit
        periodicity (str): Frequency of the habit ('daily' or 'weekly')
        created_at (datetime): When the habit was created
        current_streak (int): Number of consecutive successful completions
        max_streak (int): Highest streak achieved
        daily_completions (list): Related DailyCompletion records
        weekly_completions (list): Related WeeklyCompletion records
    """
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

    VALID_PERIODICITIES = ['daily', 'weekly']

    @validates('periodicity')
    def validate_periodicity(self, key, periodicity):
        """Validate that periodicity is either 'daily' or 'weekly'"""
        if periodicity not in self.VALID_PERIODICITIES:
            raise ValueError(f"Periodicity must be one of: {', '.join(self.VALID_PERIODICITIES)}")
        return periodicity

    def complete(self, session: Session, completion_time=None):
        """
        Record a completion of the habit.

        Args:
            session (Session): SQLAlchemy database session
            completion_time (datetime, optional): Time of completion. Defaults to current UTC time

        Raises:
            ValueError: If habit has invalid periodicity
        """
        # Ensure completion_time is UTC-aware
        if completion_time is None:
            completion_time = datetime.now(UTC)
        elif completion_time.tzinfo is None:
            raise ValueError("completion_time must be timezone-aware")
        
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

    def _update_streak(self, completion_time):
        """
        Update the current and maximum streak based on completion time.

        Args:
            completion_time (datetime): Time of the completion
        """
        if self._is_within_period(completion_time):
            self.current_streak += 1
            self.max_streak = max(self.max_streak, self.current_streak)
        else:
            self.break_streak()

    def break_streak(self):
        """Reset the current streak to zero."""
        self.current_streak = 0

    def _is_within_period(self, completion_time):
        """
        Check if completion time is within allowed period to maintain streak.

        Args:
            completion_time (datetime): Time of the completion

        Returns:
            bool: True if completion maintains streak, False otherwise

        Raises:
            ValueError: If habit has invalid periodicity
        """
        if self.periodicity == 'daily':
            last_completion = self.daily_completions[-1] if self.daily_completions else None
            if not last_completion:
                return True
            # Ensure both dates are UTC-aware before comparison
            last_completion_date = last_completion.completed_at.replace(tzinfo=UTC).date()
            completion_date = completion_time.replace(tzinfo=UTC).date()
            return (completion_date - last_completion_date) <= timedelta(days=1)
        elif self.periodicity == 'weekly':
            last_completion = self.weekly_completions[-1] if self.weekly_completions else None
            if not last_completion:
                return True
            # Ensure both dates are UTC-aware before comparison
            current_week_start = self._get_week_start(completion_time.replace(tzinfo=UTC))
            last_week_start = self._get_week_start(last_completion.completed_at.replace(tzinfo=UTC))
            return (current_week_start - last_week_start) <= timedelta(weeks=1)
        else:
            raise ValueError(f"Invalid periodicity: {self.periodicity}")

    @staticmethod
    def _get_week_start(date):
        """
        Calculate the Monday date for the week containing the given date.

        Args:
            date (datetime): Any date within the desired week

        Returns:
            date: The Monday of that week
        """
        return date.date() - timedelta(days=date.weekday())

class DailyCompletion(Base):
    """
    Records a single completion of a daily habit.

    Attributes:
        id (int): Primary key
        habit_id (int): Foreign key to associated habit
        completed_at (datetime): When the habit was completed
        habit (Habit): Related habit object
    """
    __tablename__ = 'daily_completions'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    habit = relationship("Habit", back_populates="daily_completions")

class WeeklyCompletion(Base):
    """
    Records a single completion of a weekly habit.

    Attributes:
        id (int): Primary key
        habit_id (int): Foreign key to associated habit
        week_start (date): Monday date of the completion week
        completed_at (datetime): When the habit was completed
        habit (Habit): Related habit object
    """
    __tablename__ = 'weekly_completions'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    week_start = Column(Date, nullable=False)
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    habit = relationship("Habit", back_populates="weekly_completions")
