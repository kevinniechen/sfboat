/* Learn mode: a guided, quiz-driven course on the map, starting from Pier 40.
   Uses globals from app.js (map, groups, syncLayers, slider, onTime, CUR, ...). */
'use strict';

const P40 = [37.7814, -122.3867];
const PLACES = {
  sbNorth: [37.7819, -122.3847],
  research3A: [37.7836, -122.3850],
  ferryBldg: [37.7955, -122.3937],
  precaution: [37.7994, -122.3967],
  oakBar1: [37.8043, -122.3560],
  oakBar2: [37.7995, -122.3605],
  anch8A: [37.7812, -122.3616],
  wreck51: [37.7844, -122.3791],
  rock0: [37.7386, -122.3684],
  blossom: [37.8184, -122.4028],
  gate: [37.8100, -122.4775],
};

// ------------------------------------------------------------------ lessons
const LESSONS = [
  {
    id: 'big-picture', title: 'What to pay attention to', tag: 'start here',
    steps: [
      {
        view: [37.795, -122.40, 13], layers: {},
        html: `<p>Out on the Bay, everything is competing for your attention. Here's what to watch, <b>in order
          of how badly it can hurt you</b>:</p>
          <ol class="prio">
            <li><b>Big ships and ferries.</b> They're huge and fast, they can't stop or swerve, and they often can't see you.</li>
            <li><b>Current and wind.</b> The water itself moves, and the afternoon wind builds. Either can push you
              somewhere you didn't plan to go, or keep you from getting home.</li>
            <li><b>Things you can hit.</b> Shallow water, rocks, piers, and buoys.</li>
            <li><b>Other small boats.</b> The rules of the road decide who moves.</li>
            <li><b>Markers.</b> They tell you where the safe water is, but only in channels.</li>
          </ol>
          <p>Each lesson takes one of these and shows it to you <b>on your actual water</b>, starting from Pier 40.
          Each one is short and ends with a quiz.</p>`,
      },
    ],
  },
  {
    id: 'geography', title: 'Your Bay: where everything is', tag: 'ships, ferries, calm & rough water',
    steps: [
      {
        view: [37.815, -122.43, 12], layers: { lanes: true, channels: true }, anim: 'ships',
        marks: [{ ll: PLACES.gate, label: 'Golden Gate', color: '#e040c8' }, { ll: PLACES.oakBar2, label: 'to Oakland port', color: '#7aa0dc' },
                { ll: P40, label: 'you (Pier 40)' }],
        html: `<p>Start with the <b>shipping highways</b>. Big ships enter under the <b>Golden Gate</b> and follow the
          <span style="color:#e040c8"><b>pink traffic lanes</b></span>, one lane for each direction, past Alcatraz. The arrows show
          which way ships travel in each lane, like the two sides of a freeway.</p>
          <p>From there, most head for <b>Oakland</b> (east, past the Bay Bridge) or north to <b>Richmond</b>.
          The <span style="color:#7aa0dc"><b>blue-gray shapes</b></span> are dredged channels: deep trenches that ships can't
          leave.</p>
          <p>Notice that Pier 40 sits <b>south of all of this</b>. To reach the rest of the Bay, you have to cross ship traffic near the Bay Bridge.</p>`,
      },
      {
        view: [37.83, -122.39, 12], layers: { ferries: true, lanes: true }, anim: 'ferries',
        marks: [{ ll: PLACES.ferryBldg, label: 'Ferry Building (the hub)', color: '#4fa3ff' }, { ll: P40, label: 'Pier 40' }],
        html: `<p>Now the <span style="color:#4fa3ff"><b>ferry routes</b></span>. They spread out from the <b>Ferry Building</b> like spokes:
          to Oakland, Alameda, Sausalito, Larkspur, Tiburon, Vallejo, Richmond, Treasure Island and South San Francisco.</p>
          <p>Two things to notice near you:</p>
          <ul>
            <li>Ferries to Oakland and Alameda pass <b>right off the southern waterfront</b>, between Pier 40 and the Bay Bridge.</li>
            <li>The <b>dashed</b> routes are event-day ferries to <b>Oracle Park and Chase Center</b>, a few hundred
              meters from your harbor. On game and concert days, expect fast ferries coming and going.</li>
          </ul>
          <p>Ferries go 25–35 knots. Click any route to see its name.</p>`,
      },
      {
        view: [37.835, -122.43, 12], layers: { zones: true },
        html: `<p>Now <b>where the water gets rough</b>. Each red zone is one of these:</p>
          <ul>
            <li><b>Golden Gate</b>: the strongest current in the Bay, ocean swell, and steep waves when wind fights the ebb.</li>
            <li><b>The Slot</b>: the band from the Gate past Alcatraz toward Berkeley. Summer afternoon wind funnels through it at 20–25+ knots.</li>
            <li><b>Around Alcatraz, Point Blunt, and Raccoon Strait</b>: current speeds up around points and through narrow gaps.</li>
            <li><b>The Bay Bridge</b>: current swirls around the towers, and ships and ferries converge there.</li>
          </ul>
          <p>Click a zone for details. These areas are approximate, based on typical conditions. The pattern to remember:
          <b>rough water is where the wind funnels and where the current squeezes</b>, through gaps, around points and islands.</p>`,
      },
      {
        view: [37.80, -122.39, 13], layers: { zones: true },
        marks: [{ ll: P40, label: 'Pier 40' }],
        html: `<p>And the <span style="color:#2fcf6f"><b>calmer, sheltered</b></span> water: places protected by land or a
          breakwater, or out of the afternoon wind's path.</p>
          <ul>
            <li><b>McCovey Cove / China Basin</b>: right next to you. Good for practicing slow maneuvers.</li>
            <li><b>The southern waterfront</b> (yellow): usually less wind than the Slot, especially in the
              morning. A sensible first practice area, as long as you watch for ferries and stay clear of ships at
              Anchorage 8A.</li>
            <li><b>Clipper Cove</b> (Treasure Island): a sheltered destination. Getting there means crossing the busy Bay Bridge area.</li>
            <li>Farther away: <b>Richardson Bay</b> (Sausalito) and the <b>Oakland Estuary</b>.</li>
          </ul>`,
      },
      {
        view: [37.815, -122.42, 12], layers: { zones: true, lanes: true }, anim: 'everything',
        html: `<p>Now everything at once: a typical summer afternoon.</p>
          <ul>
            <li><b>Ships</b> run the lanes from the Gate, past Alcatraz, then cut across to Oakland under the Bay Bridge, just north of you.</li>
            <li><b>Ferries</b> shuttle from the Ferry Building in every direction, faster than anything else out there.</li>
            <li><b>Sailboats</b> race in the Slot, because that's where the wind is.</li>
            <li><b>You</b> (orange) practice along the southern waterfront, away from the lanes, with the ferry routes in view.</li>
          </ul>
          <p>Watch where everything converges: the <b>Bay Bridge / Ferry Building area</b>, a mile north of Pier 40.
          That's the spot to be most alert whenever you head north.</p>`,
      },
      {
        view: [37.80, -122.40, 12], layers: { zones: true, ferries: true, lanes: true },
        quiz: {
          q: `For your first few trips from Pier 40, which plan makes the most sense?`,
          options: [
            { t: 'Morning, along the southern waterfront, staying clear of ferries and ship areas', ok: true,
              why: 'Yes. Calmer water, close to home, lighter morning wind, and away from the shipping lanes. Build skills there first.' },
            { t: 'Afternoon trip out to the Golden Gate Bridge', why: 'The Gate is the roughest water in the Bay, and afternoons bring the strongest wind. Save it for much later, with an experienced skipper.' },
            { t: 'Cross the Slot to Angel Island around 3 pm', why: 'That means crossing the ship lanes in the windiest part of the Bay, at the windiest time of day. Not a beginner trip.' },
          ],
        },
      },
    ],
  },
  {
    id: 'home', title: 'Leaving and returning to Pier 40', tag: 'markers, part 1',
    steps: [
      {
        view: [37.7805, -122.3850, 17], layers: { chart: true, buoys: true },
        marks: [{ ll: [37.7819, -122.3847], label: 'north entrance', color: '#fff' },
                { ll: [37.7784, -122.3852], label: 'south entrance', color: '#fff' }],
        html: `<p>This is the <b>official NOAA chart</b> of your harbor. It shows something the plain map doesn't:
          the <b>breakwater</b>, the long black wall along the right (east) side of the marina. It protects the docks from waves.</p>
          <p>Because of it, there are only <b>two ways in or out</b>: a gap at the <b>north end</b> of the wall and a gap at the
          <b>south end</b>.</p>
          <p>The green "1" and red "2" are lights on posts at the <b>two sides of each gap</b>, like the
          posts of a doorway. The doorway is narrow, about <b>40 m (130 ft)</b> wide, which is why the dots look so close together.</p>`,
      },
      {
        view: [37.7801, -122.3849, 17], layers: { chart: true, buoys: true },
        anim: 'harborIn',
        paths: [{ pts: [[37.7827, -122.383], [37.7826, -122.3845], [37.7819, -122.3847], [37.7812, -122.385]], label: 'coming home (north door)', color: '#4fa3ff' },
                { pts: [[37.7773, -122.3866], [37.7779, -122.3859], [37.7784, -122.3852], [37.7789, -122.3847]], label: 'coming home (south door)', color: '#4fa3ff' }],
        html: `<p>Here's how you <b>come home</b> through each door (blue arrows):</p>
          <ul>
            <li><b>North door:</b> come around the north tip of the breakwater, then turn and go through the gap <b>heading south</b>.
              The <b class="r">red 2</b> ends up on your <b>right</b> (the pier side) and the <b class="g">green 1</b> on your left (the breakwater).</li>
            <li><b>South door:</b> approach from the China Basin side, <b>heading northeast</b>. Again,
              <b class="r">red</b> on your right and <b class="g">green</b> on your left.</li>
          </ul>
          <p>Notice that the red light sits on a <b>different wall</b> at each door. The rule isn't about which wall;
          it's about <b>your direction</b>. Heading into the harbor, red is on your right.</p>
          <p class="rule">Red, Right, Returning</p>`,
      },
      {
        view: [37.7801, -122.3849, 17], layers: { chart: true, buoys: true },
        anim: 'harborOut',
        paths: [{ pts: [[37.7812, -122.385], [37.7819, -122.3847], [37.7826, -122.3845], [37.7827, -122.383]], label: 'leaving (north door)', color: '#f2a541' },
                { pts: [[37.7789, -122.3847], [37.7784, -122.3852], [37.7779, -122.3859], [37.7773, -122.3866]], label: 'leaving (south door)', color: '#f2a541' }],
        html: `<p><b>Leaving</b> is the same doorway in reverse (orange arrows), so everything flips:
          <b class="r">red</b> is on your <b>left</b> and <b class="g">green</b> on your right.</p>
          <p>So yes, it matters both ways. The rule is named for returning; when you leave, just flip it.</p>
          <p>What actually matters at a harbor entrance:</p>
          <ul>
            <li>Go through the <b>middle</b> of the gap, <b>slowly</b>, with no wake.</li>
            <li>It's narrow, so if another boat is coming the other way, <b>keep to your right side</b> of the gap,
              just like a narrow road.</li>
            <li>You can't see around the corner. <b>Go slow and look</b> before you turn through.</li>
          </ul>`,
      },
      {
        view: [37.7812, -122.3848, 18], layers: { chart: true, buoys: true },
        paths: [{ pts: [[37.7827, -122.383], [37.7826, -122.3845], [37.7819, -122.3847], [37.7812, -122.385]], label: '?', color: '#4fa3ff' }],
        quiz: {
          q: `You're coming home through the north door, heading south into the harbor (blue arrow). Which side is the red "2" on?`,
          options: [
            { t: 'On my right (starboard)', ok: true, why: 'Right. You\'re returning (going into the harbor), so red is on your right.' },
            { t: 'On my left (port)', why: 'That\'s for leaving. Going into the harbor is returning, so red is on your right.' },
            { t: 'It doesn\'t matter, just go between them', why: 'Going between them is the main thing, but checking that red is on your right confirms you\'re heading the right way through the right gap.' },
          ],
        },
      },
      {
        view: [37.7790, -122.3851, 18], layers: { chart: true, buoys: true },
        paths: [{ pts: [[37.7789, -122.3847], [37.7784, -122.3852], [37.7779, -122.3859], [37.7773, -122.3866]], label: '?', color: '#f2a541' }],
        quiz: {
          q: `Now you're leaving through the south door, heading southwest out toward China Basin (orange arrow). Where's the red "2"?`,
          options: [
            { t: 'On my left (port)', ok: true, why: 'Yes. Leaving flips the rule: red on your left, green on your right.' },
            { t: 'On my right (starboard)', why: 'That\'s for coming in. You\'re leaving, so red is on your left.' },
          ],
        },
      },
      {
        view: [37.7835, -122.3815, 15], layers: { buoys: true, hazards: true },
        marks: [{ ll: PLACES.research3A, label: 'yellow buoy "3A"', color: '#f5c542' }],
        html: `<p>Here's the surprise: <b>once you're out of the harbor, there's no channel.</b> It's open water.
          No red and green to follow, no lanes. That's normal. Most of the time, a small boat isn't in a channel.</p>
          <p>The first buoy you'll pass outside is this <b style="color:#f5c542">yellow</b> one, "3A". Yellow means
          <b>special purpose</b>: this one is a research buoy. It doesn't mark a channel. It's simply something solid
          to avoid hitting.</p>
          <p>In open water you navigate by three things: <b>the rules of the road</b> (who gives way), <b>the
          chart</b> (where it's shallow), and <b>your eyes</b>.</p>`,
      },
    ],
  },
  {
    id: 'ships', title: 'Big ships and ferries', tag: 'priority #1',
    steps: [
      {
        view: [37.795, -122.378, 14], layers: { lanes: true, channels: true, buoys: true },
        marks: [{ ll: PLACES.precaution, label: 'precautionary area', color: '#f5c542' },
                { ll: PLACES.oakBar2, label: 'Oakland Bar Channel', color: '#7aa0dc' }],
        html: `<p>The yellow dashed shape just north of Pier 40 is a <b style="color:#f5c542">precautionary area</b>,
          around the Bay Bridge. Ships coming in from the Golden Gate pass through here, and many turn toward
          <b>Oakland</b>, one of the busiest container ports on the West Coast. They enter it through the
          <b>Oakland Bar Channel</b>, marked by buoys south of Yerba Buena Island.</p>
          <p>So the water between you and Treasure Island is, in effect, a <b>highway on-ramp for container ships</b>.</p>
          <p>The rule that matters: <b>in a channel, you must not get in the way of a ship that can only operate in the
          channel.</b> No matter what the other rules say, they win.</p>`,
      },
      {
        view: [37.795, -122.378, 14], layers: { lanes: true, channels: true },
        html: `<p>Why do they always win? A loaded container ship:</p>
          <ul>
            <li>is over <b>300 m</b> long, which is about 40 times your boat,</li>
            <li>travels at <b>10–15 knots</b>, two or three times your speed,</li>
            <li>needs a <b>mile or more</b> to stop, and can't leave the deep channel to swerve,</li>
            <li>has its bridge at the very back, so the water <b>hundreds of meters ahead of its bow</b> can be
              invisible to the crew.</li>
          </ul>
          <p>Ships that look slow are not slow. They're just far away and huge.</p>`,
        quiz: {
          q: `You want to cross toward Treasure Island. A container ship is coming through the precautionary area, about a mile away, heading for Oakland. What do you do?`,
          options: [
            { t: 'Wait, or turn, and pass well behind it', ok: true, why: 'Exactly. Always pass behind a ship, never in front. Slowing down and waiting a few minutes is free.' },
            { t: 'Speed up and cross in front. A mile is plenty.', why: 'At 15 knots it covers a mile in 4 minutes, and you may be in its blind zone. If your engine stalls in front of it, there\'s nothing it can do.' },
            { t: 'Hold course. As a powerboat, I\'m equal to it.', why: 'In a channel, small boats must not impede ships that can only operate there. And even outside channels, "being right" doesn\'t help against 100,000 tons.' },
          ],
        },
      },
      {
        view: [37.788, -122.385, 15], layers: { channels: true },
        marks: [{ ll: PLACES.ferryBldg, label: 'Ferry Building', color: '#4fa3ff' }],
        html: `<p><b>Ferries</b> are the other big one, and they're right next door. The Ferry Building is about
          <b>1 nautical mile</b> north of Pier 40. Ferries leave it all day for Oakland, Alameda, Sausalito, Larkspur,
          Tiburon, Vallejo and more, at <b>25–35 knots</b>.</p>
          <p>They don't follow the ship lanes. They go wherever their route takes them, and they appear quickly.</p>`,
        quiz: {
          q: `A ferry is 2 nautical miles away, coming toward you at 30 knots. Roughly how long until it's where you are?`,
          options: [
            { t: 'About 4 minutes', ok: true, why: 'Right: 30 knots is a mile every 2 minutes. That\'s why you look around constantly, every 30 seconds or so, including behind you.' },
            { t: 'About 15 minutes', why: '30 knots means 30 nautical miles an hour, which is one mile every 2 minutes. So 2 miles takes 4 minutes.' },
            { t: 'About 30 minutes', why: 'Much faster than that: 30 knots covers 1 nm in 2 minutes, so 2 nm takes 4 minutes.' },
          ],
        },
      },
      {
        view: [37.783, -122.37, 15], layers: { areas: true },
        marks: [{ ll: PLACES.anch8A, label: 'Anchorage 8A', color: '#c9a7ff' }],
        html: `<p>Turn on the purple outlines: that's <b>Anchorage 8A</b>, only about <b>1.2 nm east</b> of Pier 40.
          Big ships wait here, sometimes for days, for a berth in Oakland.</p>
          <ul>
            <li>An anchored ship can <b>start moving</b> when its turn comes.</li>
            <li>It <b>swings</b> around its anchor as the current changes.</li>
            <li>The current builds up against its hull. <b>Never pass close on the downstream side</b>, because
              the current can push you into it.</li>
          </ul>
          <p>Give anchored ships a wide berth: at least a few hundred meters.</p>`,
      },
      {
        view: [37.8, -122.39, 13], layers: { lanes: true },
        html: `<p>How do you know a ship is coming before it's close?</p>
          <ul>
            <li><b>Look.</b> Do a full 360° scan, including behind you, every 30 seconds or so.</li>
            <li><b>Listen on VHF channel 14</b> (Vessel Traffic Service). Ships report things like
              "inbound, passing Alcatraz, bound for Oakland."</li>
            <li><b>Five or more short horn blasts</b> means "danger, I don't understand what you're doing." If you
              hear it, assume it's for you and change something, obviously.</li>
            <li><b>The live ship layer</b> on this map, once you add the free AIS key, shows ship positions.</li>
          </ul>`,
        quiz: {
          q: `You hear five short blasts from a ship nearby. What does it mean?`,
          options: [
            { t: 'Danger / "I don\'t understand your intentions"', ok: true, why: 'Yes. Make a clear, obvious move away from the ship, such as a big turn or slowing right down, so it can see what you\'re doing.' },
            { t: 'Hello, a friendly greeting', why: 'Ships don\'t honk to say hi. Five short blasts is the danger signal.' },
            { t: '"I\'m turning to starboard"', why: 'That\'s one short blast. Five short means danger or doubt.' },
          ],
        },
      },
    ],
  },
  {
    id: 'current', title: 'The water moves: current', tag: 'priority #2',
    steps: [
      {
        view: [37.80, -122.43, 12], layers: { currents: true },
        marks: [{ ll: PLACES.gate, label: 'Golden Gate', color: '#2ec4b6' }],
        html: `<p>Each arrow shows which way the water is flowing at that spot <b>right now</b>. The color and length show
          its speed in knots.</p>
          <p>Roughly every six hours, the tide reverses through the Golden Gate:</p>
          <ul>
            <li><b>Flood</b>: water pours <b>into</b> the Bay.</li>
            <li><b>Ebb</b>: water drains <b>out</b> to sea.</li>
            <li><b>Slack</b>: the brief pause when it turns, and the calmest time.</li>
          </ul>
          <p>Press the buttons to jump to the next strong ebb and flood, and watch the arrows flip.</p>
          <div class="row"><button data-jump="ebb">Next max ebb</button><button data-jump="flood">Next max flood</button>
          <button data-jump="slack">Next slack</button><button data-jump="now">Now</button></div>
          <div id="jumpOut" class="muted small"></div>`,
      },
      {
        view: [37.785, -122.385, 14], layers: { currents: true },
        marks: [{ ll: P40, label: 'Pier 40' }],
        html: `<p>Here's the key idea. Your boat moves <b>through the water</b>, and the water moves <b>over the ground</b>.
          What you actually get is the two added together.</p>
          <ul>
            <li>Current <b>behind</b> you: you go faster than your boat speed.</li>
            <li>Current <b>against</b> you: you go slower. Sometimes you barely move.</li>
            <li>Current <b>from the side</b>: you drift sideways, even though your bow points straight.</li>
          </ul>
          <p>Near Pier 40 the current mostly runs along the shore, roughly north–south. Near the Golden Gate it can
          reach <b>4–6 knots</b>, which is as fast as many small boats go.</p>`,
        quiz: {
          q: `Your boat does 5 knots. You head straight into a 2-knot current. How fast are you actually moving over the ground?`,
          options: [
            { t: '3 knots', ok: true, why: 'Right: 5 − 2 = 3. Turn around and you\'d do 7. That\'s why you plan your trip so the current helps you home.' },
            { t: '5 knots', why: 'Your speed through the water is 5, but the water is moving 2 knots the other way. Over the ground you make 3.' },
            { t: '7 knots', why: 'That\'s with the current behind you. Into it, you subtract: 5 − 2 = 3.' },
          ],
        },
      },
      {
        view: [37.785, -122.385, 14], layers: { currents: true, buoys: true },
        html: `<p>Current also pushes you <b>sideways into things that don't move</b>: piers, pilings, buoys, anchored ships.
          This is the most common way beginners bump into stuff, especially when docking.</p>
          <p>Tip: <b>look at a buoy or piling</b>. The water streaming past it, with a little wake on one side, shows you
          exactly which way and how hard the current is running.</p>
          <p>And the <b>wind</b> usually picks up through the day. On summer afternoons a strong westerly (from the
          ocean) is routine, especially between the Gate and Berkeley. When that wind blows <b>against</b> an ebb
          current, the waves get short and steep.</p>`,
        quiz: {
          q: `What should you check before you go out?`,
          options: [
            { t: 'Current predictions and the wind forecast', ok: true, why: 'Yes. Plan to leave in the morning, around slack if you can, and to come home with the current and wind helping.' },
            { t: 'Just the tide height (high or low)', why: 'Tide height tells you how deep the water is, but not how fast it\'s moving. On the Bay, the current is what moves you. Check the current predictions.' },
            { t: 'Nothing, I can see the water', why: 'You can\'t see the current until you\'re in it, and afternoon wind builds quickly. Always check both.' },
          ],
        },
      },
    ],
  },
  {
    id: 'hazards', title: 'Things you can hit', tag: 'priority #3',
    steps: [
      {
        view: [37.785, -122.383, 15], layers: { hazards: true },
        marks: [{ ll: PLACES.wreck51, label: 'wreck, 51 ft deep', color: '#ffd166' }],
        html: `<p>The chart shows lots of rocks, wrecks and obstructions. Most of them <b>don't matter to you</b>. The
          number that matters is <b>how deep it is</b>.</p>
          <p>This wreck, 0.4 nm from Pier 40, lies <b>51 feet</b> under the surface. Your boat probably reaches only
          3 to 6 feet below the waterline (that's called its <b>draft</b>). You could float over it all day.</p>
          <p>Click any orange or yellow dot to see its depth.</p>`,
      },
      {
        view: [37.742, -122.372, 15], layers: { hazards: true },
        marks: [{ ll: PLACES.rock0, label: 'rock, 0 ft', color: '#ff4d4d' }],
        html: `<p>Compare that wreck with this rock off the southern waterfront. Its charted depth is <b>0 ft</b>: it's
          right at the surface at low tide. This one really matters.</p>
          <p>Chart depths are measured at a <b>low tide level</b>, so the real water is usually a bit deeper than
          the number, but you shouldn't count on that.</p>
          <p>As a rule, <b>danger lives close to shore</b>: near points of land, around islands, and near old piers and
          pilings. Open water in the middle of the Central Bay is mostly deep.</p>`,
        quiz: {
          q: `Your boat's draft is 4 ft. Which of these should you worry about?`,
          options: [
            { t: 'A rock charted at 0 ft', ok: true, why: 'Yes. 0 ft is at the surface at low tide, so your 4-ft keel or prop would hit it.' },
            { t: 'A wreck charted at 51 ft', why: 'That\'s 47 ft below your boat. No danger to you (only to ships).' },
            { t: 'Blossom Rock, charted at about 39 ft', why: 'Its name sounds scary, but at 39 ft it\'s a concern for deep ships, not for you.' },
          ],
        },
      },
    ],
  },
  {
    id: 'rules', title: 'Other boats: who moves?', tag: 'priority #4',
    steps: [
      {
        view: [37.788, -122.378, 16], layers: {},
        scene: [{ ll: [37.7865, -122.3790], hdg: 0, col: '#4fa3ff', label: 'you' },
                { ll: [37.7885, -122.3755], hdg: 270, col: '#f2a541', label: 'powerboat' }],
        html: `<p>When two small boats might collide, one has to move (the <b>give-way</b> boat) and the other holds steady
          (the <b>stand-on</b> boat). For two powerboats, there are three situations:</p>
          <ul>
            <li><b>Crossing:</b> the boat on <b>your right</b> has priority. If they're on your right, you give way.</li>
            <li><b>Head-on:</b> both turn <b>right</b> and pass left side to left side.</li>
            <li><b>Overtaking:</b> the boat doing the passing keeps clear.</li>
          </ul>
          <p>When you give way, make it <b>early and obvious</b>: a big turn to the right, or slow right down.</p>`,
        quiz: {
          q: `You're heading north. A powerboat is coming from your right, crossing your path. Who gives way?`,
          options: [
            { t: 'Me', ok: true, why: 'Yes. The boat on your right stands on. Slow down or turn right and pass behind it.' },
            { t: 'The other boat', why: 'The boat on the right has priority. You see its red (left-side) light, and red means stop.' },
            { t: 'Whoever is faster', why: 'Speed doesn\'t matter. The boat on your right has priority, so you give way.' },
          ],
        },
      },
      {
        view: [37.788, -122.378, 16], layers: {},
        scene: [{ ll: [37.7865, -122.3790], hdg: 0, col: '#4fa3ff', label: 'you' },
                { ll: [37.7885, -122.3830], hdg: 90, col: '#c58cff', label: 'sailboat (sails only)', sail: true }],
        quiz: {
          q: `Same spot, but this time a sailboat under sail alone (no engine) crosses from your LEFT. Who gives way?`,
          options: [
            { t: 'Me, because powerboats give way to sailboats', ok: true, why: 'Right. Sailboats can\'t maneuver as easily, so powerboats keep clear of them. (A sailboat with its engine running counts as a powerboat.)' },
            { t: 'The sailboat, because it\'s on my left', why: 'Left and right only decide things between two similar boats. A powerboat gives way to a boat under sail.' },
          ],
        },
      },
      {
        view: [37.788, -122.378, 16], layers: {},
        scene: [{ ll: [37.7850, -122.3790], hdg: 0, col: '#4fa3ff', label: 'you (faster)' },
                { ll: [37.7880, -122.3790], hdg: 0, col: '#c58cff', label: 'slow sailboat', sail: true }],
        quiz: {
          q: `You're catching up to a slow sailboat from behind. Who gives way?`,
          options: [
            { t: 'Me, the overtaking boat', ok: true, why: 'Yes. Whoever is overtaking always keeps clear, whatever kind of boat it is. Pass with plenty of room.' },
            { t: 'The sailboat should move over', why: 'The boat being passed holds its course. The overtaking boat keeps clear.' },
          ],
        },
      },
    ],
  },
  {
    id: 'checklist', title: 'Before every trip', tag: 'putting it together',
    steps: [
      {
        view: [37.795, -122.40, 13], layers: { lanes: true, currents: true, channels: true },
        html: `<p>Your 5-minute pre-trip routine:</p>
          <ol class="prio">
            <li><b>Current:</b> when is slack, and which way will it be running on your way home?</li>
            <li><b>Wind:</b> check the forecast. Afternoons are windier, so go out early.</li>
            <li><b>Route:</b> trace it on the chart. Where does it cross ship areas? What's shallow?</li>
            <li><b>Radio:</b> VHF on 16 (emergencies), and listen to 14 (ship traffic).</li>
            <li><b>On the water:</b> look all the way around every 30 seconds. Pass behind ships. When in doubt,
              slow down.</li>
          </ol>
          <p>Now try it: go to <b>Explore → Plan a route</b>, click a trip from Pier 40, and see what it warns you about.</p>
          <div class="row"><button id="goPlan">Plan a trip from Pier 40 →</button></div>`,
      },
    ],
  },
];

