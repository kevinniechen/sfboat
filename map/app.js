/* SF Bay Navigator: NOAA chart features + predicted currents + live AIS + route check. */
'use strict';

const PIER40 = [37.7814, -122.3867];
const BOUNDS = { s: 37.58, n: 38.10, w: -122.75, e: -122.18 };
const TZ = 'America/Los_Angeles';
const COL = { lane: '#e040c8', prec: '#f5c542', dredge: '#7aa0dc', fair: '#b58cff',
              red: '#ff4d4d', green: '#2fcf6f', rock: '#ff9f6b' };

// ------------------------------------------------------------------ map
const map = L.map('map', { preferCanvas: true, zoomControl: false, doubleClickZoom: true })
  .setView([37.805, -122.41], 13);
L.control.zoom({ position: 'topright' }).addTo(map);
L.control.scale({ position: 'bottomright', metric: false }).addTo(map);

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Esri, HERE, Garmin, © OpenStreetMap · NOAA', maxZoom: 19, maxNativeZoom: 16,
}).addTo(map);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 19, maxNativeZoom: 16, pane: 'shadowPane', opacity: 0.8,
}).addTo(map);
const chartLayer = L.tileLayer.wms(
  'https://gis.charttools.noaa.gov/arcgis/rest/services/MCS/NOAAChartDisplay/MapServer/exts/MaritimeChartService/WMSServer',
  { layers: '0,1,2,3,4,5,6,7', format: 'image/png', transparent: true, version: '1.3.0',
    opacity: 0.92, maxZoom: 19, attribution: 'NOAA ENC' });

for (const [name, z] of [['areas', 405], ['lanesP', 410], ['hazP', 430], ['routeP', 600],
                         ['buoyP', 620], ['curP', 640], ['shipP', 660]]) {
  map.createPane(name).style.zIndex = z;
}
const canvasHaz = L.canvas({ pane: 'hazP' });

const groups = {
  chart: L.layerGroup([chartLayer]),
  lanes: L.layerGroup(), channels: L.layerGroup(), buoys: L.layerGroup(), ferries: L.layerGroup(), zones: L.layerGroup(),
  hazards: L.layerGroup(), areas: L.layerGroup(), currents: L.layerGroup(), ships: L.layerGroup(),
};
const hazardsDetail = L.layerGroup();   // obstructions: only when zoomed in

function syncLayers() {
  document.querySelectorAll('[data-layer]').forEach(cb => {
    const g = groups[cb.dataset.layer];
    if (cb.checked) map.addLayer(g); else map.removeLayer(g);
  });
  const showDetail = document.querySelector('[data-layer=hazards]').checked && map.getZoom() >= 14;
  if (showDetail) map.addLayer(hazardsDetail); else map.removeLayer(hazardsDetail);
  map.getContainer().classList.toggle('z14', map.getZoom() >= 14);
  map.getContainer().classList.toggle('z13', map.getZoom() >= 13);
}
document.querySelectorAll('[data-layer]').forEach(cb => cb.addEventListener('change', syncLayers));
map.on('zoomend', syncLayers);

// ------------------------------------------------------------------ helpers
const deg = r => r * 180 / Math.PI, rad = d => d * Math.PI / 180;
const norm360 = a => ((a % 360) + 360) % 360;
const COMPASS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
const compass = a => COMPASS[Math.round(norm360(a) / 22.5) % 16];
const fmtDeg = a => `${String(Math.round(norm360(a))).padStart(3, '0')}° (${compass(a)})`;
const fmtTime = t => new Date(t).toLocaleString('en-US', { timeZone: TZ, weekday: 'short', hour: 'numeric', minute: '2-digit' });
const fmtClock = t => new Date(t).toLocaleTimeString('en-US', { timeZone: TZ, hour: 'numeric', minute: '2-digit' });
const mToFt = m => Math.round(m * 3.28084);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function speedColor(s) {
  const stops = [[0, '#6b7c8f'], [0.5, '#2ec4b6'], [1.5, '#9be15d'], [2.5, '#f5c542'], [3.5, '#ff8a3d'], [4.5, '#ff4d4d']];
  let c = stops[0][1];
  for (const [v, col] of stops) if (s >= v) c = col;
  return c;
}

// ------------------------------------------------------------------ time
const slider = document.getElementById('time');
let baseNow = Date.now();
const selTime = () => baseNow + (+slider.value) * 60000;
let playTimer = null;
function onTime() {
  const t = selTime();
  const rel = +slider.value;
  const relTxt = rel === 0 ? 'now' : `${rel > 0 ? '+' : '−'}${Math.floor(Math.abs(rel) / 60)}h${String(Math.abs(rel) % 60).padStart(2, '0')}`;
  document.getElementById('timeLabel').textContent = `${fmtTime(t)}  ·  ${relTxt}`;
  renderCurrents();
  renderGate();
  if (route.pts.length > 1) analyzeRoute();
}
slider.addEventListener('input', onTime);
document.getElementById('now').onclick = () => { baseNow = Date.now(); slider.value = 0; onTime(); };
document.getElementById('play').onclick = e => {
  if (playTimer) { clearInterval(playTimer); playTimer = null; e.target.textContent = '▶ Play'; e.target.classList.remove('on'); return; }
  e.target.textContent = '❚❚ Pause'; e.target.classList.add('on');
  playTimer = setInterval(() => {
    let v = +slider.value + 10;
    if (v > +slider.max) v = +slider.min;
    slider.value = v; onTime();
  }, 120);
};

// ------------------------------------------------------------------ chart features
let ENC = null;

