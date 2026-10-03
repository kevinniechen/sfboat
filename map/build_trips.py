"""Classic SF Bay trips from Pier 40 -> data/trips.json, with every leg checked against NOAA land.

    .venv/bin/python map/build_trips.py
"""
import json, math, os, sys
from shapely import wkt
from shapely.geometry import LineString, Point

HERE = os.path.dirname(os.path.abspath(__file__))
LAND = wkt.loads(open(os.path.join(HERE, "data", "land.wkt")).read())

# ---- shared legs (lat, lon) -----------------------------------------------------------------
OUT_NORTH = [(37.7808, -122.3858), (37.7819, -122.3847), (37.7826, -122.3845), (37.7829, -122.3818), (37.7840, -122.3790)]
OUT_SOUTH = [(37.7795, -122.3852), (37.7784, -122.3852), (37.7776, -122.3858)]
CITY_FRONT = [(37.7935, -122.3835), (37.8010, -122.3895), (37.8080, -122.3965), (37.8135, -122.4060), (37.8150, -122.4180)]
TO_GATE = [(37.8140, -122.4300), (37.8125, -122.4420), (37.8115, -122.4600), (37.8130, -122.4740)]
SLOT_TO_SAUSALITO = [(37.8290, -122.4400), (37.8450, -122.4640), (37.8505, -122.4710)]
SAUSALITO_FRONT = [(37.8580, -122.4760)]
RACCOON_W = [(37.8570, -122.4620), (37.8625, -122.4535)]
RACCOON_E = [(37.8690, -122.4470)]
AYALA = [(37.8715, -122.4400), (37.8700, -122.4362)]
ANGEL_EAST = [(37.8738, -122.4330), (37.8728, -122.4200), (37.8680, -122.4110), (37.8590, -122.4100), (37.8500, -122.4150)]
HOME_FROM_NORTH = [(37.8350, -122.4050), (37.8150, -122.3950), (37.8060, -122.3880), (37.7935, -122.3835), (37.7840, -122.3790)]
IN_NORTH = list(reversed(OUT_NORTH))


def r(*legs):
    pts = []
    for leg in legs:
        for p in leg:
            if not pts or pts[-1] != p:
                pts.append(p)
    return pts


CITY_FRONT_BACK = list(reversed(CITY_FRONT))
SOUTH_SHORE = [(37.7780, -122.3830), (37.7760, -122.3800), (37.7720, -122.3790), (37.7600, -122.3760), (37.7480, -122.3700), (37.7400, -122.3620), (37.7330, -122.3540)]
LOOP_NORTH = [(37.8240, -122.4120), (37.8350, -122.4050)] + list(reversed(ANGEL_EAST)) + RACCOON_E + list(reversed(RACCOON_W))
SAUSALITO_TO_GATE = [(37.8580, -122.4745), (37.8500, -122.4700), (37.8420, -122.4680), (37.8365, -122.4665), (37.8270, -122.4700), (37.8130, -122.4740)]