// ------------------------------------------------------------------ state
const LS = 'sfbay-learn-v1';
const learnState = (() => { try { return JSON.parse(localStorage.getItem(LS)) || { done: {} }; } catch { return { done: {} }; } })();
const saveLearn = () => { try { localStorage.setItem(LS, JSON.stringify(learnState)); } catch { /* ignore */ } };
let cur = null; // {li, si}
const learnLayer = L.layerGroup().addTo(map);
const learnBox = document.getElementById('learn');

function setLayersFor(step) {
  const want = Object.assign({ chart: false, currents: false, ships: false, lanes: false, channels: false, ferries: false, zones: false,
                               buoys: false, hazards: false, areas: false }, step.layers || {});
  document.querySelectorAll('[data-layer]').forEach(cb => { cb.checked = !!want[cb.dataset.layer]; });
  syncLayers();
}

function pulse(ll, label, color = '#ffffff') {
  const m = L.marker(ll, { pane: 'shipP', interactive: false,
    icon: L.divIcon({ className: 'pulse-ico', iconSize: [40, 40], iconAnchor: [20, 20],
      html: `<div class="pulse" style="--c:${color}"></div>` }) });
  if (label) m.bindTooltip(label, { permanent: true, direction: 'right', offset: [16, 0], className: 'learn-tip' });
  return m;
}

