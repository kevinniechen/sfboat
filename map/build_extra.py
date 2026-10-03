"""Ferry routes (OpenStreetMap) and hand-drawn calm/rough water zones -> data/.

    python3 map/build_extra.py
"""
import json, os, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
MIRRORS = ["https://overpass.private.coffee/api/interpreter",
           "https://overpass-api.de/api/interpreter",
           "https://overpass.kumi.systems/api/interpreter"]
Q = '[out:json][timeout:60];way["route"="ferry"](37.6,-122.6,38.15,-122.15);out geom;'


def ferries():
    cached = os.environ.get("FERRY_JSON")   # reuse a saved Overpass response
    if cached:
        d = json.load(open(cached))
        return to_fc(d)
    for url in MIRRORS:
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": Q}).encode(),
                                         headers={"User-Agent": "sfbay-navigator/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.load(r)
            break
        except Exception as e:
            print("  overpass failed:", url, e)
    else:
        raise SystemExit("no overpass mirror worked")
    return to_fc(d)


def to_fc(d):
    feats = []
    for e in d["elements"]:
        t = e.get("tags", {})
        feats.append({"type": "Feature",
                      "properties": {"name": t.get("name"), "operator": t.get("operator")},
                      "geometry": {"type": "LineString",
                                   "coordinates": [[p["lon"], p["lat"]] for p in e["geometry"]]}})
    return {"type": "FeatureCollection", "features": feats}


def poly(*latlons):
    ring = [[lon, lat] for lat, lon in latlons]
    return {"type": "Polygon", "coordinates": [ring + [ring[0]]]}


def point(lat, lon):
    return {"type": "Point", "coordinates": [lon, lat]}


# Approximate, local-knowledge zones. kind: rough | moderate | calm.  r = radius (m) for points.
ZONES = [
    ("rough", "Golden Gate", poly((37.795, -122.535), (37.832, -122.535), (37.832, -122.466), (37.806, -122.466)),
     "The strongest currents in the Bay (4–6 kn on a big ebb). Ocean swell meets the Bay, and when the afternoon "
     "westerly blows against an ebb, waves get steep and confused. Not a beginner area."),
    ("rough", "The Slot", poly((37.808, -122.466), (37.832, -122.466), (37.852, -122.43), (37.872, -122.38),
                               (37.886, -122.33), (37.866, -122.318), (37.846, -122.37), (37.826, -122.415)),
     "From the Gate past Alcatraz toward Berkeley. The summer afternoon sea breeze funnels through here: "
     "20–25+ knots is common. It's also where the main ship traffic lanes run."),
    ("rough", "Raccoon Strait", poly((37.873, -122.455), (37.879, -122.435), (37.870, -122.422), (37.862, -122.440)),
     "Narrow passage between Tiburon and Angel Island. Current runs hard here."),
    ("rough", "Around Alcatraz", (point(37.8267, -122.4230), 700),
     "Strong currents and eddies swirl around the island, and ship lanes pass on both sides."),
    ("rough", "Point Blunt (Angel Island)", (point(37.8530, -122.4190), 600),
     "Current accelerates around the point, and it's exposed to the afternoon wind."),
    ("rough", "Bay Bridge & Yerba Buena Island", (point(37.8010, -122.3800), 900),
     "Current swirls around the bridge towers and the island. Ships turn here for Oakland, and ferries converge "
     "on the Ferry Building."),
    ("moderate", "Southern waterfront", poly((37.792, -122.386), (37.790, -122.368), (37.762, -122.362),
                                             (37.736, -122.366), (37.735, -122.379), (37.762, -122.384), (37.780, -122.385)),
     "South of the Bay Bridge along the city shore. Usually less wind than the Slot, especially in the morning, "
     "but there's still current, ferries (Oracle Park and Chase Center on event days), and ships at Anchorage 8A."),
    ("calm", "McCovey Cove / China Basin", (point(37.7775, -122.3885), 220),
     "Protected water right next to Pier 40. Calm, but full of kayaks and small boats on game days."),
    ("calm", "Clipper Cove", (point(37.8157, -122.3720), 380),
     "Small, protected cove between Treasure Island and Yerba Buena Island, and a popular anchorage. "
     "It's shallow near the edges and at the entrance, so stay in the middle and watch the depth."),
    ("calm", "Aquatic Park", (point(37.8080, -122.4225), 300),
     "Enclosed by a curved breakwater. Calm, but there are swimmers: go dead slow and give them room."),
    ("calm", "Richardson Bay", (point(37.8780, -122.4920), 1400),
     "Sheltered from the ocean swell, with lighter wind than the Slot. It's shallow outside the marked channel, "
     "and there are no-wake zones near Sausalito."),
    ("calm", "Oakland Estuary", (point(37.7880, -122.2820), 1100),
     "A long, protected channel between Oakland and Alameda: flat water. Watch for ferries, and ships near the "
     "west end."),
]


def zones():
    feats = []
    for kind, name, geom, desc in ZONES:
        props = {"kind": kind, "name": name, "desc": desc}
        if isinstance(geom, tuple):
            geom, props["r"] = geom
        feats.append({"type": "Feature", "properties": props, "geometry": geom})
    return {"type": "FeatureCollection", "features": feats}


os.makedirs(DATA, exist_ok=True)
f = ferries()
json.dump(f, open(os.path.join(DATA, "ferries.json"), "w"))
json.dump(zones(), open(os.path.join(DATA, "zones.json"), "w"))
print(len(f["features"]), "ferry routes,", len(ZONES), "zones")
