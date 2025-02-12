@echo off
:: Stop execution if any command fails
setlocal enabledelayedexpansion

:: Check if Python is installed
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v

if "%PYTHON_VERSION%"=="" (
    echo Python is not installed or not found in PATH. Please install Python and try again.
    exit /b 1
) else (
    echo Python is installed. Version: %PYTHON_VERSION%
)

:: Check if venv already exists
if exist venv\Scripts\activate (
    echo Virtual environment already exists. Skipping creation.
) else (
    :: Create a virtual environment named "venv"
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        exit /b %errorlevel%
    )
)

:: Change directory to the virtual environment's Scripts folder
cd venv\Scripts

:: Activate the virtual environment
call activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    exit /b %errorlevel%
)

:: Upgrade pip
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip.
    exit /b %errorlevel%
)

:: Return to the root project directory
cd ..\..

:: Install required Python modules
if exist requirements.txt (
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install required modules.
        exit /b %errorlevel%
    )
) else (
    echo requirements.txt not found. Skipping module installation.
)

echo Virtual environment setup complete!
exit /b 0