function boatMarker(b) {
  const shape = b.sail
    ? `<path d="M0,-12 L5,-2 L4,10 L-4,10 L-5,-2Z" fill="${b.col}" stroke="#fff" stroke-width="1"/><path d="M0,-6 L0,7 L6,5Z" fill="#fff" opacity=".9"/>`
    : `<path d="M0,-12 L5,-2 L4,10 L-4,10 L-5,-2Z" fill="${b.col}" stroke="#fff" stroke-width="1"/><rect x="-2.5" y="-1" width="5" height="5" fill="#fff" opacity=".8"/>`;
  const m = L.marker(b.ll, { pane: 'shipP', interactive: false,
    icon: L.divIcon({ className: 'ship-ico', iconSize: [34, 34], iconAnchor: [17, 17],
      html: `<svg width="34" height="34" viewBox="-17 -17 34 34" style="transform:rotate(${b.hdg}deg)">${shape}
             <path d="M0,-13 L0,-17" stroke="${b.col}" stroke-width="2"/></svg>` }) });
  m.bindTooltip(b.label, { permanent: true, direction: 'right', offset: [14, 0], className: 'learn-tip' });
  // heading line
  const end = turf.destination([b.ll[1], b.ll[0]], 0.25, b.hdg, { units: 'kilometers' }).geometry.coordinates;
  const line = L.polyline([b.ll, [end[1], end[0]]], { pane: 'shipP', color: b.col, weight: 2, dashArray: '4 4', interactive: false });
  return [m, line];
}