function polyArrows(feature, orient, twoWay, color, placed) {
  const out = [];
  let c;
  try { c = turf.centroid(feature); } catch { return out; }
  for (let k = -12; k <= 12; k++) {
    const p = k === 0 ? c : turf.destination(c, k * 1.1, orient, { units: 'kilometers' });
    if (!turf.booleanPointInPolygon(p, feature)) continue;
    const [lon, lat] = p.geometry.coordinates;
    if (placed.some(q => Math.abs(q.o - orient) < 25 && turf.distance(q.p, p) < 0.7)) continue;
    placed.push({ p, o: orient });
    const path = twoWay
      ? 'M0,-14 L6,-6 L2.2,-6 L2.2,6 L6,6 L0,14 L-6,6 L-2.2,6 L-2.2,-6 L-6,-6Z'
      : 'M0,-14 L7,-3 L2.5,-3 L2.5,12 L-2.5,12 L-2.5,-3 L-7,-3Z';
    out.push(L.marker([lat, lon], {
      pane: 'lanesP', interactive: false,
      icon: L.divIcon({ className: 'lane-ico', iconSize: [32, 32], iconAnchor: [16, 16],
        html: `<svg width="32" height="32" viewBox="-16 -16 32 32" style="transform:rotate(${orient}deg)">
                 <path d="${path}" fill="${color}" stroke="#fff" stroke-width="1.2" opacity=".95"/></svg>` }),
    }));
  }
  return out;
}

function buildLanes() {
  const placed = [];
  const lanePopup = p => `<b>${esc(p.INFORM || 'Traffic lane')}</b><br>
    Ships travel toward <b>${fmtDeg(p.ORIENT)}</b>.<br>
    <span class="warn">Don't impede ships here. Stay out, or cross quickly at a right angle, behind them.</span>`;
  L.geoJSON(ENC.lanes, {
    pane: 'lanesP',
    style: { color: COL.lane, weight: 1.2, fillColor: COL.lane, fillOpacity: 0.17 },
    onEachFeature: (f, l) => l.bindPopup(lanePopup(f.properties)),
  }).addTo(groups.lanes);
  for (const f of ENC.lanes.features) {
    if (f.properties.ORIENT == null) continue;
    polyArrows(f, f.properties.ORIENT, false, COL.lane, placed).forEach(m => m.addTo(groups.lanes));
  }
  L.geoJSON(ENC.sepzones, {
    pane: 'lanesP', style: { stroke: false, fillColor: COL.lane, fillOpacity: 0.38 },
    onEachFeature: (f, l) => l.bindPopup('<b>Separation zone</b><br>Divides opposing ship lanes. Keep out.'),
  }).addTo(groups.lanes);
  L.geoJSON(ENC.deepwater, {
    pane: 'lanesP', style: { color: '#6fb8ff', weight: 1.2, dashArray: '6 4', fillColor: '#6fb8ff', fillOpacity: 0.12 },
    onEachFeature: (f, l) => l.bindPopup(`<b>${esc(f.properties.INFORM || 'Deep-water route')}</b><br>
      Two-way route for deep-draft ships, oriented ${fmtDeg(f.properties.ORIENT || 0)}.<br>
      <span class="warn">Big ships can't leave it. Keep clear.</span>`),
  }).addTo(groups.lanes);
  for (const f of ENC.deepwater.features) {
    if (f.properties.ORIENT == null) continue;
    polyArrows(f, f.properties.ORIENT, true, '#6fb8ff', placed).forEach(m => m.addTo(groups.lanes));
  }
  L.geoJSON(ENC.precaution, {
    pane: 'lanesP', style: { color: COL.prec, weight: 1.6, dashArray: '8 6', fillColor: COL.prec, fillOpacity: 0.05 },
    onEachFeature: (f, l) => l.bindPopup(`<b>Precautionary area</b> ${esc(f.properties.INFORM || '')}<br>
      Ships converge, turn, and pick up pilots here. Navigate with extra caution.`),
  }).addTo(groups.lanes);
}

function buildChannels() {
  L.geoJSON(ENC.dredged, {
    pane: 'areas', style: { color: COL.dredge, weight: 0.8, fillColor: COL.dredge, fillOpacity: 0.16 },
    onEachFeature: (f, l) => {
      const p = f.properties;
      l.bindPopup(`<b>${esc(p.OBJNAM || 'Dredged channel')}</b><br>
        ${p.DRVAL1 != null ? `Maintained depth ≈ <b>${mToFt(p.DRVAL1)} ft</b><br>` : ''}
        Deep water kept open for big ships. Ships here can't maneuver outside it,
        so you must not impede them (Rule 9).`);
    },
  }).addTo(groups.channels);
  L.geoJSON(ENC.fairways, {
    pane: 'areas', style: { color: COL.fair, weight: 1.2, dashArray: '3 5', fill: true, fillOpacity: 0.03 },
    onEachFeature: (f, l) => l.bindPopup(`<b>${esc(f.properties.OBJNAM || 'Fairway')}</b><br>
      Charted fairway (channel). ${f.properties.TRAFIC === 4 ? 'Two-way traffic. ' : ''}
      Keep to the starboard (right) side of it, and expect ships.`),
  }).addTo(groups.channels);
}

function buildAreas() {
  L.geoJSON(ENC.restricted, {
    pane: 'areas', style: { color: '#ff7b7b', weight: 1, dashArray: '2 4', fillColor: '#ff7b7b', fillOpacity: 0.06 },
    onEachFeature: (f, l) => l.bindPopup(`<b>Restricted area</b><br>${esc(f.properties.OBJNAM || '')}
      ${esc(f.properties.INFORM || f.properties.NINFOM || '')}<br><span class="muted">Check the chart notes for what's restricted.</span>`),
  }).addTo(groups.areas);
  L.geoJSON(ENC.anchorage, {
    pane: 'areas', style: { color: '#c9a7ff', weight: 1, dashArray: '6 3', fillOpacity: 0.04 },
    onEachFeature: (f, l) => l.bindPopup(`<b>Anchorage</b> ${esc(f.properties.OBJNAM || '')}<br>
      Big ships may be anchored here and can swing with the current. Don't pass close downstream of them.`),
  }).addTo(groups.areas);
}

