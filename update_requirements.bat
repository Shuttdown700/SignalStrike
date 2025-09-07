@echo off
REM --- Start of Script ---

REM Check if inside a virtual environment
if not defined VIRTUAL_ENV (
    REM Check if virtual environment exists, if not, create it
    if not exist venv (
        echo.
        echo Creating virtual environment...
        echo.
        python -m venv venv
    )
    
    REM Activate virtual environment
    call venv\Scripts\activate
) else (
    echo.
    echo Virtual environment already active
)

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo.
    echo Error: requirements.txt not found in the root directory.
    timeout /t 20
    exit /b 1
)

:: ------------------------------------------------------------------
:: Setup Virtual Environment
:: ------------------------------------------------------------------

:: Check if venv already exists
if exist venv\Scripts\activate (
    echo.
    echo Virtual environment already exists. Skipping creation.
) else (
    :: Create a virtual environment named "venv"
    echo.
    echo Creating virtual environment
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo Failed to create virtual environment.
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

cd ..\..

REM Upgrade pip first
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo Error: Failed to upgrade pip -- check internet connection.
    timeout /t 20
    exit /b 1
)

REM Upgrade all packages in requirements.txt
echo.
echo Installing/upgrading packages from requirements.txt...
setlocal enabledelayedexpansion
for /f "delims=" %%i in ('pip install --upgrade -r requirements.txt 2^>^&1') do (
    set "line=%%i"
    echo !line!
    set "pipOutput=!line!"
)
endlocal & set "pipOutput=%pipOutput%"

if errorlevel 1 (
    echo.
    echo Error: Failed to install/upgrade some dependencies -- check errors above.
    timeout /t 20
    exit /b 1
)

REM Check if nothing was updated (pip says "Requirement already satisfied")
echo %pipOutput% | find /i "Requirement already satisfied" >nul
if %errorlevel%==0 (
    echo.
    echo Dependencies are already up to date.
) else (
    echo.
    echo Dependencies were updated successfully.
)

REM Wait before exit
timeout /t 20 >nul
echo.
REM --- End of Script ---
