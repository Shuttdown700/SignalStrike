@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

REM =========================================
REM Activate virtual environment
REM =========================================
CALL .\venv\Scripts\activate.bat || (
    ECHO [ERROR] Failed to activate virtual environment.
    EXIT /B 1
)

ECHO [INFO] Starting PyTest Session in separate terminal...

REM =========================================
REM Run pytest in new terminal
REM - If SUCCESS → wait 20 seconds then close
REM - If FAILURE → wait indefinitely until keypress
REM =========================================
START "PyTest Session" /D . cmd /c "pytest ./tests && timeout /t 20 || (echo [ERROR] Tests failed. Press any key to close... & pause)"
