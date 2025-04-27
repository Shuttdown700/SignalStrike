@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

REM Optional: Upgrade pip (uncomment if needed)
REM python -m pip install --upgrade pip

REM Activate virtual environment
CALL .\venv\Scripts\activate.bat || (
    ECHO [ERROR] Failed to activate virtual environment.
    EXIT /B 1
)

ECHO [INFO] Starting Map Tile Downloader...
START "Map Tile Downloader" /D . python src/batch_tile_download.py
IF ERRORLEVEL 1 (
    ECHO [ERROR] Failed to start Map Tile Downloader.
    EXIT /B 1
)

ECHO [INFO] Map Tile Downloader started successfully.
ENDLOCAL
timeout /t 100
echo.
EXIT /B 0