function drawPath(p) {
  const out = [L.polyline(p.pts, { pane: 'shipP', color: p.color, weight: 5, opacity: 0.95, interactive: false })];
  const a = p.pts[p.pts.length - 2], b = p.pts[p.pts.length - 1];
  const brg = turf.bearing([a[1], a[0]], [b[1], b[0]]);
  out.push(L.marker(b, { pane: 'shipP', interactive: false,
    icon: L.divIcon({ className: 'ship-ico', iconSize: [26, 26], iconAnchor: [13, 13],
      html: `<svg width="26" height="26" viewBox="-13 -13 26 26" style="transform:rotate(${brg}deg)"><path d="M0,-12 L9,6 L-9,6Z" fill="${p.color}" stroke="#fff" stroke-width="1.5"/></svg>` }) }));
  if (p.label && p.label !== '?') out[0].bindTooltip(p.label, { permanent: true, direction: 'left', className: 'learn-tip' });
  return out;
}

function renderLessonList() {
  stopAnim();
  const n = LESSONS.filter(l => learnState.done[l.id]).length;
  learnBox.innerHTML = `
    <section>
      <p class="lead">A short course on the water you'll actually boat in, in the order that matters for your safety.
        Each lesson takes about 2 minutes.</p>
      <div class="progress"><div style="width:${n / LESSONS.length * 100}%"></div></div>
      <div class="muted small">${n} of ${LESSONS.length} complete</div>
    </section>
    <section class="lessons">${LESSONS.map((l, i) => `
      <button class="lesson ${learnState.done[l.id] ? 'done' : ''}" data-li="${i}">
        <span class="num">${learnState.done[l.id] ? '✓' : i + 1}</span>
        <span><b>${l.title}</b><br><span class="muted small">${l.tag}</span></span>
      </button>`).join('')}
    </section>`;
  learnBox.querySelectorAll('[data-li]').forEach(b => b.onclick = () => openStep(+b.dataset.li, 0));
  learnLayer.clearLayers();
}

