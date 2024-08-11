# Habit Tracker

A simple CLI habit tracking application developed as a university project.

## Requirements

- Python 3.12 or higher

## Installation and Setup

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/habit-tracker.git
   cd habit-tracker
   ```

2. (Optional but recommended) Create and activate a virtual environment:

   On macOS and Linux:

   ```
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Run the setup script:

   On macOS and Linux:

   ```
   ./setup.sh
   ```

   On Windows:

   ```
   setup.bat
   ```

   This script will:

   - Install required packages
   - Initialize the SQLite database
   - Set up predefined habits

## Running the Application

After completing the setup, you can run the application with:

```
python src/main.py
```

## Available Commands

- `add`: Create a new habit
- `list`: List all habits
- `check`: Mark a habit as completed for today
- `analyze`: View analytics for your habits

Example usage:

```
python src/main.py create "Daily Exercise" --period daily
python src/main.py list
python src/main.py complete "Daily Exercise"
python src/main.py analyze
```

## Running Tests

To run the test suite:

```
python -m unittest discover tests
```

## Project Structure

```
habit_tracker/
│
├── src/
│   ├── main.py
│   ├── cli.py
│   ├── habit.py
│   ├── database.py
│   └── analytics.py
│
├── tests/
│   ├── test_habit.py
│   ├── test_database.py
│   └── test_analytics.py
│
├── setup.sh
├── setup.bat
├── requirements.txt
└── README.md
```

## Troubleshooting

If you encounter any issues:

1. Ensure you're using Python 3.12 or higher
2. Make sure you've activated the virtual environment (if used)
3. Try removing the `venv` directory and the `habit_tracker.db` file, then run the setup script again

## Contributing

This is a university project and is not open for contributions.


## Packaging

Use pip install -e

then run:

hapi