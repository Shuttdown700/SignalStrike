@echo off

rem Navigate to your git repository directory
rem cd /d C:\path\to\your\repository

rem Fetch the latest changes from the remote repository
git fetch

rem Pull the latest changes from the remote repository into the current branch
git pull

rem Print that the code base was updated
echo.
echo Code Base was updated!

rem Sleep for 5 seconds
ping 127.0.0.1 -n 6 > nul