# Habit Tracker

A simple CLI habit tracking application.

## Requirements

-   Python 3.12 or higher
    Note: If your system uses `python` instead of `python3`, you may have to replace `python3` with `python` in the commands.

## Installation and Setup

1. Clone this repository or unzip the project files

    ```
    git clone https://github.com/momueh/habit-tracker.git
    cd habit-tracker
    ```

2. Run the setup script:

    On macOS and Linux:

    ```
    ./setup.sh
    ```

    On Windows:

    ```
    setup.bat
    ```

    This script will:

    - Create a virtual environment
    - Activate the virtual environment
    - Install required packages

## Running the Application

After the initial setup, you can run the application by:

    ```
    python3 main.py
    ```

When you first run the application, it will:

1. Create a local SQLite database file (habits.db) to store your habits and completion data
2. Populate the database with example habits

These predefined habits help demonstrate the app's features and give you a starting point. You can modify or delete them at any time.

## Using the Application

The application uses a command-line interface where you navigate by entering the number corresponding to your desired action. The interactive menu provides the following options:

1. Complete a Habit
2. Add a Habit
3. Edit a Habit
4. Delete a Habit
5. Analytics
6. Exit

When you start the application, you'll see a list of your habits with their IDs, names, and other details. To interact with specific habits, you'll need to reference their ID number.

For example, when editing a habit:

1. Select "3" for "Edit a Habit"
2. Enter the habit ID number shown in the habits overview
3. You can then modify the habit's name and description
   Note: Changing a habit's periodicity (daily/weekly) is currently not supported.

When completing a habit:

1. Select "1" for "Complete a Habit"
2. Enter the ID of the habit you want to mark as completed

To add a new habit:

1. Select "2" for "Add a Habit"
2. Enter the name for your new habit
3. Enter a description
4. Choose the periodicity (daily or weekly)

To delete a habit:

1. Select "5" for "Delete a Habit"
2. Enter the ID of the habit you want to remove

The Analytics section (option 5) opens a new submenu and provides insights into your habit completion rates and streaks.

To exit the application, select option 6.

## Project Structure

-   `main.py`: The main application file containing the CLI interface and core application logic. It handles user interactions, menu displays, and coordinates between different components.

-   `models.py`: Defines the database models using SQLAlchemy ORM. Contains the Habit class with streak tracking logic and completion models for both daily and weekly habits.

-   `database.py`: Manages database operations including initialization, session management, and seeding of example data. Handles both production and test database setups.

-   `analytics.py`: Contains functions for analyzing habit data, including streak calculations, habit filtering, and completion statistics.

-   `setup.sh`/`setup.bat`: Setup scripts for Unix-based systems and Windows respectively. They create a virtual environment, install dependencies, and launch the application.

-   `requirements.txt`: Lists all Python package dependencies required by the application.

-   `tests/`: Directory containing test files

    -   `test_analytics.py`: Unit tests for the analytics functionality

-   `habits.db`: SQLite database file (created on first run) that stores all habit and completion data.

## Running Tests

```bash
python3 -m pytest tests
```

The test suite uses a separate test database (`test_habits.db`) that's completely isolated from your main habits database (`habits.db`). This ensures that:

-   Your actual habit data is never affected by running tests
-   Tests run against a clean, predictable database state
-   Test data and production data remain separate

When you run the tests:

1. If the test database doesn't exist, it's created
2. Before each testcase runs:
    - All existing test data is cleared
3. Tests are executed against this clean test database state