function openStep(li, si) {
  cur = { li, si };
  const lesson = LESSONS[li], step = lesson.steps[si];
  learnLayer.clearLayers();
  setLayersFor(step);
  if (step.view) map.flyTo([step.view[0], step.view[1]], step.view[2], { duration: 1.2 });
  (step.marks || []).forEach(m => pulse(m.ll, m.label, m.color).addTo(learnLayer));
  (step.scene || []).forEach(b => boatMarker(b).forEach(x => x.addTo(learnLayer)));
  if (!step.anim) (step.paths || []).forEach(p => drawPath(p).forEach(x => x.addTo(learnLayer)));
  stopAnim();
  if (step.anim) setTimeout(() => { if (cur && cur.li === li && cur.si === si) SCENES[step.anim](); }, 1300);
  const last = si === lesson.steps.length - 1;
  learnBox.innerHTML = `
    <section>
      <div class="crumbs"><button id="lBack">← All lessons</button>
        <span class="muted small">Lesson ${li + 1} · step ${si + 1} of ${lesson.steps.length}</span></div>
      <h3>${lesson.title}</h3>
      <div class="lbody">${step.html || ''}</div>
      ${step.quiz ? `<div class="quiz"><div class="q">${step.quiz.q}</div>
        ${step.quiz.options.map((o, i) => `<button class="opt" data-oi="${i}">${o.t}</button>`).join('')}
        <div class="why"></div></div>` : ''}
      <div class="row nav">
        ${si > 0 ? '<button id="lPrev">← Back</button>' : ''}
        <button id="lNext" class="primary" ${step.quiz ? 'disabled' : ''}>${last ? (li < LESSONS.length - 1 ? 'Finish → next lesson' : 'Finish') : 'Next →'}</button>
      </div>
    </section>`;
  learnBox.scrollTop = 0;
  document.getElementById('panel').scrollTop = 0;
  document.getElementById('lBack').onclick = renderLessonList;
  const prev = document.getElementById('lPrev');
  if (prev) prev.onclick = () => openStep(li, si - 1);
  document.getElementById('lNext').onclick = () => {
    if (!last) return openStep(li, si + 1);
    learnState.done[lesson.id] = true; saveLearn();
    if (li < LESSONS.length - 1) openStep(li + 1, 0); else renderLessonList();
  };
  if (step.quiz) {
    learnBox.querySelectorAll('.opt').forEach(b => b.onclick = () => {
      const o = step.quiz.options[+b.dataset.oi];
      b.classList.add(o.ok ? 'right' : 'wrong');
      const why = learnBox.querySelector('.why');
      why.innerHTML = `<b class="${o.ok ? 'ok' : 'bad'}">${o.ok ? 'Correct.' : 'Not quite.'}</b> ${o.why}`;
      if (o.ok) {
        document.getElementById('lNext').disabled = false;
        learnBox.querySelectorAll('.opt').forEach(x => x.disabled = true);
      }
    });
  }
  learnBox.querySelectorAll('[data-jump]').forEach(b => b.onclick = () => jumpTide(b.dataset.jump));
  const gp = document.getElementById('goPlan');
  if (gp) gp.onclick = () => {
    learnState.done[lesson.id] = true; saveLearn();
    showTab('explore');
    ['lanes', 'channels', 'currents', 'buoys', 'hazards', 'ferries', 'zones'].forEach(k => { document.querySelector(`[data-layer=${k}]`).checked = true; });
    syncLayers();
    map.flyTo(P40, 14);
    if (!route.drawing) document.getElementById('routeBtn').click();
    document.getElementById('routeBtn').scrollIntoView({ behavior: 'smooth' });
  };
}

