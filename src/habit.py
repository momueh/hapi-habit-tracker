import datetime
from typing import List


class Habit:
    """
    Represents a habit that a user wants to track.
    Attributes:
        name (str): The name of the habit (e.g., "Drink Water").
        periodicity (str): The periodicity of the habit (e.g., "daily", "weekly").
        creation_date (datetime.date): The date when the habit was created.
        completion_dates (List[datetime.date]): A list of dates when the habit was completed.
    """

    def __init__(
        self,
        name: str,
        periodicity: str,
        creation_date: datetime.date = None,
        completion_dates: List[datetime.date] = None,
    ):
        """
        Initializes a new Habit object.
        """

        self.name = name
        self.periodicity = periodicity
        self.creation_date = creation_date or datetime.date.today()
        self.completion_dates = completion_dates or []

    def complete(self, date: datetime.date = None):
        """
        Marks the habit as completed on the given date.

        Args:
            date (datetime.date, optional): The completion date. Defaults to the current date.
        """
        if date and date < self.creation_date:
            raise ValueError("Completion date cannot be before creation date.")
        self.completion_dates.append(date or datetime.date.today())
