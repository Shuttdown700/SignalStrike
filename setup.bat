@echo off
:: Stop execution if any command fails
setlocal enabledelayedexpansion

:: Attempt to get Python version
for /f "delims=" %%v in ('python -c "import sys; print(sys.version.split()[0])" 2^>nul') do set PYTHON_VERSION=%%v

:: Check if variable was set
if not defined PYTHON_VERSION (
    echo.
    echo Python is not installed or not found in PATH. Please install Python 3.x and try again.
    echo.
    timeout /t 20
    exit /b 1
)

:: Split the version number
for /f "tokens=1,2,3 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

:: Check if Python version is >= 3.0
set /a MAJOR_CHECK=%MAJOR%
if %MAJOR_CHECK% LSS 3 (
    echo.
    echo Python version %PYTHON_VERSION% is too old. Please install Python 3.0 or higher.
    echo.
    timeout /t 20
    exit /b 1
)

echo.
echo Python is installed. Version: %PYTHON_VERSION%

:: Check if venv already exists
if exist venv\Scripts\activate (
    echo.
    echo Virtual environment already exists. Skipping creation.
    echo.
) else (
    :: Create a virtual environment named "venv"
    echo.
    echo Creating virtual environment
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo Failed to create virtual environment.
        echo.
        timeout /t 20
        exit /b %errorlevel%
    )
)

:: Change directory to the virtual environment's Scripts folder
cd venv\Scripts

:: Activate the virtual environment
echo.
echo Activating virtual environment
call activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    timeout /t 20
    exit /b %errorlevel%
)

:: Upgrade pip
echo.
echo Upgrading pip
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip.
    timeout /t 20
    exit /b %errorlevel%
)

:: Return to the root project directory
cd ..\..

:: Install required Python modules
if exist requirements.txt (
    echo.
    echo Installing required Python modules from requirements.txt
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install required modules.
        timeout /t 20
        exit /b %errorlevel%
    )
) else (
    echo requirements.txt not found. Skipping module installation.
)

echo.
echo Virtual environment setup complete!
echo.

:: Run the create_shortcuts.bat script
echo Creating shortcuts
call create_shortcuts.bat
if %errorlevel% neq 0 (
    echo Failed to run create_shortcuts.bat.
    exit /b %errorlevel%
)

timeout /t 20
echo.

exit /b 0