// ---- buoys
const S57COL = { 1: 'white', 2: 'black', 3: 'red', 4: 'green', 6: 'yellow', 11: 'orange' };
const HEX = { white: '#f4f4f4', black: '#222', red: COL.red, green: COL.green, yellow: '#f5c542', orange: '#ff9f43' };

function markInfo(p) {
  const cols = String(p.COLOUR || '').split(',').map(c => S57COL[+c]).filter(Boolean);
  const objl = p.OBJL;
  const isBeacon = [5, 7, 8, 9, 10].includes(objl);
  const kind = { 17: 'lateral', 7: 'lateral', 18: 'safe', 9: 'safe', 16: 'danger', 8: 'danger',
                 19: 'special', 10: 'special', 14: 'cardinal', 5: 'cardinal' }[objl] || 'other';
  const num = (String(p.OBJNAM || '').match(/(?:Buoy|Beacon|Daybeacon|Light)\s+"?([0-9A-Z]{1,4})"?\s*$/i) || [])[1] || '';
  let rule = '', shape = 'circle', fill = HEX[cols[0]] || '#ccc', band = cols[1] ? HEX[cols[1]] : null;
  if (kind === 'lateral') {
    const top = cols[0];
    if (top === 'red') { shape = 'tri'; rule = cols.length > 1
      ? 'Preferred-channel mark (red on top): the main channel is the one where you keep this on your <b>right</b> when returning.'
      : 'Keep this on your <b>RIGHT</b> when returning (coming in from sea or heading upstream). Keep it on your left when heading out.'; }
    else if (top === 'green') { shape = 'sq'; rule = cols.length > 1
      ? 'Preferred-channel mark (green on top): the main channel is the one where you keep this on your <b>left</b> when returning.'
      : 'Keep this on your <b>LEFT</b> when returning (coming in from sea or heading upstream). Keep it on your right when heading out.'; }
  } else if (kind === 'safe') {
    rule = 'Safe-water mark: deep water all around. Often marks a channel entrance or midline. Pass on either side.';
    fill = COL.red; band = '#fff';
  } else if (kind === 'danger') {
    rule = 'Isolated danger: a hazard right at this mark, with navigable water around it. Give it room.';
    fill = '#222'; band = COL.red;
  } else if (kind === 'special') {
    rule = 'Special-purpose mark (yellow). Marks a special area or feature; check the chart.'; shape = 'diamond';
  }
  return { cols, kind, num, rule, shape, fill, band, isBeacon };
}

function markIcon(m) {
  const s = m.isBeacon ? 12 : 16;
  let g;
  const st = `stroke="#0b121b" stroke-width="1.4"`;
  if (m.shape === 'tri') g = `<path d="M8,1 L15,15 L1,15Z" fill="${m.fill}" ${st}/>` +
    (m.band ? `<path d="M5.2,8.7 L10.8,8.7 L12.3,11.7 L3.7,11.7Z" fill="${m.band}"/>` : '');
  else if (m.shape === 'sq') g = `<rect x="2" y="2" width="12" height="12" fill="${m.fill}" ${st}/>` +
    (m.band ? `<rect x="2.7" y="6.5" width="10.6" height="3" fill="${m.band}"/>` : '');
  else if (m.shape === 'diamond') g = `<path d="M8,1 L15,8 L8,15 L1,8Z" fill="${m.fill}" ${st}/>`;
  else g = `<circle cx="8" cy="8" r="6.5" fill="${m.fill}" ${st}/>` +
    (m.band ? `<rect x="6.5" y="1.8" width="3" height="12.4" fill="${m.band}"/>` : '');
  const ring = m.isBeacon ? '' : '';
  return L.divIcon({
    className: 'buoy-ico', iconSize: [s + 30, s], iconAnchor: [s / 2, s / 2],
    html: `<div style="display:flex;align-items:center;gap:2px">
      <svg width="${s}" height="${s}" viewBox="0 0 16 16">${g}${ring}</svg>
      ${m.num ? `<span class="lbl num">${esc(m.num)}</span>` : ''}</div>`,
  });
}

function buildBuoys() {
  for (const grp of ['buoys', 'beacons']) {
    for (const f of ENC[grp].features) {
      const p = f.properties, [lon, lat] = f.geometry.coordinates;
      const m = markInfo(p);
      const typ = (m.isBeacon ? 'Fixed beacon / daymark' : 'Buoy') +
        (m.cols.length ? ` · ${m.cols.join('/')}` : '') + (p.BOYSHP ? ` · ${p.BOYSHP}` : '');
      L.marker([lat, lon], { pane: 'buoyP', icon: markIcon(m) })
        .bindPopup(`<b>${esc(p.OBJNAM || 'Navigation mark')}</b><br><span class="muted">${esc(typ)}</span>
          ${m.rule ? `<br>${m.rule}` : ''}`)
        .addTo(groups.buoys);
    }
  }
}

// ---- hazards
const WATLEV = { 1: 'partly submerged at high water', 2: 'always dry', 3: 'always underwater',
                 4: 'covers and uncovers with the tide', 5: 'awash', 7: 'floating' };
let HAZ = [];
function buildHazards() {
  const add = (fc, label, group, color, r) => {
    for (const f of fc.features) {
      if (f.geometry.type !== 'Point') continue;
      const p = f.properties, [lon, lat] = f.geometry.coordinates;
      const depth = p.VALSOU != null ? ` · ${mToFt(p.VALSOU)} ft below chart datum` : '';
      const desc = `<b>${esc(p.OBJNAM || label)}</b><br>${esc(WATLEV[p.WATLEV] || '')}${depth}`;
      L.circleMarker([lat, lon], { renderer: canvasHaz, radius: r, color, weight: 1.5, fillColor: color, fillOpacity: 0.7 })
        .bindPopup(desc).addTo(group);
      HAZ.push({ pt: turf.point([lon, lat]), label: p.OBJNAM || label, depth: p.VALSOU, watlev: p.WATLEV });
    }
  };
  add(ENC.rocks, 'Rock', groups.hazards, COL.rock, 3.2);
  add(ENC.wrecks, 'Wreck', groups.hazards, '#ffd166', 3);
  add(ENC.obstructions, 'Obstruction', hazardsDetail, '#c7a37a', 2.2);
}