function jumpTide(kind) {
  const out = document.getElementById('jumpOut');
  if (kind === 'now') { slider.value = 0; onTime(); out.textContent = ''; return; }
  const st = CUR.stations.find(s => s.id === 'SFB1201');
  if (!st?.data) { out.textContent = 'Currents are still loading. Try again in a few seconds.'; return; }
  const t0 = selTime() + 60000;
  const evs = eventsAfter(st, t0, 12);
  const ev = evs.find(e => kind === 'slack' ? e.type === 'slack'
    : e.type === 'max' && ((e.dir > 160 && e.dir < 340) === (kind === 'ebb')));
  if (!ev) { out.textContent = 'No such event in the prediction window.'; return; }
  slider.value = Math.max(+slider.min, Math.min(+slider.max, Math.round((ev.t - baseNow) / 600000) * 10));
  onTime();
  out.innerHTML = `Showing <b>${fmtTime(ev.t)}</b>: ${kind === 'slack' ? 'slack at the Gate' : `max ${kind}, ${ev.spd.toFixed(1)} kn at the Gate`}.
    Look at how the arrows near you changed.`;
}

// ------------------------------------------------------------------ tabs
function showTab(which) {
  document.getElementById('learn').style.display = which === 'learn' ? '' : 'none';
  document.getElementById('explore').style.display = which === 'explore' ? '' : 'none';
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('on', t.dataset.tab === which));
  if (which === 'learn') { if (!cur) renderLessonList(); } else { stopAnim(); learnLayer.clearLayers(); }
}
document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
  if (t.dataset.tab === 'learn') { cur = null; }
  showTab(t.dataset.tab);
});

