@echo off

rem Navigate to your git repository directory
rem cd /d C:\path\to\your\repository

rem Add all changes to the staging area
git add .

rem Prompt user to enter a commit message
set /p commit_message="Enter your commit message: "

rem Commit changes with the user-provided message
git commit -m "%commit_message%"

rem Push changes to the 'main' branch of the remote repository
git push origin main
git push mic main