const ZONE_STYLE = {
  rough:    { color: '#ff5a5a', fill: 0.16, label: 'Often rough' },
  moderate: { color: '#f5c542', fill: 0.10, label: 'Moderate' },
  calm:     { color: '#2fcf6f', fill: 0.16, label: 'Usually calm / sheltered' },
};
function buildZones(fc) {
  for (const f of fc.features) {
    const p = f.properties, z = ZONE_STYLE[p.kind];
    const style = { pane: 'areas', color: z.color, weight: 1.5, dashArray: '2 6', fillColor: z.color, fillOpacity: z.fill };
    const lyr = f.geometry.type === 'Point'
      ? L.circle([f.geometry.coordinates[1], f.geometry.coordinates[0]], { ...style, radius: p.r })
      : L.geoJSON(f, { style: () => style });
    lyr.bindPopup(`<b style="color:${z.color}">${z.label}:</b> <b>${esc(p.name)}</b><br>${esc(p.desc)}
      <div class="muted small" style="margin-top:4px">Approximate, based on typical conditions. Any day can be different.</div>`);
    lyr.bindTooltip(p.name, { permanent: true, direction: 'center', className: 'zone-lbl', opacity: 0.9 });
    lyr.addTo(groups.zones);
  }
}
function buildFerries(fc) {
  window.FERRIES = fc;
  for (const f of fc.features) {
    const p = f.properties;
    const seasonal = /seasonal/i.test(p.name || '');
    L.geoJSON(f, { pane: 'lanesP', style: { color: '#4fa3ff', weight: seasonal ? 2 : 3, opacity: 0.85,
                                            dashArray: seasonal ? '6 6' : null } })
      .bindPopup(`<b>Ferry: ${esc(p.name)}</b><br><span class="muted">${esc(p.operator || '')}</span><br>
        Ferries run at <b>25–35 knots</b> and don't stay in the ship lanes. Look for them often, and never cross
        close in front of one.${seasonal ? '<br><i>Seasonal / event-day route.</i>' : ''}`)
      .addTo(groups.ferries);
  }
}

function buildPier40() {
  L.circleMarker(PIER40, { pane: 'buoyP', radius: 7, color: '#fff', weight: 2, fillColor: '#4fa3ff', fillOpacity: 1 })
    .bindTooltip('Pier 40', { permanent: true, direction: 'right', className: 'lbl', offset: [8, 0] })
    .bindPopup(`<b>Pier 40 (South Beach)</b><br>Leaving here you're in open water, not a marked channel,
      so there's no red/green to follow. Look at the map before you go:<br>
      • Where are the nearest <span style="color:${COL.lane}">ship lanes</span> and dredged channels on your route?<br>
      • Which way is the current running at the time you'll be out?<br>
      • Watch for ferries and ships near the Bay Bridge and the city waterfront.<br>
      Use <b>Plan a route</b> to check your trip.`)
    .addTo(map);
}

// ------------------------------------------------------------------ currents
const CUR = { stations: [], markers: new Map() };
const API = 'https://api.tidesandcurrents.noaa.gov';

function ymd(d) { return d.toISOString().slice(0, 10).replace(/-/g, ''); }
const parseGmt = s => Date.parse(s.replace(' ', 'T') + 'Z');

async function fetchJson(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(r.status);
  return r.json();
}
function cacheGet(k) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch { return null; } }
function cacheSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* full or blocked */ } }

async function loadStation(st, begin) {
  const key = `cur2:${st.id}:${begin}`;
  const hit = cacheGet(key);
  if (hit) return hit;
  let data;
  if (st.type === 'H') {
    const j = await fetchJson(`${API}/api/prod/datagetter?product=currents_predictions&station=${st.id}` +
      `&begin_date=${begin}&range=96&interval=30&units=english&time_zone=gmt&format=json&vel_type=speed_dir&application=sfbaynav`);
    const cp = j.current_predictions?.cp || [];
    data = { kind: 'H', series: cp.map(r => [parseGmt(r.Time), +r.Speed, +r.Direction]) };
  } else {
    const j = await fetchJson(`${API}/api/prod/datagetter?product=currents_predictions&station=${st.id}` +
      `&bin=${st.bin}&begin_date=${begin}&range=96&interval=MAX_SLACK&units=english&time_zone=gmt&format=json&application=sfbaynav`);
    const cp = j.current_predictions?.cp || [];
    data = { kind: 'S', events: cp.map(r => [parseGmt(r.Time), +r.Velocity_Major, r.Type]),
             flood: cp[0]?.meanFloodDir, ebb: cp[0]?.meanEbbDir };
  }
  if ((data.series?.length || data.events?.length)) cacheSet(key, data);
  return data;
}