// ------------------------------------------------------------------ animations
/* Each animated vessel follows a polyline at a real speed (knots), sped up by `scale`
   (simulated seconds per real second). Tooltips can change with progress along the path. */
const ANIM = { raf: null, items: [], t0: 0, scale: 1, clock: null };

const HARBOR = {
  northIn: [[37.7834, -122.3800], [37.7829, -122.3818], [37.7827, -122.3833], [37.7826, -122.3845],
            [37.7819, -122.3847], [37.7812, -122.3851], [37.7808, -122.3858]],
  southIn: [[37.7764, -122.3832], [37.7769, -122.3852], [37.7774, -122.3860], [37.7779, -122.3858],
            [37.7784, -122.3852], [37.7790, -122.3847], [37.7795, -122.3852]],
};
const SHIP_ROUTES = {
  oaklandIn: [[37.773, -122.62], [37.784, -122.564], [37.791, -122.543], [37.799, -122.513], [37.808, -122.497],
              [37.812, -122.478], [37.8195, -122.445], [37.8222, -122.428], [37.819, -122.405], [37.809, -122.390],
              [37.8015, -122.362], [37.8035, -122.345], [37.7995, -122.330]],
  oaklandOut: [[37.7985, -122.328], [37.8045, -122.346], [37.8055, -122.362], [37.813, -122.388], [37.822, -122.404],
               [37.8305, -122.414], [37.8315, -122.428], [37.8278, -122.445], [37.8195, -122.468], [37.811, -122.505],
               [37.797, -122.539], [37.788, -122.564], [37.776, -122.615]],
  richmondIn: [[37.776, -122.60], [37.787, -122.56], [37.799, -122.512], [37.810, -122.49], [37.814, -122.475],
               [37.822, -122.448], [37.826, -122.432], [37.833, -122.412], [37.846, -122.396], [37.872, -122.386],
               [37.900, -122.392], [37.910, -122.400]],
};
const FERRY_PICK = [
  ['Sausalito - San Francisco Ferry Building', 26], ['Larkspur - San Francisco Ferry Building', 34],
  ['Oakland Jack London Square - San Francisco Ferry Building', 28], ['Alameda Main Street - San Francisco Ferry Building', 28],
  ['Vallejo - San Francisco Ferry Building', 34], ['Tiburon - San Francisco Ferry Building', 26],
  ['Richmond - San Francisco Ferry Building', 30], ['Treasure Island - San Francisco Ferry Building', 20],
  ['Chase Center Pier 48 1/2 - Oakland Jack London Square (Seasonal)', 28],
];

function ferryRoutes() {
  const fc = window.FERRIES;
  if (!fc) return [];
  return FERRY_PICK.map(([name, kn], i) => {
    const f = fc.features.find(x => x.properties.name === name);
    return f && { path: f.geometry.coordinates.map(([lo, la]) => [la, lo]), kn, kind: 'ferry', pingpong: true,
                  offset: i * 0.37, label: i < 3 ? 'ferry' : null };
  }).filter(Boolean);
}

function vesselSvg(kind, color) {
  if (kind === 'ship') return `<svg width="46" height="46" viewBox="-23 -23 46 46"><path d="M0,-21 L5,-12 L5,19 L-5,19 L-5,-12Z" fill="${color}" stroke="#0b121b" stroke-width="1.2"/>
    <rect x="-3.5" y="-9" width="7" height="20" fill="#c0392b" opacity=".85"/><rect x="-4" y="13" width="8" height="4" fill="#fff"/></svg>`;
  if (kind === 'ferry') return `<svg width="26" height="26" viewBox="-13 -13 26 26"><path d="M0,-11 L5,-3 L5,10 L-5,10 L-5,-3Z" fill="${color}" stroke="#fff" stroke-width="1.2"/>
    <rect x="-3" y="-2" width="6" height="8" fill="#fff" opacity=".85"/></svg>`;
  if (kind === 'sail') return `<svg width="20" height="20" viewBox="-10 -10 20 20"><path d="M0,-9 L4,-1 L3,8 L-3,8 L-4,-1Z" fill="${color}" stroke="#fff" stroke-width="1"/>
    <path d="M0,-5 L0,6 L5,4Z" fill="#fff"/></svg>`;
  // small powerboat, with its side lights: red = port (left), green = starboard (right)
  return `<svg width="30" height="30" viewBox="-15 -15 30 30"><path d="M0,-13 L6,-3 L5,11 L-5,11 L-6,-3Z" fill="${color}" stroke="#fff" stroke-width="1.4"/>
    <rect x="-3" y="0" width="6" height="6" fill="#fff" opacity=".85"/>
    <circle cx="-4.6" cy="-3" r="1.9" fill="#ff4d4d"/><circle cx="4.6" cy="-3" r="1.9" fill="#2fcf6f"/></svg>`;
}

function prepPath(pts) {
  const cum = [0];
  for (let i = 1; i < pts.length; i++)
    cum.push(cum[i - 1] + turf.distance([pts[i - 1][1], pts[i - 1][0]], [pts[i][1], pts[i][0]], { units: 'nauticalmiles' }));
  return cum;
}
function pointAt(pts, cum, d) {
  let i = 1;
  while (i < cum.length - 1 && cum[i] < d) i++;
  const f = (d - cum[i - 1]) / ((cum[i] - cum[i - 1]) || 1);
  const a = pts[i - 1], b = pts[i];
  return { ll: [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f],
           brg: turf.bearing([a[1], a[0]], [b[1], b[0]]), frac: d / cum[cum.length - 1] };
}

function stopAnim() {
  if (ANIM.raf) cancelAnimationFrame(ANIM.raf);
  ANIM.raf = null; ANIM.items = [];
  ANIM.clock?.remove(); ANIM.clock = null;
}

