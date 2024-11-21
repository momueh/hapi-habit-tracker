@echo off

REM Try python3 first, fall back to python if not found
where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

%PYTHON_CMD% -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
%PYTHON_CMD% main.py