// current at time t -> {spd, dir, signed?}
function currentAt(st, t) {
  const d = st.data;
  if (!d) return null;
  if (d.kind === 'H') {
    const s = d.series;
    if (!s.length || t < s[0][0] || t > s[s.length - 1][0]) return null;
    let i = Math.min(s.length - 2, Math.max(0, Math.floor((t - s[0][0]) / 1800000)));
    while (i > 0 && s[i][0] > t) i--;
    while (i < s.length - 2 && s[i + 1][0] < t) i++;
    const [t0, v0, d0] = s[i], [t1, v1, d1] = s[i + 1];
    const f = Math.min(1, Math.max(0, (t - t0) / (t1 - t0)));
    const u = v0 * Math.sin(rad(d0)) * (1 - f) + v1 * Math.sin(rad(d1)) * f;
    const w = v0 * Math.cos(rad(d0)) * (1 - f) + v1 * Math.cos(rad(d1)) * f;
    return { spd: Math.hypot(u, w), dir: norm360(deg(Math.atan2(u, w))) };
  }
  const e = d.events;
  if (e.length < 2 || t < e[0][0] || t > e[e.length - 1][0]) return null;
  let i = 0;
  while (i < e.length - 2 && e[i + 1][0] <= t) i++;
  const [t0, v0] = e[i], [t1, v1] = e[i + 1];
  const f = (t - t0) / (t1 - t0);
  const v = v0 + (v1 - v0) * (1 - Math.cos(Math.PI * f)) / 2;
  return { spd: Math.abs(v), dir: v >= 0 ? d.flood : d.ebb, phase: Math.abs(v) < 0.2 ? 'slack' : v > 0 ? 'flood' : 'ebb' };
}

// upcoming slack / max events after t
function eventsAfter(st, t, n = 4) {
  const d = st.data;
  if (!d) return [];
  if (d.kind === 'S') return d.events.filter(e => e[0] > t).slice(0, n)
    .map(([tt, v, ty]) => ({ t: tt, type: ty, spd: Math.abs(v) }));
  const s = d.series, out = [];
  for (let i = 1; i < s.length - 1 && out.length < n; i++) {
    if (s[i][0] <= t) continue;
    if (s[i][1] <= s[i - 1][1] && s[i][1] < s[i + 1][1] && s[i][1] < 0.6) out.push({ t: s[i][0], type: 'slack', spd: s[i][1] });
    else if (s[i][1] >= s[i - 1][1] && s[i][1] > s[i + 1][1] && s[i][1] > 0.3) out.push({ t: s[i][0], type: 'max', spd: s[i][1], dir: s[i][2] });
  }
  return out;
}

function curIcon() {
  return L.divIcon({
    className: 'cur-ico', iconSize: [44, 44], iconAnchor: [22, 22],
    html: `<div style="position:relative;width:44px;height:44px">
      <svg class="ca" width="44" height="44" viewBox="-22 -22 44 44" style="transition:transform .15s">
        <path d="M0,-19 L6,-8 L2,-8 L2,15 L-2,15 L-2,-8 L-6,-8Z" stroke="#0b121b" stroke-width="1"/>
      </svg>
      <span class="lbl cs" style="position:absolute;left:30px;top:14px;font-size:10px"></span></div>`,
  });
}

function stationPopup(st) {
  const t = selTime(), c = currentAt(st, t);
  const now = c ? `<b>${c.spd.toFixed(1)} kn</b> flowing toward ${fmtDeg(c.dir)}${c.phase ? ` · ${c.phase}` : ''}` : 'no prediction for this time';
  const ev = eventsAfter(st, t).map(e => `<li>${fmtClock(e.t)}: ${e.type === 'slack' ? 'slack' :
      `${e.type === 'max' ? 'max' : 'max ' + e.type} ${e.spd.toFixed(1)} kn`}</li>`).join('');
  return `<b>${esc(st.name)}</b><br>${now}<br><span class="muted small">NOAA ${st.type === 'H' ? 'harmonic' : 'subordinate'} station ${st.id}, predicted</span>
    ${ev ? `<div style="margin-top:6px">Next:</div><ul style="margin:2px 0;padding-left:18px">${ev}</ul>` : ''}`;
}

async function loadCurrents() {
  const status = document.getElementById('curStatus');
  try {
    const j = await fetchJson(`${API}/mdapi/prod/webapi/stations.json?type=currentpredictions`);
    const byId = new Map();
    for (const s of j.stations) {
      if (!(s.lat > BOUNDS.s && s.lat < BOUNDS.n && s.lng > BOUNDS.w && s.lng < BOUNDS.e)) continue;
      if (s.type !== 'H' && s.type !== 'S') continue;
      const prev = byId.get(s.id);
      const depth = s.depth ?? 1e9;
      if (!prev || depth < prev.depth) byId.set(s.id, { id: s.id, name: s.name, lat: s.lat, lng: s.lng, type: s.type, bin: s.currbin, depth });
    }
    CUR.stations = [...byId.values()];
  } catch (e) {
    status.textContent = 'couldn\'t reach NOAA currents'; return;
  }
  const begin = ymd(new Date(Date.now() - 86400000));
  let done = 0, ok = 0;
  const queue = [...CUR.stations];
  // nearest-to-view first
  const c = map.getCenter();
  queue.sort((a, b) => Math.hypot(a.lat - c.lat, a.lng - c.lng) - Math.hypot(b.lat - c.lat, b.lng - c.lng));
  const worker = async () => {
    while (queue.length) {
      const st = queue.shift();
      try { st.data = await loadStation(st, begin); ok++; } catch { st.data = null; }
      done++;
      status.textContent = `currents ${done}/${CUR.stations.length}`;
      if (st.data) addStationMarker(st);
      if (st.id === 'SFB1201') renderGate();
    }
  };
  await Promise.all(Array.from({ length: 6 }, worker));
  status.textContent = `${ok} current stations`;
  renderCurrents();
  renderGate();
}

function addStationMarker(st) {
  const m = L.marker([st.lat, st.lng], { pane: 'curP', icon: curIcon() })
    .bindPopup(() => stationPopup(st));
  m.addTo(groups.currents);
  CUR.markers.set(st.id, m);
  paintStation(st, m, selTime());
}

