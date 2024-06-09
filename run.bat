@ECHO OFF
start "EW Targeting App" /d . python src/gui.py
start "Map Tile Server" /d . python src/map_server.py localhost 1234 ./map_tiles/ESRI
start "Tile Download Service" /d . python src/download_tile_service.py
