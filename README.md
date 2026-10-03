# SF Boat

A beginner's guide to boating on San Francisco Bay, starting from Pier 40 (South Beach Harbor).

- **Learn**: a guided course on the real water around Pier 40: harbor entrances, big ships and ferries, current, hazards, rules of the road.
- **Explore**: NOAA chart features (ship lanes, channels, buoys, rocks), predicted tidal currents, ferry routes, calm/rough water, and a route checker.
- **Trips**: outings locals do again and again, plus a map of docks and chill spots.
- `boating.py`: a Manim explainer video on the rules of the road.

Not for navigation. Always use official charts and your own judgment.

## Run locally

```sh
uv venv .venv && uv pip install --python .venv/bin/python websockets shapely
.venv/bin/python map/server.py      # http://localhost:8040
```

Live ship positions (AIS) only work locally: put `AISSTREAM_API_KEY=...` in `.env` (free key from aisstream.io).

## Data

- `map/fetch_data.py`: NOAA ENC chart features → `map/data/enc.json`
- `map/build_extra.py`: OpenStreetMap ferry routes + hand-drawn calm/rough zones
- `map/build_trips.py`: trips, with every leg checked against NOAA charted land