function paintStation(st, m, t) {
  const el = m.getElement();
  if (!el) return;
  const c = currentAt(st, t);
  const svg = el.querySelector('.ca'), lab = el.querySelector('.cs'), path = svg.querySelector('path');
  if (!c) { svg.style.opacity = 0.15; lab.textContent = ''; return; }
  const sc = c.spd < 0.15 ? 0.35 : 0.62 + Math.min(c.spd, 5) / 5 * 0.9;
  svg.style.opacity = c.spd < 0.15 ? 0.5 : 1;
  svg.style.transform = `rotate(${c.dir}deg) scale(${sc})`;
  path.setAttribute('fill', speedColor(c.spd));
  lab.textContent = c.spd >= 0.15 ? c.spd.toFixed(1) : 'slack';
}

function renderCurrents() {
  const t = selTime();
  for (const st of CUR.stations) {
    const m = CUR.markers.get(st.id);
    if (m) paintStation(st, m, t);
  }
}
map.on('zoomend moveend', () => renderCurrents());
map.on('layeradd', e => { if (e.layer === groups.currents) setTimeout(renderCurrents, 0); });

function renderGate() {
  const box = document.getElementById('gate');
  const st = CUR.stations.find(s => s.id === 'SFB1201');
  if (!st?.data) { box.innerHTML = ''; return; }
  const t = selTime(), c = currentAt(st, t);
  if (!c) { box.innerHTML = '<span class="muted">Golden Gate: outside prediction window</span>'; return; }
  const ebb = c.dir > 160 && c.dir < 340;
  const phase = c.spd < 0.4 ? 'near slack' : ebb ? 'EBB: flowing out to sea' : 'FLOOD: flowing into the Bay';
  const next = eventsAfter(st, t, 3).map(e => `${e.type === 'slack' ? 'slack' : `max ${e.spd.toFixed(1)} kn`} ${fmtClock(e.t)}`).join(' · ');
  box.innerHTML = `<b>Golden Gate Bridge</b>: <span style="color:${speedColor(c.spd)}">${c.spd.toFixed(1)} kn</span>, ${phase}
    <div class="muted small">next: ${next}</div>`;
}

// ------------------------------------------------------------------ ships (AIS)
const SHIPS = new Map();
function shipClass(type) {
  const t = +type || 0;
  if (t >= 60 && t < 70) return ['Passenger / ferry', '#4fa3ff'];
  if (t >= 70 && t < 80) return ['Cargo', '#6fd06f'];
  if (t >= 80 && t < 90) return ['Tanker', '#ff6b6b'];
  if ([31, 32, 52].includes(t)) return ['Tug / towing', '#2ec4b6'];
  if (t === 36) return ['Sailing', '#c58cff'];
  if (t === 37) return ['Pleasure craft', '#f2a541'];
  if (t === 30) return ['Fishing', '#ffd166'];
  if ([35, 51, 55].includes(t)) return ['Military / SAR / law enforcement', '#ffffff'];
  if (t === 50) return ['Pilot boat', '#ffffff'];
  return ['Unknown type', '#9aa7b5'];
}
function shipIcon(s) {
  const [, col] = shipClass(s.type);
  const len = s.length || 0;
  const px = len >= 150 ? 30 : len >= 60 ? 22 : 14;
  const moving = (s.sog || 0) >= 0.5;
  const rot = moving ? (s.hdg ?? s.cog ?? 0) : 0;
  const shape = moving
    ? `<path d="M0,-10 L4,-3 L4,9 L-4,9 L-4,-3Z" fill="${col}" stroke="#0b121b" stroke-width="1"/>`
    : `<circle r="4" fill="${col}" stroke="#0b121b" stroke-width="1"/>`;
  return L.divIcon({
    className: 'ship-ico', iconSize: [px, px], iconAnchor: [px / 2, px / 2],
    html: `<svg width="${px}" height="${px}" viewBox="-11 -11 22 22" style="transform:rotate(${rot}deg)">${shape}</svg>`,
  });
}
function shipPopup(s) {
  const [cls] = shipClass(s.type);
  return `<b>${esc(s.name || 'MMSI ' + s.mmsi)}</b><br>${cls}${s.length ? ` · ${s.length} m` : ''}<br>
    ${(s.sog ?? 0).toFixed(1)} kn${s.cog != null ? ` · course ${fmtDeg(s.cog)}` : ''}
    ${s.dest ? `<br>→ ${esc(s.dest)}` : ''}<br><span class="muted small">updated ${s.age}s ago</span>`;
}
async function pollShips() {
  const box = document.getElementById('shipStatus');
  let j;
  try {
    const r = await fetch('/api/ships', { cache: 'no-store' });
    j = await r.json();
  } catch {
    box.innerHTML = 'Live ships only work when you run the map locally (<code>map/server.py</code> with an aisstream.io key). See the README.';
    return;
  }
  const st = j.status;
  if (st.ais === 'disabled') {
    box.innerHTML = `Live ships are off. Get a free key at <a href="https://aisstream.io" target="_blank" style="color:#9cc4ff">aisstream.io</a>,
      add <code>AISSTREAM_API_KEY=…</code> to <code>.env</code>, and restart the server.`;
    return;
  }
  const seen = new Set();
  for (const s of j.ships) {
    seen.add(s.mmsi);
    const ahead = (s.sog || 0) >= 0.5 && s.cog != null
      ? turf.destination([s.lon, s.lat], (s.sog * 10 / 60) * 1.852, s.cog, { units: 'kilometers' }).geometry.coordinates : null;
    let e = SHIPS.get(s.mmsi);
    if (!e) {
      e = { m: L.marker([s.lat, s.lon], { pane: 'shipP' }).addTo(groups.ships),
            l: L.polyline([], { pane: 'shipP', weight: 1.5, dashArray: '4 4', opacity: 0.85, interactive: false }).addTo(groups.ships) };
      SHIPS.set(s.mmsi, e);
    }
    e.m.setLatLng([s.lat, s.lon]).setIcon(shipIcon(s));
    e.m.bindPopup(shipPopup(s));
    e.l.setLatLngs(ahead ? [[s.lat, s.lon], [ahead[1], ahead[0]]] : []).setStyle({ color: shipClass(s.type)[1] });
    e.s = s;
  }
  for (const [k, e] of SHIPS) if (!seen.has(k)) { groups.ships.removeLayer(e.m); groups.ships.removeLayer(e.l); SHIPS.delete(k); }
  const big = j.ships.filter(s => (s.length || 0) >= 100 && (s.sog || 0) >= 1).length;
  box.innerHTML = `<b>${j.ships.length}</b> vessels tracked · <b>${big}</b> large ships underway
    <div class="small">${st.ais}${st.error ? `: ${esc(st.error)}` : ''}</div>`;
}