function startAnim(defs, scale, note) {
  stopAnim();
  ANIM.scale = scale; ANIM.t0 = performance.now();
  const colors = { ship: '#9aa7b5', ferry: '#4fa3ff', sail: '#c58cff', small: '#f2a541', you: '#4fa3ff' };
  for (const d of defs) {
    const cum = prepPath(d.path);
    if (d.showPath !== false) L.polyline(d.path, { pane: 'lanesP', color: d.pathColor || colors[d.kind] || '#fff', weight: d.kind === 'ship' ? 3 : 2,
      opacity: 0.35, dashArray: '4 6', interactive: false }).addTo(learnLayer);
    const kind = d.kind === 'you' ? 'small' : d.kind;
    const m = L.marker(d.path[0], { pane: 'shipP', interactive: false,
      icon: L.divIcon({ className: 'ship-ico', iconSize: [10, 10], iconAnchor: [5, 5],
        html: `<div class="vess" style="position:absolute;left:5px;top:5px;transform:translate(-50%,-50%)">${vesselSvg(kind, d.color || colors[d.kind])}</div>` }) }).addTo(learnLayer);
    if (d.label || d.notes) m.bindTooltip(d.label || '', { permanent: true, direction: 'right', offset: [14, 0], className: 'learn-tip' });
    ANIM.items.push({ d, cum, m, lastNote: null });
  }
  const box = L.DomUtil.create('div', 'anim-clock', map.getContainer());
  box.innerHTML = note;
  ANIM.clock = box;
  const tick = now => {
    const simSec = (now - ANIM.t0) / 1000 * ANIM.scale;
    for (const it of ANIM.items) {
      const total = it.cum[it.cum.length - 1];
      const pause = it.d.pause ?? 0.15;           // fraction of the trip spent waiting at the ends
      const travel = total + total * pause;
      let dist = ((simSec * it.d.kn / 3600) + (it.d.offset || 0) * travel) % (it.d.pingpong ? travel * 2 : travel);
      let reverse = false;
      if (it.d.pingpong && dist > travel) { dist -= travel; reverse = true; }
      dist = Math.min(dist, total);
      const pts = reverse ? [...it.d.path].reverse() : it.d.path;
      const cum = reverse ? it.cumR || (it.cumR = prepPath(pts)) : it.cum;
      const p = pointAt(pts, cum, dist);
      it.m.setLatLng(p.ll);
      const el = it.m.getElement()?.querySelector('.vess');
      if (el) el.style.transform = `translate(-50%,-50%) rotate(${p.brg}deg)`;
      if (it.d.notes) {
        const n = [...it.d.notes].reverse().find(x => p.frac >= x.at);
        const txt = n ? n.text : '';
        if (txt !== it.lastNote) { it.m.setTooltipContent(txt); it.lastNote = txt; }
      }
    }
    ANIM.raf = requestAnimationFrame(tick);
  };
  ANIM.raf = requestAnimationFrame(tick);
}

const SCENES = {
  harborIn: () => startAnim([
    { path: HARBOR.northIn, kn: 4, kind: 'you', pause: 0.35, notes: [
      { at: 0, text: 'coming home → north door' }, { at: 0.45, text: 'turn south into the gap' },
      { at: 0.6, text: 'red 2 on my RIGHT ✓  green 1 on my left' }, { at: 0.85, text: 'inside: slow, no wake' }] },
    { path: HARBOR.southIn, kn: 4, kind: 'you', offset: 0.5, pause: 0.35, color: '#7ce38b', notes: [
      { at: 0, text: 'coming home → south door' }, { at: 0.5, text: 'red 2 on my RIGHT ✓  green 1 on my left' },
      { at: 0.8, text: 'inside: slow, no wake' }] },
  ], 10, 'Animation sped up 10× · boats at 4 knots (harbor speed)'),
  harborOut: () => startAnim([
    { path: [...HARBOR.northIn].reverse(), kn: 4, kind: 'you', pause: 0.35, color: '#f2a541', notes: [
      { at: 0, text: 'leaving → north door' }, { at: 0.2, text: 'red 2 on my LEFT ✓  green 1 on my right' },
      { at: 0.5, text: 'out: look both ways for traffic' }] },
    { path: [...HARBOR.southIn].reverse(), kn: 4, kind: 'you', offset: 0.5, pause: 0.35, color: '#f2a541', notes: [
      { at: 0, text: 'leaving → south door' }, { at: 0.25, text: 'red 2 on my LEFT ✓  green 1 on my right' },
      { at: 0.5, text: 'out into China Basin' }] },
  ], 10, 'Animation sped up 10× · boats at 4 knots (harbor speed)'),
  ships: () => startAnim([
    { path: SHIP_ROUTES.oaklandIn, kn: 12, kind: 'ship', label: 'container ship → Oakland', pause: 0.05 },
    { path: SHIP_ROUTES.oaklandOut, kn: 12, kind: 'ship', label: 'leaving Oakland → sea', offset: 0.45, pause: 0.05 },
    { path: SHIP_ROUTES.richmondIn, kn: 11, kind: 'ship', label: 'tanker → Richmond', offset: 0.7, pause: 0.05 },
  ], 120, 'Sped up 120× (1 second = 2 minutes) · ships at 11–12 knots · routes simplified'),
  ferries: () => startAnim([
    ...ferryRoutes(),
    { path: SHIP_ROUTES.oaklandIn, kn: 12, kind: 'ship', label: 'ship', pause: 0.05, offset: 0.62 },
  ], 90, 'Sped up 90× · ferries at 20–34 knots, ships at 12 · ferries on their real routes'),
  everything: () => startAnim([
    ...ferryRoutes().map(f => ({ ...f, label: null })),
    { path: SHIP_ROUTES.oaklandIn, kn: 12, kind: 'ship', label: 'ship → Oakland', pause: 0.05, offset: 0.55 },
    { path: SHIP_ROUTES.oaklandOut, kn: 12, kind: 'ship', label: 'ship → sea', pause: 0.05, offset: 0.1 },
    { path: SHIP_ROUTES.richmondIn, kn: 11, kind: 'ship', pause: 0.05, offset: 0.8 },
    { path: [[37.840, -122.470], [37.830, -122.445], [37.846, -122.430], [37.836, -122.405]], kn: 6, kind: 'sail', pingpong: true, showPath: false },
    { path: [[37.828, -122.460], [37.842, -122.448], [37.832, -122.425]], kn: 6, kind: 'sail', pingpong: true, offset: 0.4, showPath: false },
    { path: [[37.852, -122.440], [37.838, -122.420], [37.850, -122.400]], kn: 5, kind: 'sail', pingpong: true, offset: 0.7, showPath: false, label: 'sailboats in the Slot' },
    { path: [[37.7784, -122.3852], [37.7770, -122.3835], [37.7700, -122.3800], [37.7600, -122.3790], [37.7520, -122.3780]], kn: 6,
      kind: 'you', pingpong: true, label: 'you: southern waterfront', pause: 0.2 },
  ], 90, 'A typical afternoon, sped up 90× · routes simplified'),
};

showTab('learn');