TRIPS = [
    {
        "id": "clipper-cove", "name": "Clipper Cove hangout", "pop": 5, "level": "beginner+",
        "hours": "2–4 hrs (or overnight)", "kind": "Your backyard anchorage",
        "summary": "The local favorite anchorage, and the closest one to you: a short hop around Yerba Buena Island into a calm "
                   "cove with the skyline in front of you. Drop the hook, raft up with friends, swim if you're brave, and stay "
                   "for the Bay Bridge lights after dark.",
        "why": "Close, calm even when the Central Bay is howling, and different every time: busy raft-ups on weekends, "
               "nearly empty midweek. Locals pick it as a top overnight spot for the night view of the bridge and the city.",
        "when": "Any day. Enter near high tide (shallow entrance). Weekday evenings are quiet; weekends are social.",
        "route": r(OUT_NORTH, [(37.7930, -122.3650), (37.8030, -122.3510), (37.8120, -122.3505), (37.8160, -122.3560),
                               (37.8155, -122.3690)],
                   [(37.8160, -122.3560), (37.8120, -122.3505), (37.8030, -122.3510), (37.7930, -122.3650)], IN_NORTH),
        "stops": [
            {"at": (37.8155, -122.3690), "name": "Clipper Cove anchorage", "type": "anchor",
             "notes": "Protected on three sides, 12–18 ft with a mud/sand bottom (good holding). Enter at or near high "
                      "tide, and beware the shoal on the north side of the entrance. No permit for a stay under 24 hours."},
        ],
        "tips": ["You cross the Oakland ship channel area near the Bay Bridge. Look hard for ships turning toward Oakland.",
                 "Sheltered from the afternoon westerly, which makes it a good plan B when the Slot is too windy."],
    },
    {
        "id": "daysail-loop", "name": "The locals' Central Bay loop", "pop": 5, "level": "intermediate",
        "hours": "4–5 hrs", "kind": "Just go boating",
        "summary": "No destination, just the best of the Bay in the right order. Leave around 11 as the fog burns off, go up "
                   "the back side of Angel Island, through Raccoon Strait, along the Sausalito waterfront and Yellow Bluff, "
                   "then ride the afternoon breeze back along the city front.",
        "why": "This is the classic local daysail, the route Latitude 38 recommends instead of learning it by trial and error. "
               "It works with the Bay's daily rhythm: you go upwind while it's light and come home downwind when it's strong.",
        "when": "Late morning start. The breeze peaks around 2–3 pm. Check the current: Raccoon Strait is easier with the flood.",
        "route": r(OUT_NORTH, CITY_FRONT, LOOP_NORTH, [(37.858, -122.4745), (37.8625, -122.479), (37.869, -122.4835), (37.8625, -122.479)], SAUSALITO_TO_GATE, list(reversed(TO_GATE)), CITY_FRONT_BACK, IN_NORTH),
        "stops": [
            {"at": (37.8365, -122.4665), "name": "Yellow Bluff", "type": "view",
             "notes": "The wind gets fluky hugging the Sausalito shore. From here you can see straight out the Gate."},
            {"at": (37.8130, -122.4740), "name": "Fort Point (turnaround)", "type": "view",
             "notes": "Optional extension under the Golden Gate, only at slack or a moderate flood. On a small boat, don't get "
                      "caught on a strong ebb that carries you out to sea."},
        ],
        "tips": ["Go counterclockwise: upwind in the light morning air, downwind in the strong afternoon breeze.",
                 "Watch for gusts coming out of the lee of the islands and the headlands.",
                 "Want lunch? Stop at Ayala Cove or Sausalito along the way."],
    },
    {
        "id": "sunset-cityfront", "name": "After-work sunset run", "pop": 5, "level": "beginner+",
        "hours": "1.5–2 hrs", "kind": "Evening cruise",
        "summary": "Out the north door, up the Embarcadero past the Ferry Building, Pier 39 and Aquatic Park, and back as "
                   "the sun drops behind the Golden Gate. On summer Friday nights you'll share the city front with "
                   "beer-can racers.",
        "why": "Short enough for a weeknight, beautiful every single time, and never far from home. Friday-night beer-can "
               "racing is a decades-old Bay tradition, and the city front is where you see it.",
        "when": "Summer evenings. The wind usually eases toward sunset. Bring layers: it gets cold fast.",
        "route": r(OUT_NORTH, CITY_FRONT, [(37.8140, -122.4300)], CITY_FRONT_BACK, [(37.7840, -122.3790), (37.7805, -122.3812), (37.7781, -122.3830), (37.7776, -122.3858), (37.7772, -122.3870), (37.7770, -122.3885), (37.7772, -122.3870)], list(reversed(OUT_SOUTH))),
        "stops": [
            {"at": (37.8140, -122.4300), "name": "Off Aquatic Park (turnaround)", "type": "view",
             "notes": "Golden Gate sunset view. Aquatic Park itself is for swimmers; stay outside the breakwater."},
            {"at": (37.8080, -122.3965), "name": "City front piers", "type": "view",
             "notes": "Ferries come and go from the Ferry Building and Pier 41. Keep a sharp lookout."},
        ],
        "tips": ["Give racing sailboats room. They can't easily change course mid-race.",
                 "Coming home after dark? Practice it first. Red, right, returning works at night too: look for the lights."],
    },
    {
        "id": "angel-ayala", "name": "Angel Island picnic & hike", "pop": 4, "level": "intermediate",
        "hours": "5–6 hrs", "kind": "Dock & explore",
        "summary": "Tie up in Ayala Cove, then hike up Mt. Livermore or picnic in the park. Head home down the island's east "
                   "side with the afternoon breeze behind you.",
        "why": "Locals go back over and over: it's a state park you can only really get to by boat, with the Bay's biggest "
               "public docks, and it's well protected once you're in.",
        "when": "Go early: the docks fill up on summer weekends. Slips are open 8 am to sunset.",
        "route": r(OUT_NORTH, CITY_FRONT, [(37.8290, -122.4400), (37.8450, -122.4560)], RACCOON_W, RACCOON_E, AYALA,
                   [(37.8715, -122.4400)], ANGEL_EAST, HOME_FROM_NORTH, IN_NORTH),
        "stops": [
            {"at": (37.8700, -122.4362), "name": "Ayala Cove, Angel Island State Park", "type": "dock",
             "notes": "Day-use slips (fee, self-pay) and moorings. Café, picnic areas, trails. No one may stay on the island "
                      "after sunset."},
        ],
        "tips": ["Raccoon Strait has strong current. Time it with the tide.",
                 "China Cove, just east of Ayala, and Quarry Beach on the east side are quieter lunch anchors."],
    },
    {
        "id": "mccovey", "name": "Giants game in McCovey Cove", "pop": 4, "level": "beginner",
        "hours": "game length", "kind": "Event (all season)",
        "summary": "Out the south door of your harbor and into the cove behind right field. Float with the kayaks, listen to "
                   "the crowd, and wait for a splash hit.",
        "why": "It's two minutes from your slip, there are 81 home games a year, and it never gets old.",
        "when": "Home games. Boats may anchor up to 2 hours before first pitch and must leave soon after the game.",
        "route": r(OUT_SOUTH, [(37.7772, -122.3870), (37.7768, -122.3885)]),
        "stops": [
            {"at": (37.7768, -122.3885), "name": "McCovey Cove", "type": "anchor",
             "notes": "No-wake, minimum speed, no overnight anchoring. Packed with kayaks, so go dead slow."},
        ],
        "tips": ["Big fenders if you'll raft up, and a long-handled net for home-run balls.",
                 "Check the Port of SF's McCovey Cove rules before you go."],
    },
    {
        "id": "halibut-south", "name": "Halibut drift off Hunters Point", "pop": 4, "level": "beginner+",
        "hours": "3–5 hrs", "kind": "Fishing",
        "summary": "Cruise south along the quieter southern waterfront to the flats off Hunters Point and drift for halibut. "
                   "It's away from the ship lanes and the Slot, and it's the nearest good fishing ground to Pier 40.",
        "why": "Fishing is one of the main things locals do with small powerboats, and the east shore from Hunters Point "
               "south is a well-known halibut area. Every trip is different, and it teaches you to read current and depth.",
        "when": "Roughly April–October, best with live bait (May onward). Calmer in the morning.",
        "route": r(OUT_SOUTH, SOUTH_SHORE, [(37.7180, -122.3580)], list(reversed(SOUTH_SHORE)), list(reversed(OUT_SOUTH))),
        "stops": [
            {"at": (37.7330, -122.3540), "name": "Hunters Point flats", "type": "anchor",
             "notes": "Drift or troll slowly with live anchovies. California limit: 3 halibut, minimum 22 inches. You need a "
                      "fishing license."},
            {"at": (37.7180, -122.3580), "name": "Toward Candlestick", "type": "view",
             "notes": "The flats continue south along the shore. Shallow near the shore, so watch your depth."},
        ],
        "tips": ["Check the current: drifting works best on a moderate tide, not a rip.",
                 "Anchorage 8A (big ships waiting) is just offshore. Keep your distance."],
    },
    {
        "id": "sausalito", "name": "Lunch in Sausalito", "pop": 3, "level": "intermediate",
        "hours": "4–5 hrs", "kind": "Dock & dine",
        "summary": "Cross to Sausalito, tie up at a marina restaurant dock, and come back with the breeze behind you.",
        "why": "A reliable crowd-pleaser when you have guests, and it pairs naturally with the Central Bay loop.",
        "when": "Cross in the morning; the Slot builds by early afternoon.",
        "route": r(OUT_NORTH, CITY_FRONT, SLOT_TO_SAUSALITO, [(37.8580, -122.4745), (37.8625, -122.4790), (37.8655, -122.4880), (37.8652, -122.4925)],
                   [(37.8655, -122.4880), (37.8690, -122.4835), (37.8625, -122.4790), (37.8580, -122.4745)], [(37.8480, -122.4560), (37.8360, -122.4280)], HOME_FROM_NORTH[1:], IN_NORTH),
        "stops": [
            {"at": (37.8652, -122.4925), "name": "Sausalito marinas (guest docks)", "type": "dock",
             "notes": "Clipper Yacht Harbor's south dock (Fish Café) and Schoonmaker Point's north dock (Le Garage). Call ahead."},
        ],
        "tips": ["The Sausalito ferry runs the same path. Watch for it.", "Slow down inside Richardson Bay: there are no-wake zones."],
    },
    {
        "id": "tiburon-sams", "name": "Burgers at Sam's, Tiburon", "pop": 3, "level": "intermediate",
        "hours": "4–5 hrs", "kind": "Dock & dine",
        "summary": "Through Raccoon Strait to Sam's Anchor Cafe's guest dock: a perennial local boat-in favorite.",
        "why": "It's the Bay's classic boat-up deck lunch, and you get Raccoon Strait and Angel Island on the way.",
        "when": "Mid to high tide (it's shallow at the dock). Weekday lunches are easier.",
        "route": r(OUT_NORTH, CITY_FRONT, [(37.8290, -122.4400), (37.8450, -122.4560)], RACCOON_W, [(37.8665, -122.4545),
                   (37.8715, -122.4555)], [(37.8665, -122.4545)], RACCOON_E, ANGEL_EAST, HOME_FROM_NORTH, IN_NORTH),
        "stops": [
            {"at": (37.8715, -122.4555), "name": "Sam's Anchor Cafe, Tiburon", "type": "dock",
             "notes": "A guest dock, but shallow at low tide. Some charter fleets don't allow it for that reason."},
        ],
        "tips": ["Raccoon Strait current can be strong. Plan with the current tables."],
    },
    {
        "id": "jack-london", "name": "Windy-day estuary cruise", "pop": 3, "level": "intermediate",
        "hours": "4–5 hrs", "kind": "Flat water + dock & dine",
        "summary": "When the Central Bay is too rough, go east instead: cruise up the flat Oakland Estuary and tie up for free "
                   "at Jack London Square.",
        "why": "It's the locals' plan B. The estuary stays flat when it's blowing 25 knots in the Slot, and there's food at the end.",
        "when": "Any day, but especially windy summer afternoons.",
        "route": r(OUT_NORTH, [(37.7960, -122.3600), (37.8005, -122.3500), (37.7995, -122.3350), (37.7970, -122.3230),
                               (37.7950, -122.3170), (37.7935, -122.3110), (37.7925, -122.3000), (37.7925, -122.2880), (37.7938, -122.2790)],
                   [(37.7925, -122.2880), (37.7925, -122.3000), (37.7935, -122.3110), (37.7950, -122.3170), (37.7970, -122.3230),
                    (37.7995, -122.3350), (37.8005, -122.3500), (37.7960, -122.3600)], IN_NORTH),
        "stops": [
            {"at": (37.7938, -122.2790), "name": "Jack London Square guest docks", "type": "dock",
             "notes": "Free, first come, first served. Pasta Pelican and Quinn's Lighthouse give free tie-up when you eat there."},
        ],
        "tips": ["The way in follows the Oakland ship channel. Stay at the edge and watch for container ships.",
                 "Watch for the Oakland/Alameda ferries in the estuary."],
    },
    {
        "id": "richardson", "name": "Lazy afternoon in Richardson Bay", "pop": 3, "level": "intermediate",
        "hours": "4–6 hrs", "kind": "Anchor & hang out",
        "summary": "Cross to Sausalito and drop the hook in sheltered Richardson Bay, away from the Central Bay chop.",
        "why": "It's one of the local sailors' favorite anchorages, with calm water and a view of the houseboats and hills.",
        "when": "Cross in the morning; come home with the breeze behind you.",
        "route": r(OUT_NORTH, CITY_FRONT, SLOT_TO_SAUSALITO, SAUSALITO_FRONT, [(37.8650, -122.4800), (37.8690, -122.4835)],
                   [(37.8650, -122.4800)], SAUSALITO_FRONT, [(37.8480, -122.4560), (37.8360, -122.4280)], HOME_FROM_NORTH[1:], IN_NORTH),
        "stops": [
            {"at": (37.8715, -122.4840), "name": "Richardson Bay anchorage", "type": "anchor",
             "notes": "Stays up to 72 hours in the designated anchorage. There's no anchoring in the eelgrass zone, small-boat "
                      "channels, or the Audubon sanctuary, so check the RBRA map."},
        ],
        "tips": ["Shallow outside the channels. Watch your depth sounder."],
    },
]


