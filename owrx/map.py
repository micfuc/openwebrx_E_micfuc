from datetime import datetime, timedelta
from owrx.config import Config
from owrx.bands import Band
import threading
import time
import sys

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Location(object):
    def __dict__(self):
        return {}


class Map(object):
    sharedInstance = None
    creationLock = threading.Lock()

    @staticmethod
    def getSharedInstance():
        with Map.creationLock:
            if Map.sharedInstance is None:
                Map.sharedInstance = Map()
        return Map.sharedInstance

    def __init__(self):
        self.clients = []
        self.positions = {}
        self.positionsLock = threading.Lock()

        def removeLoop():
            loops = 0
            while True:
                try:
                    self.removeOldPositions()
                except Exception:
                    logger.exception("error while removing old map positions")
                loops += 1
                # rebuild the positions dictionary every once in a while, it consumes lots of memory otherwise
                if loops == 60:
                    try:
                        self.rebuildPositions()
                    except Exception:
                        logger.exception("error while rebuilding positions")
                    loops = 0
                time.sleep(60)

        threading.Thread(target=removeLoop, daemon=True, name="map_removeloop").start()
        super().__init__()

    def broadcast(self, update):
        for c in self.clients:
            c.write_update(update)

    def addClient(self, client):
        self.clients.append(client)
        client.write_update(
            [
                {
                    "callsign": callsign,
                    "location": record["location"].__dict__(),
                    "lastseen": record["updated"].timestamp() * 1000,
                    "mode": record["mode"],
                    "direct": record["direct"],      # by I8FUC 20230324
                    "band": record["band"].getName() if record["band"] is not None else None,
                    "hops": record["hops"],
                }
                for (callsign, record) in self.positions.items()
            ]
        )
#        print("------------------>The  positions Array is: ", self.positions)   # by I8FUC

    def removeClient(self, client):
        try:
            self.clients.remove(client)
        except ValueError:
            pass

    def updateLocation(self, callsign, loc: Location, mode: str, direct: str , band: Band = None , hops: [str] = [] ):   # by I8FUC 20230416 for rspberry operation
        pm = Config.get()
        ignoreIndirect = pm["map_ignore_indirect_reports"]
        preferRecent = pm["map_prefer_recent_reports"]
        needBroadcast = False
        ts = datetime.now()
# following 3 lines by I8FUC 20230325
        if callsign in self.positions:
           if( self.positions[callsign]["direct"] == '[DIR]') :
              direct = '[DIR]'           
#        print("------------------->The  positions Array is: ", self.positions)   # by I8FUC
#        print("\n\n\n------------------->The  hops len is : ", len(hops))   # by I8FUC
#        print("============== OLD HOPS =============>: ", hops)
        with self.positionsLock:
            # ignore indirect reports if ignoreIndirect set
            if not ignoreIndirect or len(hops)==0:
                # prefer messages with shorter hop count unless preferRecent set
                if preferRecent or callsign not in self.positions or len(hops) <= len(self.positions[callsign]["hops"]):
                    self.positions[callsign] = {"location": loc, "updated": ts, "mode": mode, "direct": direct , "band": band, "hops": hops} # by I8FUC 20230324
                    needBroadcast = True
        if needBroadcast:
            self.broadcast(
                [
                    {
                        "callsign": callsign,
                        "location": loc.__dict__(),
                        "lastseen": ts.timestamp() * 1000,
                        "mode": mode,
                        "direct": direct,       # by I8FUC 20230324
                        "band": band.getName() if band is not None else None,
                        "hops": hops,
                    }
                ]
            )
#        print("------------------->The  positions Array is: ", self.positions)   # by I8FUC

    def touchLocation(self, callsign):
        # not implemented on the client side yet, so do not use!
        ts = datetime.now()
        with self.positionsLock:
            if callsign in self.positions:
                self.positions[callsign]["updated"] = ts
        self.broadcast([{"callsign": callsign, "lastseen": ts.timestamp() * 1000}])

    def removeLocation(self, callsign):
        with self.positionsLock:
            del self.positions[callsign]
            # TODO broadcast removal to clients

    def removeOldPositions(self):
        pm = Config.get()
        retention = timedelta(seconds=pm["map_position_retention_time"])
        cutoff = datetime.now() - retention

        to_be_removed = [callsign for (callsign, pos) in self.positions.items() if pos["updated"] < cutoff]
        for callsign in to_be_removed:
            self.removeLocation(callsign)

    def rebuildPositions(self):
        logger.debug("rebuilding map storage; size before: %i", sys.getsizeof(self.positions))
        with self.positionsLock:
            p = {key: value for key, value in self.positions.items()}
            self.positions = p
        logger.debug("rebuild complete; size after: %i", sys.getsizeof(self.positions))


class LatLngLocation(Location):
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __dict__(self):
        res = {"type": "latlon", "lat": self.lat, "lon": self.lon}
        return res


class LocatorLocation(Location):
    def __init__(self, locator: str):
        self.locator = locator

    def __dict__(self):
        return {"type": "locator", "locator": self.locator}
