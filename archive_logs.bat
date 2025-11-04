@echo off
setlocal enabledelayedexpansion

:: Create timestamp in format YYYYMMDDHHMMSS
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%%datetime:~8,2%%datetime:~10,2%%datetime:~12,2%

:: Set paths
set LOG_DIR=.\logs
set OUT_DIR=.\logs_archived
set OUT_FILE=%OUT_DIR%\%timestamp%_SignalStrike_logs.zip

:: Ensure output directory exists
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

:: Compress all files in ./logs into the zip
powershell -command "Compress-Archive -Path '%LOG_DIR%\*' -DestinationPath '%OUT_FILE%' -Force"

echo Logs compressed to %OUT_FILE%
endlocal
pause