# PLAN = the stops the boat actually makes, in order. Each point must lie on the route (checked below).
# kind: "dock" (tie up) or "chill" (engine off / anchor). ref: dock name or chill id in data/places.json.
PLAN = {
    "clipper-cove":     [("chill", "clipper", (37.8155, -122.3690), "Anchor and hang out")],
    "daysail-loop":     [("chill", "angel-east", (37.8590, -122.4100), "Break in the lee of the island"),
                         ("chill", "richardson", (37.8690, -122.4835), "Lunch at anchor")],
    "sunset-cityfront": [("chill", "mccovey", (37.7770, -122.3885), "Float after sunset, then home")],
    "angel-ayala":      [("dock", "Ayala Cove docks", (37.8700, -122.4362), "Tie up: bathrooms, picnic, hike"),
                         ("chill", "angel-east", (37.8590, -122.4100), "Engine off, drift in the sun")],
    "mccovey":          [("chill", "mccovey", (37.7768, -122.3885), "Anchor for the game")],
    "halibut-south":    [("chill", "hunters-flats", (37.7330, -122.3540), "Drift and fish")],
    "sausalito":        [("dock", "Le Garage", (37.8652, -122.4925), "Tie up for lunch (Schoonmaker Point north dock)"),
                         ("chill", "richardson", (37.8690, -122.4835), "Float a while before heading home")],
    "tiburon-sams":     [("dock", "Sam's Anchor Cafe", (37.8715, -122.4555), "Tie up for lunch"),
                         ("chill", "angel-east", (37.8590, -122.4100), "Engine off on the way home")],
    "jack-london":      [("dock", "Jack London Square guest docks", (37.7938, -122.2790), "Tie up and eat")],
    "richardson":       [("chill", "richardson", (37.8690, -122.4835), "Anchor for the afternoon")],
}
# Other good spots near each trip that the boat does NOT stop at (shown as detour options).
OPTIONS = {
    "clipper-cove":     (["mccovey"], ["Treasure Isle Marina"]),
    "daysail-loop":     (["belvedere", "ayala"], ["Ayala Cove docks", "Sam's Anchor Cafe", "Horizons", "Sausalito Yacht Harbor"]),
    "sunset-cityfront": (["aquatic"], ["Pier 39 Marina"]),
    "angel-ayala":      (["ayala"], []),
    "mccovey":          ([], ["The Ramp"]),
    "halibut-south":    ([], ["The Ramp"]),
    "sausalito":        (["belvedere"], ["Fish", "Clipper Yacht Harbor", "Schoonmaker Point Marina", "Horizons", "Sausalito Yacht Harbor"]),
    "tiburon-sams":     (["belvedere", "ayala"], ["Ayala Cove docks"]),
    "jack-london":      ([], ["Pasta Pelican"]),
    "richardson":       (["belvedere"], ["Sausalito Yacht Harbor", "Horizons", "Schoonmaker Point Marina"]),
}
NO_CHILL = {
    "jack-london": "The estuary is flat, but it's a busy channel with ferries and occasional ships, so don't drift there. "
                   "The chill on this trip is tying up at Jack London Square.",
}
PLACES = json.load(open(os.path.join(HERE, "data", "places.json")))
_chill_ids = {c["id"] for c in PLACES["chill"]}
_dock_names = {d["name"] for d in PLACES["docks"]}
for t in TRIPS:
    line = LineString([(lo, la) for la, lo in t["route"]])
    t["plan"] = []
    for kind, ref, at, what in PLAN[t["id"]]:
        assert ref in (_chill_ids if kind == "chill" else _dock_names), (t["id"], ref)
        off_m = line.distance(Point(at[1], at[0])) * 111000
        assert off_m < 40, f"{t['id']}: plan stop {ref} is {off_m:.0f} m off the route"
        t["plan"].append({"kind": kind, "ref": ref, "at": list(at), "what": what})
    oc, od = OPTIONS[t["id"]]
    assert set(oc) <= _chill_ids and set(od) <= _dock_names, t["id"]
    t["opt_chill"], t["opt_dock"] = oc, od
    if t["id"] in NO_CHILL:
        t["no_chill"] = NO_CHILL[t["id"]]