// ------------------------------------------------------------------ route planner
const route = { pts: [], drawing: false, line: L.polyline([], { pane: 'routeP', color: '#fff', weight: 3, dashArray: '1 7', lineCap: 'round' }),
                verts: L.layerGroup(), warnMarks: L.layerGroup() };
route.line.addTo(map); route.verts.addTo(map); route.warnMarks.addTo(map);

const routeBtn = document.getElementById('routeBtn');
routeBtn.onclick = () => {
  route.drawing = !route.drawing;
  routeBtn.classList.toggle('on', route.drawing);
  routeBtn.textContent = route.drawing ? '✓ Done' : '✎ Draw route';
  map.getContainer().style.cursor = route.drawing ? 'crosshair' : '';
  if (route.drawing) map.doubleClickZoom.disable(); else map.doubleClickZoom.enable();
};
document.getElementById('routeClear').onclick = () => { route.pts = []; redrawRoute(); };
document.getElementById('speed').addEventListener('input', () => route.pts.length > 1 && analyzeRoute());
map.on('click', e => {
  if (!route.drawing) return;
  route.pts.push(e.latlng);
  redrawRoute();
});
map.on('dblclick', () => { if (route.drawing) routeBtn.click(); });

function redrawRoute() {
  route.line.setLatLngs(route.pts);
  route.verts.clearLayers();
  route.pts.forEach((p, i) => {
    const m = L.marker(p, { pane: 'routeP', draggable: true,
      icon: L.divIcon({ className: 'lbl', iconSize: [18, 18], iconAnchor: [9, 9],
        html: `<div style="width:18px;height:18px;border-radius:9px;background:#fff;color:#0b121b;display:flex;align-items:center;justify-content:center;font-size:10px">${i + 1}</div>` }) });
    m.on('drag', ev => { route.pts[i] = ev.target.getLatLng(); route.line.setLatLngs(route.pts); });
    m.on('dragend', () => analyzeRoute());
    m.addTo(route.verts);
  });
  analyzeRoute();
}

function nearestCurrent(lat, lng, t) {
  let best = null, bd = 1e9;
  for (const st of CUR.stations) {
    if (!st.data) continue;
    const d = turf.distance([lng, lat], [st.lng, st.lat], { units: 'kilometers' });
    if (d < bd) { bd = d; best = st; }
  }
  if (!best || bd > 4) return null;
  const c = currentAt(best, t);
  return c ? { ...c, st: best, km: bd } : null;
}

