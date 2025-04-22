@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

REM Optional: Upgrade pip (uncomment if needed)
REM python -m pip install --upgrade pip

REM Activate virtual environment
CALL .\venv\Scripts\activate.bat || (
    ECHO [ERROR] Failed to activate virtual environment.
    EXIT /B 1
)

ECHO [INFO] Starting PyTest Session in seperate terminal
START "PyTest Session" /D . cmd /c "pytest ./tests && timeout /t 20"
IF ERRORLEVEL 1 (
    ECHO [ERROR] Failed to start test suite.
    EXIT /B 1
)
