from utilities import import_libraries
libraries = [['winsdk']]
import_libraries(libraries)

import asyncio
import winsdk.windows.devices.geolocation as wdg
import time


async def getCoords():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return [pos.coordinate.latitude, pos.coordinate.longitude]


def getLoc():
    try:
        return asyncio.run(getCoords())
    except PermissionError:
        print("ERROR: You need to allow applications to access you location in Windows settings")


print(getLoc())
time.sleep(5)