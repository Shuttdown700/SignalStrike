@ECHO OFF
start "Map Tile Server" /d . python map_server.py localhost 1234 ./map_tiles/ESRI
start "EW Targeting App" /d . python src/gui.py