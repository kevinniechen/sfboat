"""Local server for the SF Bay map.

    .venv/bin/python map/server.py      ->  http://localhost:8040

Serves the static map and, if AISSTREAM_API_KEY is set (env or ../.env),
relays live AIS ship positions from aisstream.io at /api/ships.
"""
import asyncio, json, os, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 8040))
BBOX = [[37.55, -122.80], [38.12, -122.15]]  # [[lat, lon], [lat, lon]]
STALE_S = 20 * 60


def load_key():
    key = os.environ.get("AISSTREAM_API_KEY")
    env = os.path.join(HERE, "..", ".env")
    if not key and os.path.exists(env):
        for line in open(env):
            if line.startswith("AISSTREAM_API_KEY="):
                key = line.split("=", 1)[1].strip()
    return key


ships = {}            # mmsi -> dict
lock = threading.Lock()
status = {"ais": "disabled", "error": None, "messages": 0, "since": None}


def upsert(mmsi, **kw):
    with lock:
        s = ships.setdefault(mmsi, {"mmsi": mmsi})
        s.update({k: v for k, v in kw.items() if v not in (None, "")})


def handle(msg):
    mtype = msg.get("MessageType")
    meta = msg.get("MetaData", {})
    mmsi = meta.get("MMSI")
    if not mmsi:
        return
    body = msg.get("Message", {}).get(mtype, {})
    name = (meta.get("ShipName") or "").strip() or None
    if mtype in ("PositionReport", "StandardClassBPositionReport", "ExtendedClassBPositionReport"):
        hdg = body.get("TrueHeading")
        upsert(mmsi, name=name, lat=meta.get("latitude"), lon=meta.get("longitude"),
               sog=body.get("Sog"), cog=body.get("Cog"),
               hdg=hdg if hdg is not None and hdg < 360 else None,
               nav=body.get("NavigationalStatus"),
               cls="A" if mtype == "PositionReport" else "B", t=time.time())
        if mtype == "ExtendedClassBPositionReport":
            d = body.get("Dimension") or {}
            upsert(mmsi, type=body.get("Type"), length=(d.get("A", 0) + d.get("B", 0)) or None)
    elif mtype == "ShipStaticData":
        d = body.get("Dimension") or {}
        upsert(mmsi, name=(body.get("Name") or "").strip() or name, type=body.get("Type"),
               length=(d.get("A", 0) + d.get("B", 0)) or None,
               dest=(body.get("Destination") or "").strip() or None)
    elif mtype == "StaticDataReport":
        a, b = body.get("ReportA") or {}, body.get("ReportB") or {}
        d = b.get("Dimension") or {}
        upsert(mmsi, name=(a.get("Name") or "").strip() or name,
               type=b.get("ShipType") or None,
               length=(d.get("A", 0) + d.get("B", 0)) or None)


async def ais_loop(key):
    import websockets
    sub = {"APIKey": key, "BoundingBoxes": [BBOX],
           "FilterMessageTypes": ["PositionReport", "StandardClassBPositionReport",
                                  "ExtendedClassBPositionReport", "ShipStaticData",
                                  "StaticDataReport"]}
    while True:
        try:
            async with websockets.connect("wss://stream.aisstream.io/v0/stream",
                                          ping_interval=20) as ws:
                await ws.send(json.dumps(sub))
                status.update(ais="connected", error=None, since=time.time())
                async for raw in ws:
                    msg = json.loads(raw)
                    if "error" in msg:
                        status.update(ais="error", error=msg["error"])
                        break
                    status["messages"] += 1
                    handle(msg)
        except Exception as e:
            status.update(ais="reconnecting", error=str(e)[:200])
        await asyncio.sleep(5)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, *a):
        pass

    def _json(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/ships"):
            now = time.time()
            with lock:
                for k in [k for k, s in ships.items() if now - s.get("t", 0) > STALE_S]:
                    del ships[k]
                out = [dict(s, age=round(now - s["t"])) for s in ships.values()
                       if "lat" in s and "t" in s]
            return self._json({"status": status, "ships": out})
        if self.path.startswith("/api/status"):
            return self._json(status)
        return super().do_GET()


def main():
    key = load_key()
    if key:
        status["ais"] = "connecting"
        threading.Thread(target=lambda: asyncio.run(ais_loop(key)), daemon=True).start()
    else:
        print("No AISSTREAM_API_KEY: live ships disabled (map still works).")
    print(f"SF Bay map: http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
