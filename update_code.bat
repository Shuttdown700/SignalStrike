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
git pull
if errorlevel 1 (
    echo Error during git pull. Exiting script.
    exit /b 1
)

rem Print that the code base was updated
echo.
echo Code base was updated successfully!

rem Wait for 5 seconds using timeout
timeout /t 5 > nul

rem --- End of Script ---