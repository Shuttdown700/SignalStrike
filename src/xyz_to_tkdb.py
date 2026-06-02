"""
Import an existing z/x/y raster tile tree into a tkintermapview offline database.

Edit the CONFIG block below, then run:  python xyz_to_tkdb.py

SERVER_LABEL is just a label stored in the DB. It MUST be byte-for-byte identical
to the tile_server you set on the TkinterMapView widget, or the widget's lookup
query returns nothing and you get a blank/grey map.

tkintermapview uses standard XYZ/slippy y (origin top-left), which is the same
convention as a z/x/y folder tree, so NO y-flip is applied here.
"""
import os, sqlite3, glob

# ---------------------------------------------------------------------------
# CONFIG  -- edit these values
# ---------------------------------------------------------------------------
TILE_DIR     = r"C:\Users\shuttdown\Documents\Coding Projects\SignalStrike\map_tiles\Terrain"                                            # root of the z/x/y tree
DB_PATH      = r"C:\Users\shuttdown\Documents\Coding Projects\SignalStrike\map_dbs\Terrain.db"                                   # output database file
SERVER_LABEL = "offline-db://terrain/{z}/{x}/{y}.png"   # MUST match the widget's tile_server
MAX_ZOOM     = 17                                                   # max zoom present in the tree
EXT          = "png"                                                # tile image extension
# ---------------------------------------------------------------------------

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS server (
           url VARCHAR(300) PRIMARY KEY NOT NULL,
           max_zoom INTEGER NOT NULL);""",
    """CREATE TABLE IF NOT EXISTS tiles (
           zoom INTEGER NOT NULL, x INTEGER NOT NULL, y INTEGER NOT NULL,
           server VARCHAR(300) NOT NULL, tile_image BLOB NOT NULL,
           CONSTRAINT pk_tiles PRIMARY KEY (zoom, x, y, server));""",
]


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    for stmt in SCHEMA:
        cur.execute(stmt)
    cur.execute("INSERT OR REPLACE INTO server (url, max_zoom) VALUES (?, ?);",
                (SERVER_LABEL, MAX_ZOOM))

    pattern = os.path.join(TILE_DIR, "*", "*", f"*.{EXT}")
    n = 0
    for path in glob.iglob(pattern):
        # .../<z>/<x>/<y>.<ext>
        y = int(os.path.splitext(os.path.basename(path))[0])
        x = int(os.path.basename(os.path.dirname(path)))
        z = int(os.path.basename(os.path.dirname(os.path.dirname(path))))
        with open(path, "rb") as f:
            blob = f.read()
        cur.execute(
            "INSERT OR REPLACE INTO tiles (zoom, x, y, server, tile_image) "
            "VALUES (?, ?, ?, ?, ?);", (z, x, y, SERVER_LABEL, blob))
        n += 1
    con.commit()
    con.close()
    print(f"Imported {n} tiles into {DB_PATH}")


if __name__ == "__main__":
    main()