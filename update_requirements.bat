@echo off
REM Batch script to update Python libraries from requirements.txt

REM Check if inside a virtual environment
if not defined VIRTUAL_ENV (
    REM Check if virtual environment exists, if not, create it
    if not exist venv (
        echo Creating virtual environment...
        python -m venv venv
    )
    
    REM Activate virtual environment
    call venv\Scripts\activate
) else (
    echo Virtual environment already active.
)

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo Error: requirements.txt not found in the root directory.
    exit /b 1
)

REM Upgrade pip first
python -m pip install --upgrade pip

REM Upgrade all packages in requirements.txt
pip install --upgrade -r requirements.txt

echo.
echo All dependencies in requirements.txt have been updated.
echo.

rem Wait for 5 seconds using timeout
timeout /t 5 > nul
