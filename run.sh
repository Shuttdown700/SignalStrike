python src/gui.py &
python src/map_server.py localhost 1234 ./map_tiles/ESRI &
python src/dynamic_tile_download_service.py
python src/batch_tile_download_service.py