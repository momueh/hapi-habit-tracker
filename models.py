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
    daily_completions = relationship(
        "DailyCompletion",
        back_populates="habit",
        order_by="DailyCompletion.completed_at",  # Oldest first
        lazy="select",
        cascade="all, delete-orphan"
    )
    weekly_completions = relationship(
        "WeeklyCompletion",
        back_populates="habit",
        order_by="WeeklyCompletion.completed_at",  # Oldest first
        lazy="select",
        cascade="all, delete-orphan"
    )

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

        # Recalculate streaks after recording completion
        self.current_streak = self.calculate_streak(completion_time)
        self.max_streak = self.calculate_max_streak()

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
            self.current_streak = 1

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

    
    def calculate_streak(self, at_time=None):
        """
        Calculate the current streak based on completion history.
        
        Args:
            at_time (datetime, optional): Calculate streak as of this time
                                        Defaults to current UTC time
        Returns:
            int: Current streak count
        """
        if at_time is None:
            at_time = datetime.now(UTC)
        elif at_time.tzinfo is None:
            raise ValueError("at_time must be timezone-aware")

        completions = (self.daily_completions if self.periodicity == 'daily' 
                      else self.weekly_completions)
        
        if not completions:
            return 0

        # Check if the last completion is recent enough to count
        last_completion_date = completions[-1].completed_at.date()
        days_since_last = (at_time.date() - last_completion_date).days
    
        # If too much time has passed, streak is broken
        if (self.periodicity == 'daily' and days_since_last > 1) or \
        (self.periodicity == 'weekly' and days_since_last > 7):
            return 0

        streak = 1
        if self.periodicity == 'daily':
            # Get all completion dates and sort them
            completion_dates = sorted([c.completed_at.date() for c in completions], reverse=True)
            
            current_date = completion_dates[0]
            
            for next_date in completion_dates[1:]:
                if (current_date - next_date) == timedelta(days=1):
                    streak += 1
                    current_date = next_date
                else:
                    break
                    
        else:  # weekly
            # Get all completion weeks and sort them
            completion_weeks = sorted([self._get_week_start(c.completed_at) for c in completions], reverse=True)
            
            current_week = completion_weeks[0]
            
            for next_week in completion_weeks[1:]:
                if (current_week - next_week) == timedelta(weeks=1):
                    streak += 1
                    current_week = next_week
                else:
                    break

        return streak 

    def calculate_max_streak(self):
        """
        Calculate the maximum streak achieved based on completion history.
        
        Returns:
            int: Maximum streak achieved
        """
        completions = (self.daily_completions if self.periodicity == 'daily' 
                      else self.weekly_completions)
        
        if not completions:
            return 0

        max_streak = current_streak = 1
        
        if self.periodicity == 'daily':
            completion_dates = sorted([c.completed_at.date() for c in completions])
            current_date = completion_dates[0]
            
            for next_date in completion_dates[1:]:
                if (next_date - current_date) == timedelta(days=1):
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
                current_date = next_date
        else:  # weekly
            completion_weeks = sorted([self._get_week_start(c.completed_at) for c in completions])
            current_week = completion_weeks[0]
            
            for next_week in completion_weeks[1:]:
                if (next_week - current_week) == timedelta(weeks=1):
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
                current_week = next_week

        return max_streak
    
    def get_last_completion(self):
        """
        Get the most recent completion time for the habit.

        Returns:
            datetime: The last completion time, or None if never completed
        """
        if self.periodicity == 'daily':
            last_completion = (self.daily_completions[-1]
                         if self.daily_completions 
                         else None)
        else:  # weekly
            last_completion = (self.weekly_completions[-1]
                         if self.weekly_completions 
                         else None)
    
        return last_completion.completed_at if last_completion else None

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
