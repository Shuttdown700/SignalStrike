@ECHO OFF
start "Map Tile Server" /d . python -m http.server 1234 --directory ./map_tiles/ESRI
start "EW Targeting App" /d . python src/gui.py