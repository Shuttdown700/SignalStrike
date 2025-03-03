@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

REM Upgrade pip if needed (uncomment if required)
REM python -m pip install --upgrade pip

REM Activate virtual environment
CALL .\venv\Scripts\activate.bat || (
    ECHO Failed to activate virtual environment.
    EXIT /B 1
)

REM Start Map Tile Server
ECHO Starting Map Tile Server...
START "Map Tile Server" /D . python src/map_server.py localhost 1234 ./map_tiles
IF ERRORLEVEL 1 ECHO Failed to start Map Tile Server.

REM Start Dynamic Map Tile Downloader
ECHO Starting Dynamic Tile Downloader...
START "Dynamic Tile Downloader" /D . python src/dynamic_tile_download_service.py
IF ERRORLEVEL 1 ECHO Failed to start Dynamic Tile Downloader.

REM Start EW Targeting App
ECHO Starting EW Targeting App...
START "EW Targeting App" /D . python src/gui.py
IF ERRORLEVEL 1 ECHO Failed to start EW Targeting App.

ECHO All services started.
ENDLOCAL
EXIT /B 0