function analyzeRoute() {
  const out = document.getElementById('routeOut');
  route.warnMarks.clearLayers();
  if (route.pts.length < 2) { out.innerHTML = route.pts.length ? '<p class="muted small">Add another point…</p>' : ''; return; }
  const boat = Math.max(0.5, +document.getElementById('speed').value || 6);
  let t = selTime(), totalNm = 0, rows = '', warns = [];
  for (let i = 0; i < route.pts.length - 1; i++) {
    const a = route.pts[i], b = route.pts[i + 1];
    const A = [a.lng, a.lat], B = [b.lng, b.lat];
    const leg = turf.lineString([A, B]);
    const nm = turf.distance(A, B, { units: 'nauticalmiles' });
    const brg = norm360(turf.bearing(A, B));
    totalNm += nm;
    // current: average over samples along the leg at the time we'd be there
    let along = 0, cross = 0, n = 0;
    for (let k = 0; k <= 4; k++) {
      const p = turf.along(leg, nm * k / 4, { units: 'nauticalmiles' }).geometry.coordinates;
      const c = nearestCurrent(p[1], p[0], t);
      if (!c) continue;
      const rel = rad(c.dir - brg);
      along += c.spd * Math.cos(rel); cross += c.spd * Math.sin(rel); n++;
    }
    if (n) { along /= n; cross /= n; }
    // to hold the track, crab into the cross-current; remaining boat speed goes along track
    const crabOk = Math.abs(cross) < boat;
    const crab = crabOk ? deg(Math.asin(cross / boat)) : 90;
    const sog = crabOk ? boat * Math.cos(rad(crab)) + along : 0;
    const mins = sog > 0.2 ? nm / sog * 60 : Infinity;
    rows += `<tr><td>${i + 1}→${i + 2}</td><td>${nm.toFixed(2)}</td><td>${fmtDeg(brg)}</td>
      <td>${n ? `<span style="color:${speedColor(Math.hypot(along, cross))}">${along >= 0 ? '+' : ''}${along.toFixed(1)}</span>` : '—'}</td>
      <td>${isFinite(mins) ? Math.round(mins) + ' min' : '<span class="bad">no headway</span>'}</td></tr>`;
    if (n && Math.abs(cross) > 0.7) warns.push(`<span class="warn">Leg ${i + 1}→${i + 2}:</span> current sets you
      ${Math.abs(cross).toFixed(1)} kn to ${cross > 0 ? 'starboard' : 'port'}. Aim about ${Math.round(Math.abs(crab))}°
      to ${cross > 0 ? 'port' : 'starboard'} of your track to stay on it.`);
    if (n && along < -1) warns.push(`<span class="warn">Leg ${i + 1}→${i + 2}:</span> ${(-along).toFixed(1)} kn of current
      against you. Consider a different time.`);
    if (!isFinite(mins)) warns.push(`<span class="bad">Leg ${i + 1}→${i + 2}: at ${boat} kn you can't make headway against this current.</span>`);
    // lanes & channels
    const hits = new Map();
    for (const f of ENC.lanes.features) {
      if (!turf.booleanIntersects(leg, f)) continue;
      const name = (f.properties.INFORM || 'Traffic lane').replace(/\s*\(33 CFR.*\)/, '');
      const ang = Math.abs(((brg - f.properties.ORIENT) % 180 + 180) % 180);
      const cross90 = Math.min(ang, 180 - ang);
      const prev = hits.get(name);
      if (!prev || cross90 < prev.a) hits.set(name, { a: cross90, o: f.properties.ORIENT });
    }
    for (const [name, h] of hits) {
      warns.push(h.a < 55
        ? `<span class="bad">Leg ${i + 1}→${i + 2} runs along the <b>${esc(name)}</b></span> (ships go ${fmtDeg(h.o)}).
           Get out of the lane, or cross it at a right angle.`
        : `<span class="warn">Leg ${i + 1}→${i + 2} crosses the <b>${esc(name)}</b></span> at ~${Math.round(h.a)}°.
           Ships go ${fmtDeg(h.o)}. Look both ways, cross quickly, and pass behind ships.`);
    }
    for (const f of ENC.precaution.features) if (turf.booleanIntersects(leg, f)) {
      warns.push(`<span class="warn">Leg ${i + 1}→${i + 2}</span> passes through a <b>precautionary area</b>, where ships converge and turn.`); break;
    }
    const dn = new Set();
    for (const f of ENC.dredged.features) if (turf.booleanIntersects(leg, f)) dn.add(f.properties.OBJNAM || 'dredged channel');
    if (dn.size) warns.push(`<span class="warn">Leg ${i + 1}→${i + 2}</span> crosses dredged ship channels: ${[...dn].slice(0, 3).map(esc).join(', ')}.
      Watch for ships that can't leave the channel.`);
    // hazards near the leg
    for (const h of HAZ) {
      const d = turf.pointToLineDistance(h.pt, leg, { units: 'nauticalmiles' });
      if (d < 0.06 && h.watlev !== 2) {
        const [lon, lat] = h.pt.geometry.coordinates;
        L.circleMarker([lat, lon], { pane: 'routeP', radius: 9, color: '#ff4d4d', weight: 2, fill: false })
          .bindPopup(`<b>${esc(h.label)}</b> within ${Math.round(d * 1852)} m of your route`).addTo(route.warnMarks);
        if (route.warnMarks.getLayers().length <= 6) warns.push(`<span class="bad">Hazard:</span> ${esc(h.label)} about
          ${Math.round(d * 1852)} m from leg ${i + 1}→${i + 2}${h.depth != null ? ` (${mToFt(h.depth)} ft deep)` : ''}.`);
      }
    }
    if (isFinite(mins)) t += mins * 60000;
  }
  const hz = route.warnMarks.getLayers().length;
  if (hz > 6) warns.push(`<span class="bad">…and ${hz - 6} more hazards</span> near the route (circled in red).`);
  const totalMin = (t - selTime()) / 60000;
  out.innerHTML = `<div class="card"><b>${totalNm.toFixed(2)} nm</b> · ${isFinite(totalMin) ? `about <b>${Math.round(totalMin)} min</b> · arrive ${fmtClock(t)}` : ''}
      <div class="muted small">leaving ${fmtTime(selTime())} at ${boat} kn through the water</div></div>
    <table><tr><th>leg</th><th>nm</th><th>heading</th><th>current<br>(kn, + helps)</th><th>time</th></tr>${rows}</table>
    ${warns.length ? `<ul>${warns.map(w => `<li>${w}</li>`).join('')}</ul>` : '<p class="ok">No ship lanes, dredged channels, or charted hazards right on this route.</p>'}`;
}

// ------------------------------------------------------------------ panel & locate
document.getElementById('collapse').onclick = () => { document.getElementById('panel').classList.add('hidden'); document.getElementById('expand').style.display = 'block'; };
document.getElementById('expand').onclick = () => { document.getElementById('panel').classList.remove('hidden'); document.getElementById('expand').style.display = 'none'; };
const Locate = L.Control.extend({
  onAdd() {
    const b = L.DomUtil.create('button'); b.textContent = '◎'; b.title = 'Show my location';
    b.style.cssText = 'font-size:16px;padding:4px 9px';
    L.DomEvent.on(b, 'click', ev => { L.DomEvent.stop(ev); map.locate({ setView: true, maxZoom: 15 }); });
    return b;
  },
});
new Locate({ position: 'topright' }).addTo(map);
let me = null;
map.on('locationfound', e => { me?.remove(); me = L.circleMarker(e.latlng, { radius: 7, color: '#fff', fillColor: '#4fa3ff', fillOpacity: 1, pane: 'shipP' }).addTo(map); });

// ------------------------------------------------------------------ boot
(async function boot() {
  syncLayers();
  onTime();
  try {
    ENC = await (await fetch('data/enc.json')).json();
    buildChannels(); buildAreas(); buildLanes(); buildHazards(); buildBuoys(); buildPier40();
    const [fer, zon] = await Promise.all(['data/ferries.json', 'data/zones.json'].map(u => fetch(u).then(r => r.json())));
    buildFerries(fer); buildZones(zon);
  } catch (e) {
    console.error(e);
    document.getElementById('curStatus').textContent = 'chart data failed to load: run map/server.py';
  }
  syncLayers();
  loadCurrents();
  pollShips();
  setInterval(pollShips, 5000);
})();
