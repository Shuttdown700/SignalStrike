@echo off
rem --- Start of Script ---

rem Fetch the latest changes from the remote repository
echo Fetching the latest changes...
git fetch
if errorlevel 1 (
    echo Error during git fetch. Exiting script.
    exit /b 1
)

rem Pull the latest changes from the remote repository into the current branch
echo Pulling the latest changes...
setlocal enabledelayedexpansion
for /f "delims=" %%i in ('git pull 2^>^&1') do (
    set "line=%%i"
    echo !line!
    set "gitOutput=!line!"
)
endlocal & set "gitOutput=%gitOutput%"

if errorlevel 1 (
    echo Error during git pull. Exiting script.
    exit /b 1
)

rem Check if Git said it was already up to date
echo.
echo %gitOutput% | find /i "Already up to date." >nul
if %errorlevel%==0 (
    echo Code base is already up to date.
) else (
    echo Code base was updated successfully!
)

rem Wait for 5 seconds using timeout
timeout /t 5 >nul
echo.

rem --- End of Script ---
