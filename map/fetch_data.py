"""Pull SF Bay chart features from NOAA ENC Direct into data/enc.json.

Run occasionally (charts change rarely):  python3 map/fetch_data.py
"""
import json, os, urllib.request, urllib.parse

BBOX = "-122.80,37.55,-122.15,38.12"
BASE = "https://encdirect.noaa.gov/arcgis/rest/services/encdirect/{svc}/MapServer/{lid}/query"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "enc.json")

# group -> list of (service, layer id). Earlier sources win when de-duplicating.
SOURCES = {
    "lanes":        [("enc_approach", 220), ("enc_harbour", 215)],
    "sepzones":     [("enc_approach", 219), ("enc_harbour", 214)],
    "precaution":   [("enc_approach", 216), ("enc_harbour", 211)],
    "deepwater":    [("enc_approach", 212), ("enc_harbour", 207)],
    "fairways":     [("enc_harbour", 208), ("enc_approach", 213)],
    "dredged":      [("enc_harbour", 228), ("enc_approach", 233)],
    "restricted":   [("enc_harbour", 197), ("enc_approach", 202)],
    "anchorage":    [("enc_harbour", 186), ("enc_approach", 191)],
    "buoys":        [("enc_harbour", 6), ("enc_harbour", 7), ("enc_harbour", 5), ("enc_harbour", 4),
                     ("enc_harbour", 8), ("enc_approach", 8), ("enc_approach", 9), ("enc_approach", 7),
                     ("enc_approach", 6), ("enc_approach", 10)],
    "beacons":      [("enc_harbour", 1), ("enc_harbour", 2), ("enc_approach", 3), ("enc_approach", 4),
                     ("enc_approach", 2)],
    "rocks":        [("enc_harbour", 34), ("enc_approach", 37)],
    "wrecks":       [("enc_harbour", 36), ("enc_approach", 39)],
    "obstructions": [("enc_harbour", 33), ("enc_approach", 36)],
}
KEEP = {"OBJNAM", "INFORM", "ORIENT", "COLOUR", "COLPAT", "BOYSHP", "BCNSHP", "CATLAM", "DRVAL1",
        "DRVAL2", "VALSOU", "CATRES", "RESTRN", "WATLEV", "CATWRK", "CATOBS", "CATTSS", "NINFOM",
        "TRAFIC", "OBJL"}


def query(svc, lid):
    params = dict(where="1=1", geometry=BBOX, geometryType="esriGeometryEnvelope", inSR=4326,
                  outSR=4326, outFields="*", f="geojson", geometryPrecision=6)
    url = BASE.format(svc=svc, lid=lid) + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r).get("features", [])


def key(f):
    p, g = f["properties"], f["geometry"] or {}
    if g.get("type") == "Point":
        x, y = g["coordinates"][:2]
        return (p.get("OBJNAM") or "", round(x, 4), round(y, 4))
    return (p.get("OBJNAM") or "", p.get("INFORM") or "", p.get("ORIENT"),
            json.dumps(g)[:80] if not (p.get("OBJNAM") or p.get("INFORM")) else "")


out = {}
for group, srcs in SOURCES.items():
    seen, feats = set(), []
    for svc, lid in srcs:
        try:
            fs = query(svc, lid)
        except Exception as e:
            print(f"  ! {svc}/{lid}: {e}")
            continue
        for f in fs:
            if not f.get("geometry"):
                continue
            k = key(f)
            if k in seen:
                continue
            seen.add(k)
            f["properties"] = {a: b for a, b in f["properties"].items()
                               if a in KEEP and b not in (None, "", " ")}
            feats.append(f)
    out[group] = {"type": "FeatureCollection", "features": feats}
    print(f"{group:13s} {len(feats)}")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), separators=(",", ":"))
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")
