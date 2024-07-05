@ECHO OFF
rem python -m pip install --upgrade pip
start "Map Tile Server" /d . python src/map_server.py localhost 1234 ./map_tiles/ESRI
start "Dynamic Tile Downloader" /d . python src/dynamic_tile_download_service.py
start "Batch Tile Downloader" /d . python src/batch_tile_download_service.py
start "EW Targeting App" /d . python src/gui.py