def nm(a, b):
    la = math.radians((a[0] + b[0]) / 2)
    return math.hypot((a[0] - b[0]) * 60, (a[1] - b[1]) * 60 * math.cos(la))


def check(trip):
    bad = []
    pts = trip["route"]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        seg = LineString([(a[1], a[0]), (b[1], b[0])])
        hit = seg.intersection(LAND)
        if not hit.is_empty and hit.length > 0.00015:   # > ~15 m of land
            bad.append((i, a, b, round(hit.length * 111000)))
    for i, p in enumerate(pts):
        if LAND.contains(Point(p[1], p[0])):
            bad.append(("point", i, p))
    return bad


ok = True
out = []
for t in TRIPS:
    issues = check(t)
    dist = sum(nm(t["route"][i], t["route"][i + 1]) for i in range(len(t["route"]) - 1))
    print(f"{t['id']:14s} {dist:5.1f} nm  {'OK' if not issues else 'LAND: ' + str(issues)}")
    ok &= not issues
    out.append({**t, "nm": round(dist, 1),
                "route": [[la, lo] for la, lo in t["route"]],
                "stops": [{**s, "at": list(s["at"])} for s in t["stops"] if s["type"] == "view"]})

json.dump(out, open(os.path.join(HERE, "data", "trips.json"), "w"), indent=0)
if not ok:
    sys.exit(1)
