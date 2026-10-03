"""
Rules of the Road — a 3Blue1Brown-style explainer for boating on San Francisco Bay.

Render all scenes:   .venv/bin/manim -qh -a boating.py
Narration is generated with ElevenLabs (key in .env) and cached in ./audio.
"""
from manim import *
import numpy as np
import hashlib, os, subprocess, wave, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "audio")
VOICE_ID = "nPczCjzI2devNBz1zQrb"   # ElevenLabs "Brian"
TTS_MODEL = "eleven_multilingual_v2"
FONT = "Avenir Next"

WATER = "#0D1824"
config.background_color = WATER

RED_L = "#FF5A5A"      # port light
GREEN_L = "#3DDC84"    # starboard light
YOU_C = "#4FA3FF"
THEM_C = "#F2A541"
SHIP_C = "#8E9AAF"
GIVE_C = "#FF8A3D"
STAND_C = "#7CE38B"
CURRENT_C = "#2EC4B6"


# ---------------------------------------------------------------- helpers
def T(s, size=34, color=WHITE, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def _eleven_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key and os.path.exists(os.path.join(HERE, ".env")):
        for line in open(os.path.join(HERE, ".env")):
            if line.startswith("ELEVENLABS_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        raise RuntimeError("Set ELEVENLABS_API_KEY (env or .env)")
    return key


def tts(text):
    os.makedirs(AUDIO, exist_ok=True)
    h = hashlib.md5((VOICE_ID + TTS_MODEL + text).encode()).hexdigest()[:12]
    wav = os.path.join(AUDIO, f"el_{h}.wav")
    if not os.path.exists(wav):
        import json, urllib.request
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
            data=json.dumps({"text": text, "model_id": TTS_MODEL,
                             "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}).encode(),
            headers={"xi-api-key": _eleven_key(), "Content-Type": "application/json"})
        mp3 = wav[:-4] + ".mp3"
        with urllib.request.urlopen(req) as r, open(mp3, "wb") as f:
            f.write(r.read())
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mp3,
                        "-ar", "44100", "-ac", "2", wav], check=True)
        os.remove(mp3)
    with contextlib.closing(wave.open(wav)) as f:
        dur = f.getnframes() / f.getframerate()
    return wav, dur


class VScene(Scene):
    @contextlib.contextmanager
    def voice(self, text, pad=0.35):
        """Play narration; animations inside the block run alongside it, then
        we wait out whatever narration is left."""
        wav, dur = tts(text)
        self.add_sound(wav)
        t0 = self.renderer.time
        yield dur
        rem = dur + pad - (self.renderer.time - t0)
        if rem > 0.02:
            self.wait(rem)

    def horn(self, pattern):
        """'s' = short blast, 'l' = prolonged blast. Returns total duration."""
        t = 0.0
        for c in pattern:
            f = "short.wav" if c == "s" else "long.wav"
            self.add_sound(os.path.join(AUDIO, f), time_offset=t)
            t += 0.6 if c == "s" else 2.1
        return t

    def chapter(self, num, title):
        n = T(f"Part {num}", 30, GREY_B)
        t = T(title, 54, weight=BOLD)
        g = VGroup(n, t).arrange(DOWN, buff=0.3)
        self.play(FadeIn(n, shift=UP * 0.2), Write(t), run_time=1.2)
        self.wait(0.8)
        self.play(FadeOut(g), run_time=0.6)

    def clear_all(self, run_time=0.8):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self.clear()


class Boat(VGroup):
    """Top-down boat. Local frame: bow points +x, port side is +y."""

    def __init__(self, color=YOU_C, length=0.8, kind="power", lights=True,
                 boom_side=1, width_ratio=0.4, **kw):
        super().__init__(**kw)
        L, W = length, length * width_ratio
        self.L = L
        self.pivot = Dot(ORIGIN, radius=0.001).set_opacity(0)
        pts = [[L / 2, 0, 0], [L * 0.12, W / 2, 0], [-L / 2, W * 0.4, 0],
               [-L / 2, -W * 0.4, 0], [L * 0.12, -W / 2, 0]]
        if kind == "ship":
            pts = [[L / 2, 0, 0], [L * 0.38, W / 2, 0], [-L / 2, W / 2, 0],
                   [-L / 2, -W / 2, 0], [L * 0.38, -W / 2, 0]]
        hull = Polygon(*[np.array(p, dtype=float) for p in pts], color=WHITE,
                       stroke_width=1.5, fill_color=color, fill_opacity=1)
        hull.round_corners(radius=L * 0.04)
        self.hull = hull
        self.add(self.pivot, hull)
        if kind == "power":
            self.add(RoundedRectangle(width=L * 0.3, height=W * 0.5, corner_radius=W * 0.1,
                                      stroke_width=0, fill_color=WHITE,
                                      fill_opacity=0.7).move_to([-L * 0.1, 0, 0]))
        elif kind == "sail":
            mast = np.array([L * 0.1, 0, 0])
            clew = np.array([-L * 0.45, boom_side * W * 0.55, 0])
            sail = ArcBetweenPoints(mast, clew, angle=-boom_side * 0.5,
                                    color=WHITE, stroke_width=3)
            self.add(sail, Dot(mast, radius=L * 0.035, color=WHITE))
        elif kind == "ship":
            boxes = VGroup(*[
                Rectangle(width=L * 0.07, height=W * 0.8, stroke_width=0.5,
                          stroke_color=BLACK, fill_opacity=1,
                          fill_color=[RED_E, BLUE_E, GREEN_E, GOLD_E, TEAL_E][i % 5])
                .move_to([L * 0.3 - i * L * 0.08, 0, 0]) for i in range(7)])
            bridge = Rectangle(width=L * 0.08, height=W * 1.0, stroke_width=0,
                               fill_color=WHITE, fill_opacity=0.9).move_to([-L * 0.38, 0, 0])
            self.add(boxes, bridge)
        elif kind == "kayak":
            pass
        if lights:
            r = max(L * 0.045, 0.025)
            self.port_light = Dot([L * 0.08, W * 0.34, 0], radius=r, color=RED_L)
            self.stbd_light = Dot([L * 0.08, -W * 0.34, 0], radius=r, color=GREEN_L)
            self.add(self.port_light, self.stbd_light)
        self.heading = 0.0

    @property
    def pos(self):
        return self.pivot.get_center()

    def place(self, p, h=None):
        if h is not None and abs(h - self.heading) > 1e-9:
            self.rotate(h - self.heading, about_point=self.pos)
            self.heading = h
        self.shift(v3(p) - self.pos)
        return self


def v3(p):
    p = np.array(p, dtype=float)
    return np.append(p, 0.0) if p.shape == (2,) else p


def seg(a, b):
    a, b = v3(a), v3(b)
    return lambda t: a + (b - a) * t


def smooth_path(*pts):
    return VMobject().set_points_smoothly([np.array(p, dtype=float) for p in pts])


def drive(boat, path, run_time=3.0, rate_func=linear, heading=None):
    pf = path if callable(path) else path.point_from_proportion

    def upd(m, a):
        p = pf(a)
        if heading is not None:
            h = heading(a) if callable(heading) else heading
        else:
            e = 1e-3
            d = pf(min(1, a + e)) - pf(max(0, a - e))
            if np.linalg.norm(d) < 1e-9:
                h = m.heading
            else:
                h = np.arctan2(d[1], d[0])
                h = m.heading + ((h - m.heading + PI) % TAU - PI)
        m.place(p, h)

    return UpdateFromAlphaFunc(boat, upd, run_time=run_time, rate_func=rate_func)


def wake(boat, color=WHITE, t=1.4):
    return TracedPath(boat.pivot.get_center, stroke_color=color, stroke_width=2,
                      stroke_opacity=0.5, dissipating_time=t)


def tag(text, color, boat, direction=UP, buff=0.35, size=26):
    lab = T(text, size, color, weight=BOLD)
    lab.add_updater(lambda m: m.next_to(boat.pos, direction, buff=buff + boat.L * 0.3))
    return lab


# ---------------------------------------------------------------- scenes
class S1_Intro(VScene):
    def construct(self):
        traffic = [
            (Boat(SHIP_C, 3.2, "ship", lights=False, width_ratio=0.16), [-9, 2.6], [9, 2.0], 0),
            (Boat(WHITE, 1.0, "power"), [8, -3.8], [-8, 1.2], 0),
            (Boat(THEM_C, 0.7, "sail", boom_side=-1), [-7, -2.5], [2, 0.5], 0),
            (Boat(STAND_C, 0.7, "sail", boom_side=1), [6, 3.8], [1, -3.8], 0),
            (Boat(YELLOW, 0.45, "kayak", lights=False, width_ratio=0.22), [-3, -4.2], [-1.5, 3.8], 0),
            (Boat(YOU_C, 0.8, "power"), [2.5, -4.3], [-4, 3.2], 0),
        ]
        for b, a, z, _ in traffic:
            b.place(a, np.arctan2(z[1] - a[1], z[0] - a[0]))
            self.add(b, wake(b, b.hull.get_fill_color()))
        you = traffic[-1][0]
        you_lab = tag("you", YOU_C, you, RIGHT, 0.2)
        self.add(you_lab)

        with self.voice("There are no lanes painted on the water. No stop signs, no traffic "
                        "lights, no curbs. And yet, on any given afternoon on San Francisco Bay, "
                        "container ships, ferries, sailboats, kayaks, and you, all share the same "
                        "patch of water, and almost never collide.") as d:
            self.play(*[drive(b, seg(a, z), run_time=d) for b, a, z, _ in traffic])
        self.clear_all()

        title = T("The Rules of the Road", 64, weight=BOLD)
        sub = T("what actually matters on San Francisco Bay", 32, GREY_A)
        VGroup(title, sub).arrange(DOWN, buff=0.35)
        with self.voice("That works because everyone follows the same small set of rules: "
                        "the Navigation Rules, or, as boaters call them, the rules of the road. "
                        "There are dozens of them, but you don't need to memorize them all. "
                        "You need to really understand a handful of ideas."):
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(sub, shift=UP * 0.2))
        self.play(VGroup(title, sub).animate.scale(0.6).to_edge(UP))

        parts = ["Am I on a collision course?", "Who gives way?", "The pecking order",
                 "Big ships rule the Bay", "Reading the channel", "Current and wind"]
        items = VGroup(*[
            VGroup(T(f"{i + 1}", 30, YELLOW, weight=BOLD), T(p, 30)).arrange(RIGHT, buff=0.35)
            for i, p in enumerate(parts)]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        items.next_to(title, DOWN, buff=0.7).shift(DOWN * 0.15)
        with self.voice("Here's the plan. We'll start with geometry: how to tell if you're "
                        "about to hit someone. Then who has to move, and how. Then the pecking "
                        "order between different kinds of boats, why big ships always win on "
                        "the Bay, how to read channel markers, and finally the invisible forces "
                        "that make San Francisco special: current and wind.") as d:
            self.play(LaggedStart(*[FadeIn(it, shift=RIGHT * 0.3) for it in items],
                                  lag_ratio=0.5), run_time=d * 0.8)
        self.clear_all()


class S2_CollisionCourse(VScene):
    def construct(self):
        self.chapter(1, "Am I on a collision course?")

        C = np.array([-1.6, 1.3, 0])
        you0 = C + np.array([0, -4.4, 0])
        ang = 12 * DEGREES
        them0 = C + 5.6 * np.array([np.cos(ang), np.sin(ang), 0])
        Tt = 8.0
        you_p = lambda t: you0 + (C - you0) * t / Tt
        them_p = lambda t: them0 + (C - them0) * t / Tt

        you = Boat(YOU_C).place(you0, PI / 2)
        them = Boat(THEM_C).place(them0, np.arctan2(*(C - them0)[[1, 0]]))
        lab_y = tag("you", YOU_C, you, LEFT, 0.15)
        lab_t = tag("them", THEM_C, them, UP, 0.1)
        with self.voice("Before you worry about who has the right of way, figure out whether "
                        "there's any danger at all. Here's you, and here's another boat."):
            self.play(FadeIn(you), FadeIn(them), FadeIn(lab_y), FadeIn(lab_t))

        t = ValueTracker(0)
        you.add_updater(lambda m: m.place(you_p(t.get_value())))
        them.add_updater(lambda m: m.place(them_p(t.get_value())))
        sight = always_redraw(lambda: DashedLine(you.pos, them.pos, color=YELLOW,
                                                 stroke_width=3, dash_length=0.12))
        ghosts = VGroup()
        with self.voice("Draw a line between the two of you: the line of sight. Now let time run "
                        "forward, and every second, leave behind a copy of that line."):
            self.play(Create(sight))
            self.add(wake(you, YOU_C), wake(them, THEM_C))
            for k in range(1, 4):
                self.play(t.animate.set_value(k), run_time=1, rate_func=linear)
                g = Line(you.pos, them.pos, color=YELLOW, stroke_width=2, stroke_opacity=0.35)
                ghosts.add(g)
                self.add(g)
        with self.voice("Notice anything? Every copy is parallel. The direction from you to the "
                        "other boat, its bearing, never changes, while the distance keeps "
                        "shrinking. That's the signature of a collision course."):
            for k in range(4, 7):
                self.play(t.animate.set_value(k), run_time=1, rate_func=linear)
                g = Line(you.pos, them.pos, color=YELLOW, stroke_width=2, stroke_opacity=0.35)
                ghosts.add(g)
                self.add(g)
            self.play(t.animate.set_value(7.3), run_time=0.8, rate_func=linear)
            boom = Star(color=RED, fill_opacity=0.8).scale(0.45).move_to(C)
            self.play(GrowFromCenter(boom), Flash(C, color=RED))

        tri0 = Polygon(you0, them0, C, stroke_color=WHITE, stroke_width=2)
        tri1 = Polygon(you_p(3), them_p(3), C, stroke_color=WHITE, stroke_width=2)
        tri2 = Polygon(you_p(5.5), them_p(5.5), C, stroke_color=WHITE, stroke_width=2)
        with self.voice("Geometrically, you, the other boat, and the meeting point form a "
                        "triangle. As time passes, the triangle shrinks but keeps exactly the "
                        "same shape. Similar triangles, all the way down to zero."):
            self.play(Create(tri0))
            self.play(TransformFromCopy(tri0, tri1))
            self.play(TransformFromCopy(tri1, tri2))
        you.clear_updaters()
        them.clear_updaters()
        self.clear_all()

        # --- relative frame
        me = Boat(YOU_C).place([0, -2.6, 0], PI / 2)
        other_start = np.array([4.4, 2.0, 0])
        other = Boat(THEM_C).place(other_start, PI + 0.3)
        ttl = T("in your own frame of reference", 30, GREY_A).to_edge(UP)
        with self.voice("Here's another way to see it. Ride along with your own boat, so that, "
                        "to you, you're standing still. In that frame, the other boat isn't "
                        "crossing at all. It's sliding straight down the line of sight, right "
                        "at you.") as d:
            self.play(FadeIn(me), FadeIn(other), FadeIn(ttl))
            path = Line(other_start, me.pos + UP * 0.5)
            self.play(Create(DashedLine(other_start, me.pos, color=YELLOW, stroke_width=2)))
            self.play(drive(other, path, run_time=d - 3.5, heading=PI + 0.3),
                      rate_func=linear)
        self.clear_all()

        # --- bearing that drifts
        you0 = np.array([-1.6, -3.1, 0])
        them0 = C + 5.6 * np.array([np.cos(ang), np.sin(ang), 0])
        you_p = lambda t: you0 + (C - you0) * t / 8.0
        them_p = lambda t: them0 + (C - them0) * t / 4.9
        you = Boat(YOU_C).place(you0, PI / 2)
        them = Boat(THEM_C).place(them0, np.arctan2(*(C - them0)[[1, 0]]))
        t = ValueTracker(0)
        you.add_updater(lambda m: m.place(you_p(t.get_value())))
        them.add_updater(lambda m: m.place(them_p(t.get_value())))
        sight = always_redraw(lambda: DashedLine(you.pos, them.pos, color=YELLOW,
                                                 stroke_width=3, dash_length=0.12))
        self.add(you, them, sight, wake(you, YOU_C), wake(them, THEM_C))
        with self.voice("Now make the other boat a bit faster, and replay. This time the copies "
                        "fan out. The bearing drifts, and the boat crosses safely ahead of you. "
                        "Bearing drifting forward means it passes ahead; drifting aft means it "
                        "passes behind."):
            for k in range(1, 8):
                self.play(t.animate.set_value(k), run_time=0.9, rate_func=linear)
                self.add(Line(you.pos, them.pos, color=YELLOW, stroke_width=2, stroke_opacity=0.35))
        you.clear_updaters()
        them.clear_updaters()
        self.clear_all()

        rule = VGroup(T("steady bearing", 48, YELLOW, weight=BOLD), T("+", 48),
                      T("shrinking range", 48, YELLOW, weight=BOLD)).arrange(RIGHT, buff=0.3)
        eq = T("=  collision course", 48, RED, weight=BOLD).next_to(rule, DOWN, buff=0.4)
        tip = VGroup(
            T("On the water: hold your course and line the other boat up with", 28, GREY_A),
            T("a fixed point on your boat, or with the shoreline behind it.", 28, GREY_A),
            T("Frozen against the background while growing bigger?  Act.", 28, WHITE),
            T("Big ships: the bearing can drift a little and you can still hit.", 28, GREY_A),
        ).arrange(DOWN, buff=0.18).next_to(eq, DOWN, buff=0.8)
        VGroup(rule, eq, tip).move_to(ORIGIN)
        with self.voice("On the water, you don't need a compass for this. Hold a steady course, "
                        "and line the other boat up with something fixed on your own boat, like "
                        "a stanchion or a window frame, or watch the shoreline behind it. If it "
                        "stays frozen against that background while it grows bigger, you're on a "
                        "collision course. One caveat: a big ship is so long that the bearing can "
                        "drift a little and you can still hit it. Give big ships a huge margin.") as d:
            self.play(FadeIn(rule), FadeIn(eq, shift=UP * 0.2))
            self.play(LaggedStart(*[FadeIn(x) for x in tip], lag_ratio=0.8), run_time=d * 0.75)
        self.clear_all()


class S3_Roles(VScene):
    def construct(self):
        self.chapter(2, "Who gives way?")
        you = Boat(YOU_C).place([-1, -3.4, 0], PI / 2)
        them = Boat(THEM_C).place([5.5, 0.8, 0], PI)
        lg = tag("GIVE-WAY", GIVE_C, you, LEFT, 0.15)
        ls = tag("STAND-ON", STAND_C, them, UP, 0.15)
        with self.voice("Okay, so there's a risk of collision. Who does what? Here's a surprise: "
                        "the rules never actually say right of way. Instead, they give each boat a "
                        "job. One is the give-way vessel. The other is the stand-on vessel."):
            self.play(FadeIn(you), FadeIn(them))
            self.play(Write(lg))
            self.play(Write(ls))

        path_you = smooth_path([-1, -3.4, 0], [-1, -1.6, 0], [0.4, -0.6, 0], [1.6, 0.2, 0],
                               [1.9, 1.6, 0], [1.4, 3.6, 0])
        self.add(wake(you, YOU_C), wake(them, THEM_C))
        with self.voice("The give-way vessel has to keep well clear, and the rules say how: act "
                        "early, and make it big. A tiny course change nobody can see is almost "
                        "worse than nothing. Usually that means a clear turn to starboard, to your "
                        "right, passing behind the other boat. Or just slow way down.") as d:
            self.wait(1.5)
            self.play(drive(you, path_you, run_time=d - 1.5),
                      drive(them, seg([5.5, 0.8, 0], [-6.5, 0.8, 0]), run_time=d - 1.5))
        self.clear_all()

        cards = VGroup()
        for head, col, lines in [
            ("GIVE-WAY", GIVE_C, ["act early", "act big and obvious", "usually: turn right,",
                                  "pass behind, or slow down"]),
            ("STAND-ON", STAND_C, ["hold course and speed", "be predictable",
                                   "but if they don't act,", "you must"]),
        ]:
            box = RoundedRectangle(width=5.6, height=4.0, corner_radius=0.25, stroke_color=col)
            h = T(head, 40, col, weight=BOLD)
            body = VGroup(*[T(l, 28) for l in lines]).arrange(DOWN, buff=0.18)
            inner = VGroup(h, body).arrange(DOWN, buff=0.45).move_to(box)
            cards.add(VGroup(box, inner))
        cards.arrange(RIGHT, buff=0.7)
        with self.voice("The stand-on vessel's job matters just as much: hold your course and "
                        "speed. Be predictable, so the other boat can plan around you. Don't "
                        "swerve to be helpful. That's how two boats dodge right into each other."):
            self.play(FadeIn(cards[0], shift=UP * 0.3))
            self.play(FadeIn(cards[1], shift=UP * 0.3))
            self.play(Indicate(cards[1][1][1][:2], color=STAND_C))
        moral = T("Nobody ever has the right to hit anyone.", 36, YELLOW, weight=BOLD)
        moral.next_to(cards, DOWN, buff=0.5)
        with self.voice("But if it becomes clear that the give-way boat isn't doing its job, the "
                        "stand-on boat may act. And if a collision is about to happen, it must. "
                        "Nobody ever has the right to hit anyone."):
            self.play(Indicate(cards[1][1][1][2:], color=STAND_C))
            self.play(Write(moral))
        self.clear_all()


class S4_Encounters(VScene):
    def construct(self):
        ttl = T("Three encounters", 40, weight=BOLD).to_corner(UL)
        with self.voice("So how do you know which job is yours? For two powerboats, there are "
                        "only three situations."):
            self.play(Write(ttl))

        # --- head-on
        sub = T("1.  Head-on", 34, YELLOW).next_to(ttl, DOWN, aligned_edge=LEFT)
        you = Boat(YOU_C).place([-0.2, -3.6, 0], PI / 2)
        them = Boat(THEM_C).place([0.2, 2.4, 0], -PI / 2)
        self.play(FadeIn(sub), FadeIn(you), FadeIn(them))
        self.add(wake(you, YOU_C), wake(them, THEM_C))
        p1 = smooth_path([-0.2, -3.6, 0], [-0.2, -2.4, 0], [0.9, -1.2, 0], [1.3, 0.4, 0], [1.3, 2.4, 0])
        p2 = smooth_path([0.2, 2.4, 0], [0.2, 1.2, 0], [-0.9, 0.0, 0], [-1.3, -1.6, 0], [-1.3, -3.8, 0])
        with self.voice("One: head on. If you're meeting nearly bow to bow, nobody is stand-on. "
                        "Both of you turn to starboard, and you pass port side to port side. "
                        "Just like cars on an American road: keep right. At night, the giveaway "
                        "is seeing both their red and green lights at the same time.") as d:
            self.play(drive(you, p1, run_time=d * 0.7), drive(them, p2, run_time=d * 0.7))
        self.play(FadeOut(VGroup(sub, you, them)))
        self.clear()
        self.add(ttl)

        # --- crossing
        sub = T("2.  Crossing", 34, YELLOW).next_to(ttl, DOWN, aligned_edge=LEFT)
        you = Boat(YOU_C).place([-1.0, -3.4, 0], PI / 2)
        them = Boat(THEM_C).place([4.5, 0.2, 0], PI)
        lg = tag("give-way", GIVE_C, you, LEFT, 0.1)
        ls = tag("stand-on", STAND_C, them, UP, 0.1)
        with self.voice("Two: crossing. The boat that has the other on its own starboard side, "
                        "its right, is the give-way vessel. Put differently: the boat on the "
                        "right is stand-on."):
            self.play(FadeIn(sub), FadeIn(you), FadeIn(them))
            self.play(FadeIn(lg), FadeIn(ls))
            arc = Arrow(you.pos + RIGHT * 0.4, them.pos + LEFT * 0.5 + DOWN * 0.3,
                        color=GREY_B, stroke_width=3, path_arc=0.4)
            self.play(Create(arc))
        self.play(FadeOut(VGroup(sub, you, them, lg, ls, arc)))
        self.clear()

        # --- lights diagram
        big = Boat(GREY_D, 2.4).place(ORIGIN, PI / 2)
        R = 3.2
        g_sec = AnnularSector(inner_radius=0, outer_radius=R, start_angle=-22.5 * DEGREES,
                              angle=112.5 * DEGREES, fill_color=GREEN_L, fill_opacity=0.22,
                              stroke_width=0)
        r_sec = AnnularSector(inner_radius=0, outer_radius=R, start_angle=90 * DEGREES,
                              angle=112.5 * DEGREES, fill_color=RED_L, fill_opacity=0.22,
                              stroke_width=0)
        w_sec = AnnularSector(inner_radius=0, outer_radius=R, start_angle=202.5 * DEGREES,
                              angle=135 * DEGREES, fill_color=WHITE, fill_opacity=0.12,
                              stroke_width=0)
        lab_g = T("green\n112.5°", 26, GREEN_L).move_to(
            R * 0.68 * np.array([np.cos(30 * DEGREES), np.sin(30 * DEGREES), 0]))
        lab_r = T("red\n112.5°", 26, RED_L).move_to(
            R * 0.68 * np.array([np.cos(150 * DEGREES), np.sin(150 * DEGREES), 0]))
        lab_w = T("white stern light\n135°", 24, WHITE).move_to(R * 0.7 * DOWN)
        beam = DashedLine(LEFT * R, RIGHT * R, color=GREY_B, stroke_width=1.5)
        with self.voice("There's a lovely trick for remembering this, built right into the boats. "
                        "Every boat carries a red light on its port side, and a green light on "
                        "its starboard side. Each one shines from dead ahead to a little past the "
                        "beam, 112 and a half degrees. A white stern light covers the rest.") as d:
            self.play(FadeIn(big))
            self.play(Indicate(big.port_light, scale_factor=3), Indicate(big.stbd_light, scale_factor=3))
            self.play(FadeIn(r_sec), FadeIn(g_sec), FadeIn(lab_r), FadeIn(lab_g))
            self.play(Create(beam))
            self.play(FadeIn(w_sec), FadeIn(lab_w))
        self.clear_all(0.6)

        you = Boat(YOU_C, 1.0).place([-1.5, -2.6, 0], PI / 2)
        them = Boat(THEM_C, 1.0).place([2.8, 0.6, 0], PI)
        lab = tag("you", YOU_C, you, LEFT, 0.1)
        self.play(FadeIn(you), FadeIn(them), FadeIn(lab))
        ray = Line(them.port_light.get_center(), you.pos, color=RED_L, stroke_width=3)
        glow = Dot(them.port_light.get_center(), radius=0.22, color=RED_L).set_opacity(0.5)
        stop = T("you see RED  →  STOP, give way", 34, RED_L, weight=BOLD).to_edge(UP)
        with self.voice("Now picture a boat crossing from your right. Which of its lights do you "
                        "see? Its red one. Red means stop: you give way."):
            self.play(GrowFromCenter(glow), Create(ray))
            self.play(Write(stop))
        self.play(FadeOut(VGroup(them, ray, glow, stop)))
        them = Boat(THEM_C, 1.0).place([-5.6, 0.6, 0], 0)
        ray = Line(them.stbd_light.get_center(), you.pos, color=GREEN_L, stroke_width=3)
        glow = Dot(them.stbd_light.get_center(), radius=0.22, color=GREEN_L).set_opacity(0.5)
        go = T("you see GREEN  →  GO, stand on", 34, GREEN_L, weight=BOLD).to_edge(UP)
        with self.voice("A boat crossing from your left shows you its green light. Green means go: "
                        "hold your course. And notice, it's looking at your red light. Everyone "
                        "gets the same answer."):
            self.play(FadeIn(them))
            self.play(GrowFromCenter(glow), Create(ray))
            self.play(Write(go))
            yr = Dot(you.port_light.get_center(), radius=0.22, color=RED_L).set_opacity(0.5)
            self.play(GrowFromCenter(yr))
        self.clear_all(0.6)

        # --- overtaking
        ttl = T("Three encounters", 40, weight=BOLD).to_corner(UL)
        sub = T("3.  Overtaking", 34, YELLOW).next_to(ttl, DOWN, aligned_edge=LEFT)
        slow = Boat(THEM_C).place([0, -2.4, 0], PI / 2)
        fast = Boat(YOU_C).place([0, -4.6, 0], PI / 2)
        sec = AnnularSector(inner_radius=0, outer_radius=2.0, start_angle=202.5 * DEGREES,
                            angle=135 * DEGREES, fill_color=WHITE, fill_opacity=0.12, stroke_width=0)
        sec.add_updater(lambda m: m.move_arc_center_to(slow.pos))
        self.add(ttl, sub, sec, slow, fast, wake(fast, YOU_C), wake(slow, THEM_C))
        lf = tag("overtaking: keeps clear", GIVE_C, fast, RIGHT, 0.1, 24)
        lsl = tag("holds course", STAND_C, slow, LEFT, 0.1, 24)
        self.add(lf, lsl)
        pf = smooth_path([0, -4.6, 0], [0.2, -3.6, 0], [1.3, -2.2, 0], [1.4, -0.4, 0], [0.4, 1.2, 0], [0, 2.2, 0])
        with self.voice("Three: overtaking. If you're coming up on a boat from behind, from "
                        "anywhere in its white stern-light sector, you're overtaking, and you "
                        "must keep clear, no matter what kinds of boats you are. And you stay "
                        "the give-way boat until you're well past and clear.") as d:
            self.play(drive(fast, pf, run_time=d * 0.9),
                      drive(slow, seg([0, -2.4, 0], [0, -0.4, 0]), run_time=d * 0.9))
        sec.clear_updaters()
        lf.clear_updaters()
        lsl.clear_updaters()
        self.clear_all(0.6)

        # --- the map in your head
        me = Boat(YOU_C, 1.2).place(ORIGIN + DOWN * 0.3, PI / 2)
        c = me.pos
        R = 3.0
        danger = AnnularSector(inner_radius=0.7, outer_radius=R, start_angle=-22.5 * DEGREES,
                               angle=112.5 * DEGREES, fill_color=YELLOW, fill_opacity=0.35,
                               stroke_width=0, arc_center=c)
        portz = AnnularSector(inner_radius=0.7, outer_radius=R, start_angle=90 * DEGREES,
                              angle=112.5 * DEGREES, fill_color=GREY_B, fill_opacity=0.18,
                              stroke_width=0, arc_center=c)
        sternz = AnnularSector(inner_radius=0.7, outer_radius=R, start_angle=202.5 * DEGREES,
                               angle=135 * DEGREES, fill_color=GREY_B, fill_opacity=0.08,
                               stroke_width=0, arc_center=c)
        dl = T("DANGER ZONE\nyou give way", 28, YELLOW, weight=BOLD).move_to(
            c + 4.6 * np.array([np.cos(35 * DEGREES), np.sin(35 * DEGREES), 0]))
        pl = T("they give way\n(you hold course)", 26, GREY_A).move_to(
            c + 4.8 * np.array([np.cos(145 * DEGREES), np.sin(145 * DEGREES), 0]))
        sl = T("overtaking boats\ngive way", 26, GREY_A).move_to(c + 2.5 * DOWN + RIGHT * 4.2)
        with self.voice("Put it all together, and you get a map you can carry in your head. "
                        "Anything ahead of you, or on your starboard side out to just past the "
                        "beam, is your danger zone. If it's crossing, avoiding it is your job. "
                        "Anything on your port side, or coming up from behind, should be avoiding "
                        "you. Hold your course, but watch them, and be ready to act.") as d:
            self.play(FadeIn(me))
            self.play(FadeIn(danger), Write(dl))
            self.wait(d * 0.3)
            self.play(FadeIn(portz), FadeIn(pl))
            self.play(FadeIn(sternz), FadeIn(sl))
        self.clear_all()


class S5_PeckingOrder(VScene):
    def construct(self):
        self.chapter(3, "The pecking order")
        rungs = [
            ("Not under command", "broken down, can't steer"),
            ("Restricted in ability to maneuver", "dredging, towing, laying cable, diving"),
            ("Constrained by draft", "deep ship stuck in a channel  (international rules)"),
            ("Fishing", "with nets or trawls, not someone holding a rod"),
            ("Sailing", "sails only. Engine on = you're a powerboat"),
            ("Power-driven", "probably you"),
        ]
        rows = VGroup()
        for i, (name, desc) in enumerate(rungs):
            col = interpolate_color(ManimColor(STAND_C), ManimColor(GIVE_C), i / 5)
            bar = RoundedRectangle(width=8.4, height=0.82, corner_radius=0.15,
                                   stroke_color=col, fill_color=col, fill_opacity=0.12)
            n = T(name, 28, col, weight=BOLD)
            d = T(desc, 22, GREY_A)
            VGroup(n, d).arrange(DOWN, aligned_edge=LEFT, buff=0.06).move_to(bar).align_to(
                bar, LEFT).shift(RIGHT * 0.3)
            rows.add(VGroup(bar, n, d))
        rows.arrange(DOWN, buff=0.14).move_to([-0.1, 0, 0])
        arrow = Arrow(rows.get_corner(DL) + LEFT * 0.4, rows.get_corner(UL) + LEFT * 0.4,
                      buff=0, color=WHITE, stroke_width=4)
        alab = T("less able to\nmaneuver", 24, GREY_A).next_to(arrow, LEFT, buff=0.2)
        with self.voice("Those encounters assume two similar boats. But not all boats are equally "
                        "able to get out of the way, so the rules add a pecking order. Each boat "
                        "keeps clear of the ones above it on this ladder."):
            self.play(GrowArrow(arrow), FadeIn(alab))
            self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in reversed(rows)],
                                  lag_ratio=0.25), run_time=2.5)
        with self.voice("At the top, a vessel not under command, one that's broken down and can't "
                        "steer. Then vessels restricted in their ability to maneuver: dredges, tugs "
                        "with a tow, boats supporting divers. Then, under international rules, deep "
                        "ships constrained by their draft. Then boats engaged in fishing. Then "
                        "sailboats. And at the bottom, powerboats. Probably you.") as d:
            for i, r in enumerate(rows):
                self.play(Indicate(r[1], color=r[1].get_color(), scale_factor=1.08),
                          run_time=d / 7)
        with self.voice("Two traps. A sailboat with its engine running, even with sails up, "
                        "counts as a powerboat. And someone trolling with a rod isn't 'engaged in "
                        "fishing' in the legal sense; that's about gear that actually limits how "
                        "a boat can move."):
            self.play(Indicate(rows[4], color=YELLOW))
            self.play(Indicate(rows[3], color=YELLOW))
        kayak = Boat(YELLOW, 0.6, "kayak", lights=False, width_ratio=0.22).place(
            [5.4, 1.4, 0], PI / 2)
        klab = T("paddlers:\nnot on the ladder,\nbut hard to see.\nGive them room.", 22, YELLOW)
        klab.next_to(kayak, DOWN, buff=0.3)
        with self.voice("Kayaks and paddleboards aren't really on this ladder, but they're slow, "
                        "low, and hard to see. Give them plenty of room. And the ladder has "
                        "exceptions. An overtaking boat always keeps clear, even a sailboat passing "
                        "you. And, most important on the Bay, the narrow channel rule, which we'll "
                        "get to in a moment."):
            self.play(FadeIn(kayak), FadeIn(klab))
        self.clear_all()

        # --- sail vs sail
        ttl = T("If you're both sailing", 40, weight=BOLD).to_edge(UP)
        wind = VGroup(*[Arrow(UP * 2.6 + RIGHT * x, UP * 1.6 + RIGHT * x, buff=0,
                              color=BLUE_B, stroke_width=4) for x in (-3, -1, 1, 3)])
        wl = T("wind", 26, BLUE_B).next_to(wind, RIGHT)
        # starboard tack: wind over starboard side, boom out to port.
        stb = Boat(STAND_C, 1.7, "sail", boom_side=1).place([2.6, -0.4, 0], 160 * DEGREES)
        prt = Boat(GIVE_C, 1.7, "sail", boom_side=-1).place([-2.6, -0.4, 0], 20 * DEGREES)
        sl = T("starboard tack\nstands on", 26, STAND_C).next_to(stb, DOWN, buff=0.5)
        pl = T("port tack\ngives way", 26, GIVE_C).next_to(prt, DOWN, buff=0.5)
        note = T("same tack?  the upwind boat keeps clear of the downwind boat", 26, GREY_A).to_edge(DOWN)
        with self.voice("One more pairing, in case you're ever on a sailboat. When two sailboats "
                        "meet, the one with the wind coming over its port side gives way to the one "
                        "with the wind over its starboard side. And if the wind is on the same side "
                        "for both, the boat that's upwind keeps clear."):
            self.play(Write(ttl), LaggedStart(*[GrowArrow(a) for a in wind]), FadeIn(wl))
            self.play(FadeIn(stb), FadeIn(prt))
            self.play(FadeIn(sl), FadeIn(pl))
            self.play(FadeIn(note))
        self.clear_all()


class S6_BigShips(VScene):
    def construct(self):
        self.chapter(4, "Big ships rule the Bay")
        rule = T("Rule 9 — narrow channels", 40, YELLOW, weight=BOLD).to_edge(UP)
        body = VGroup(
            T("A boat under 20 m (65 ft), or any sailboat,", 32),
            T("must not impede a vessel that can only", 32),
            T("navigate safely inside the channel.", 32),
        ).arrange(DOWN, buff=0.15).next_to(rule, DOWN, buff=0.5)
        plain = T("In plain English: in the channel, big ships win.", 36, WHITE,
                  weight=BOLD).next_to(body, DOWN, buff=0.7)
        with self.voice("Here's the rule that matters most on San Francisco Bay. Rule nine. In a "
                        "narrow channel, a boat under twenty meters, about sixty-five feet, or any "
                        "sailboat, must not impede a vessel that can only navigate safely inside "
                        "that channel. In plain English: in the shipping channels, big ships win. "
                        "Even over sailboats."):
            self.play(Write(rule))
            self.play(FadeIn(body, shift=UP * 0.2))
            self.play(Write(plain))
        self.clear_all()

        # --- scale
        L_ship = 11.0
        ship = Boat(SHIP_C, L_ship, "ship", lights=False, width_ratio=0.13).place([0, 1.2, 0], 0)
        mine = Boat(YOU_C, L_ship * 8 / 330, lights=False, width_ratio=0.4).place([0, -0.6, 0], 0)
        sl = T("container ship  ~330 m", 28, SHIP_C).next_to(ship, UP)
        ml = T("your boat  ~8 m, to scale", 28, YOU_C).next_to(mine, DOWN, buff=0.3)
        circ = Circle(radius=0.25, color=YOU_C).move_to(mine.pos)
        with self.voice("Here's why. A large container ship can be well over three hundred meters "
                        "long. Here's your boat, to scale."):
            self.play(FadeIn(ship), Write(sl))
            self.play(FadeIn(mine), Create(circ), Write(ml))
        facts = VGroup(
            T("stuck in a dredged channel: can't swerve", 30),
            T("may need a mile or more to stop", 30),
            T("bridge is far aft: can't see water just ahead", 30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(DOWN, buff=0.6)
        with self.voice("That ship is stuck in a dredged channel. It can't swerve. At speed it may "
                        "need a mile or more to stop. And there's something worse.") as d:
            self.play(FadeIn(facts[0]))
            self.play(FadeIn(facts[1]))
        self.clear_all()

        # --- blind zone (side view)
        sea_y = -1.2
        sea = Line(LEFT * 7.5 + UP * sea_y, RIGHT * 7.5 + UP * sea_y, color=CURRENT_C, stroke_width=2)
        bow_x = -2.4
        hull = Polygon([-7.1, sea_y - 0.5, 0], [-7.2, sea_y + 0.5, 0], [bow_x, sea_y + 0.5, 0],
                       [bow_x - 0.5, sea_y - 0.5, 0],
                       fill_color=SHIP_C, fill_opacity=1, stroke_color=WHITE, stroke_width=1.5)
        stack = VGroup(*[Rectangle(width=0.42, height=1.4, stroke_width=0.5, stroke_color=BLACK,
                                   fill_opacity=1,
                                   fill_color=[RED_E, BLUE_E, GREEN_E, GOLD_E, TEAL_E][i % 5])
                         .move_to([-2.95 - i * 0.45, sea_y + 0.5 + 0.7, 0]) for i in range(8)])
        bridge = Rectangle(width=0.5, height=2.6, fill_color=WHITE, fill_opacity=0.9,
                           stroke_width=0).move_to([-6.5, sea_y + 0.5 + 1.3, 0])
        eye = np.array([-6.4, sea_y + 3.0, 0])
        corner = stack[0].get_corner(UR)
        slope = (corner[1] - eye[1]) / (corner[0] - eye[0])
        x_hit = eye[0] + (sea_y - eye[1]) / slope
        sight = Line(eye, [x_hit, sea_y, 0], color=YELLOW, stroke_width=3)
        blind = Polygon(corner, [x_hit, sea_y, 0], [bow_x - 0.25, sea_y, 0], [bow_x, sea_y + 0.5, 0],
                        fill_color=RED, fill_opacity=0.35, stroke_width=0)
        bl = T("BLIND ZONE", 30, RED, weight=BOLD).move_to([(bow_x + x_hit) / 2, sea_y - 0.6, 0])
        bl2 = T("can be hundreds of meters", 24, GREY_A).next_to(bl, DOWN, buff=0.15)
        me = Rectangle(width=0.2, height=0.12, fill_color=YOU_C, fill_opacity=1,
                       stroke_width=0).move_to([(bow_x + x_hit) / 2, sea_y + 0.06, 0])
        ship_g = VGroup(hull, stack, bridge)
        with self.voice("The bridge, where the captain stands, is way at the back. Draw the line "
                        "of sight from there, over the stacked containers, down to the water. "
                        "Everything under that line, sometimes hundreds of meters of water ahead "
                        "of the bow, is invisible to them. If you're under its bow, they may "
                        "literally not see you."):
            self.play(Create(sea), FadeIn(ship_g))
            self.play(Flash(eye, color=YELLOW), Create(sight))
            self.play(FadeIn(blind), Write(bl), FadeIn(bl2))
            self.play(FadeIn(me), Indicate(me, color=YOU_C, scale_factor=3))
        self.clear_all()

        # --- race over one nautical mile
        line = NumberLine(x_range=[0, 1, 0.25], length=11, include_numbers=False,
                          color=GREY_B).shift(DOWN * 0.2)
        l0 = T("0", 24, GREY_B).next_to(line.n2p(0), DOWN)
        l1 = T("1 nautical mile", 24, GREY_B).next_to(line.n2p(1), DOWN)
        racers = [("ferry, 30 kn", 30, WHITE, 1.9), ("ship, 15 kn", 15, SHIP_C, 1.0),
                  ("you, 6 kn", 6, YOU_C, 0.1)]
        tmin = ValueTracker(0)
        dots, labs = VGroup(), VGroup()
        for name, kn, col, dy in racers:
            y = dy
            d = Dot(color=col, radius=0.12)
            d.add_updater(lambda m, kn=kn, y=y: m.move_to(
                line.n2p(min(1, kn / 60 * tmin.get_value())) + UP * y))
            lab = T(name, 24, col)
            lab.add_updater(lambda m, d=d: m.next_to(d, UP, buff=0.12))
            dots.add(d)
            labs.add(lab)
        clock = always_redraw(lambda: T(f"{tmin.get_value():4.1f} minutes", 40, YELLOW,
                                        weight=BOLD).to_edge(UP, buff=0.8))
        with self.voice("And they're faster than they look. Race over one nautical mile. A ferry "
                        "at thirty knots covers it in two minutes. A ship at fifteen knots, four "
                        "minutes. You, at six knots, ten. A ship that looked far away when you "
                        "started to cross can be on top of you before you're halfway across.") as d:
            self.play(Create(line), FadeIn(l0), FadeIn(l1), FadeIn(dots), FadeIn(labs), FadeIn(clock))
            self.play(tmin.animate.set_value(10), run_time=d - 2.5, rate_func=linear)
        for m in [*dots, *labs]:
            m.clear_updaters()
        self.clear_all()

        tips = VGroup(
            T("Stay out of the main channels when you can.", 32),
            T("Cross them quickly, at right angles.", 32),
            T("Cross behind big ships, never in front.", 32),
            T("Assume they cannot see you.", 32, YELLOW, weight=BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        with self.voice("So: stay out of the main channels when you can; there's usually plenty of "
                        "water outside them. When you have to cross, cross quickly, at right "
                        "angles, and behind big ships, never in front. And assume you're "
                        "invisible.") as d:
            self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.3) for t in tips], lag_ratio=0.9),
                      run_time=d * 0.85)
        self.clear_all()

        # --- horn signals
        hdr = T("Listen for horns", 44, weight=BOLD).to_edge(UP)
        self.play(Write(hdr))

        def blasts(pat):
            parts = [RoundedRectangle(width=0.35 if c == "s" else 1.4, height=0.3,
                                      corner_radius=0.15, fill_color=YELLOW, fill_opacity=1,
                                      stroke_width=0) for c in pat]
            return VGroup(*parts).arrange(RIGHT, buff=0.18)

        signals = [
            ("sssss", "5+ short:  DANGER / \"I don't understand you\"",
             "Five or more short blasts means danger, or, I don't understand what you're doing. "
             "If you hear it on the Bay, it's probably meant for you. Change something, obviously."),
            ("s", "1 short:  turning to starboard / pass port-to-port",
             "One short blast: I'm altering course to starboard, or, in inland waters, I intend to "
             "pass you port side to port side."),
            ("ss", "2 short:  turning to port / pass starboard-to-starboard",
             "Two short blasts: the mirror image. Turning to port, or passing starboard to starboard."),
            ("sss", "3 short:  I'm backing up",
             "Three short blasts: my engines are going astern. I'm backing up."),
            ("l", "1 prolonged:  leaving a dock, or near a blind bend",
             "And one long blast: a vessel leaving its berth, or approaching a bend where it can't "
             "see around."),
        ]
        rows = VGroup()
        for pat, txt, _ in signals:
            b = blasts(pat)
            row = VGroup(b, T(txt, 26)).arrange(RIGHT, buff=0.4)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42).next_to(hdr, DOWN, buff=0.6)
        for b in rows:
            b[1].align_to(rows, LEFT).shift(RIGHT * 3.2)
        for (pat, _, vo), row in zip(signals, rows):
            with self.voice(vo):
                self.play(FadeIn(row, shift=UP * 0.1), run_time=0.6)
            dur = self.horn(pat)
            self.play(LaggedStart(*[Indicate(p, color=WHITE, scale_factor=1.4) for p in row[0]],
                                  lag_ratio=0.9), run_time=dur)
            self.wait(0.3)
        self.clear_all()

        # --- VHF
        hdr = T("And on your VHF radio", 44, weight=BOLD).to_edge(UP)
        chans = VGroup()
        for ch, desc, col in [("16", "distress, safety, and hailing", RED_L),
                              ("13", "bridge-to-bridge: where ships coordinate", WHITE),
                              ("14", "SF Vessel Traffic Service: listen to know\nwhich big ships are moving where", YELLOW)]:
            num = T(ch, 72, col, weight=BOLD)
            chans.add(VGroup(num, T(desc, 30)).arrange(RIGHT, buff=0.5))
        chans.arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(hdr, DOWN, buff=0.7)
        with self.voice("And on your VHF radio: channel sixteen is for distress, safety, and "
                        "hailing. Channel thirteen is bridge to bridge, where ships coordinate "
                        "with each other. And channel fourteen is San Francisco Vessel Traffic "
                        "Service. Just listening there tells you which big ships are moving, and "
                        "where.") as d:
            self.play(Write(hdr))
            self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in chans], lag_ratio=1.0),
                      run_time=d * 0.7)
        self.clear_all()


class S7_Channel(VScene):
    def construct(self):
        self.chapter(5, "Reading the channel")

        def nun(n):
            tri = Triangle(fill_color=RED_L, fill_opacity=1, stroke_width=0).scale(0.28)
            return VGroup(tri, T(str(n), 20, WHITE, weight=BOLD).move_to(tri).shift(DOWN * 0.05))

        def can(n):
            sq = Square(0.42, fill_color=GREEN_L, fill_opacity=1, stroke_width=0)
            return VGroup(sq, T(str(n), 20, BLACK, weight=BOLD).move_to(sq))

        CX = -2.6
        ys = np.linspace(-2.7, 2.5, 4)
        xs = lambda y: 0.6 * np.sin(y * 0.6)
        reds = VGroup(*[nun(2 * (i + 1)).move_to([xs(y) + 1.6 + CX, y, 0]) for i, y in enumerate(ys)])
        greens = VGroup(*[can(2 * i + 1).move_to([xs(y) - 1.6 + CX, y, 0]) for i, y in enumerate(ys)])
        center = smooth_path(*[[xs(y) + CX, y, 0] for y in np.linspace(-4.3, 4.3, 12)])
        sea = T("from sea", 26, GREY_B).move_to([CX + 2.2, -3.7, 0])
        port = T("to port / upstream", 26, GREY_B).move_to([CX + 2.9, 3.6, 0])
        rrr = VGroup(T("Red", 56, RED_L, weight=BOLD), T("Right", 56, weight=BOLD),
                     T("Returning", 56, weight=BOLD)).arrange(DOWN, aligned_edge=LEFT).to_edge(
            RIGHT, buff=1.5)
        with self.voice("In a marked channel, the buoys follow one simple rule: red, right, "
                        "returning. When you're returning from sea, heading into port or "
                        "upstream, keep the red markers on your right.") as d:
            self.play(FadeIn(reds), FadeIn(greens), FadeIn(sea), FadeIn(port))
            self.play(Write(rrr))
            b = Boat(YOU_C).place(center.point_from_proportion(0), PI / 2)
            self.add(b, wake(b, YOU_C))
            self.play(drive(b, center, run_time=d - 2.5))
        detail = VGroup(
            VGroup(nun(2).scale(1.3), T("red: even numbers, cone-shaped \"nuns\"", 26)).arrange(RIGHT),
            VGroup(can(1).scale(1.3), T("green: odd numbers, flat-topped \"cans\"", 26)).arrange(RIGHT),
            T("numbers increase as you come in from sea", 26, GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        detail.next_to([0.5, 0, 0], RIGHT, buff=0)
        with self.voice("Red ones carry even numbers and are often cone-shaped nuns. Green ones are "
                        "odd, often flat-topped cans. The numbers count up as you come in from sea. "
                        "Head back out, and everything flips: red on your left.") as d:
            self.play(FadeOut(rrr), FadeOut(b), FadeIn(detail))
            b2 = Boat(YOU_C).place(center.point_from_proportion(1), -PI / 2)
            self.add(b2, wake(b2, YOU_C))
            self.play(drive(b2, center.copy().reverse_points(), run_time=d - 1.5))
        with self.voice("On the Bay, 'returning' means heading in from the Golden Gate, toward the "
                        "ports and rivers. And remember, a buoy is a fixed object sitting in moving "
                        "water. Don't let the current sweep you onto one."):
            self.wait(0.5)
        self.clear_all()


class S8_CurrentWind(VScene):
    def construct(self):
        self.chapter(6, "Current and wind")
        gg = VGroup(
            T("Twice a day, the tide pours in and out through the Golden Gate.", 30),
            VGroup(T("flood", 34, CURRENT_C, weight=BOLD), T("in", 30), T("·", 30),
                   T("ebb", 34, CURRENT_C, weight=BOLD), T("out", 30)).arrange(RIGHT, buff=0.2),
            T("strong ebb at the Gate:  4 – 6 knots", 40, YELLOW, weight=BOLD),
            T("≈ as fast as many small boats cruise", 28, GREY_A),
        ).arrange(DOWN, buff=0.35)
        with self.voice("Which brings us to what makes San Francisco Bay genuinely different: the "
                        "water itself moves. Twice a day, the tide pours huge volumes of water in "
                        "and out through the Golden Gate. In is the flood, out is the ebb. At the "
                        "Gate, a strong ebb can run four to six knots. That can be as fast as your "
                        "boat.") as d:
            self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in gg], lag_ratio=0.8),
                      run_time=d * 0.8)
        self.clear_all()

        # --- vector addition
        hdr = T("where you go  =  where you point  +  where the water goes", 30).to_edge(UP)
        flow = VGroup(*[Arrow(LEFT * 0.4, RIGHT * 0.4, buff=0, color=CURRENT_C, stroke_width=3,
                              max_tip_length_to_length_ratio=0.3).set_opacity(0.35)
                        .move_to([x, y, 0]) for x in np.arange(-6, 7, 2) for y in (-3.3, 3.0)])
        start = np.array([-2.5, -2.4, 0])
        vw = np.array([0, 2.4, 0])     # boat through water
        vc = np.array([1.6, 0, 0])     # current
        b = Boat(YOU_C).place(start, PI / 2)
        a_w = Arrow(start, start + vw, buff=0, color=YOU_C, stroke_width=6)
        a_c = Arrow(start + vw, start + vw + vc, buff=0, color=CURRENT_C, stroke_width=6)
        a_g = Arrow(start, start + vw + vc, buff=0, color=YELLOW, stroke_width=6)
        lw = T("through the water", 24, YOU_C).next_to(a_w, LEFT)
        lc = T("current", 24, CURRENT_C).next_to(a_c, UP)
        lg = T("over the ground", 24, YELLOW).next_to(a_g.get_center(), RIGHT, buff=0.4)
        with self.voice("Your boat moves relative to the water. The water moves relative to the "
                        "ground. What you actually do is the sum of the two."):
            self.play(Write(hdr), FadeIn(flow), FadeIn(b))
            self.play(GrowArrow(a_w), FadeIn(lw))
            self.play(GrowArrow(a_c), FadeIn(lc))
            self.play(GrowArrow(a_g), FadeIn(lg))
        self.add(wake(b, YOU_C, 3))
        with self.voice("Point straight across a current, and you crab sideways, even though your "
                        "bow never stops pointing where you aimed.") as d:
            self.play(drive(b, seg(start, start + 2.4 * (vw + vc)), run_time=d - 0.5,
                            heading=PI / 2))
        self.clear_all()

        flow = VGroup(*[Arrow(LEFT * 0.4, RIGHT * 0.4, buff=0, color=CURRENT_C, stroke_width=3,
                              max_tip_length_to_length_ratio=0.3).set_opacity(0.35)
                        .move_to([x, y, 0]) for x in np.arange(-6, 7, 2) for y in (-3.3, 3.0)])
        start = np.array([0, -2.4, 0])
        goal = Dot([0, 2.6, 0], color=YELLOW)
        gl = T("where you want to go", 24, YELLOW).next_to(goal, RIGHT)
        aim = np.array([-1.6, 2.0, 0])
        b = Boat(YOU_C).place(start, np.arctan2(aim[1], aim[0]))
        a_w = Arrow(start, start + aim, buff=0, color=YOU_C, stroke_width=6)
        a_c = Arrow(start + aim, start + aim + vc, buff=0, color=CURRENT_C, stroke_width=6)
        a_g = Arrow(start, start + aim + vc, buff=0, color=YELLOW, stroke_width=6)
        with self.voice("To go straight across, aim upstream, so the sum points where you actually "
                        "want to go.") as d:
            self.play(FadeIn(flow), FadeIn(b), FadeIn(goal), FadeIn(gl))
            self.play(GrowArrow(a_w), GrowArrow(a_c))
            self.play(GrowArrow(a_g))
        self.add(wake(b, YOU_C, 3))
        self.play(FadeOut(VGroup(a_w, a_c, a_g)),
                  drive(b, seg(start, [0, 2.4, 0]), run_time=3, heading=np.arctan2(aim[1], aim[0])))
        self.clear_all()

        # --- into vs with
        nl = NumberLine(x_range=[-2, 10, 1], length=11, include_numbers=False, color=GREY_B)
        nl.shift(DOWN * 0.3)
        ticks = VGroup(*[T(str(i), 22, GREY_B).next_to(nl.n2p(i), DOWN) for i in (0, 1, 5, 9)])
        kn = T("knots over ground", 22, GREY_B).next_to(nl, DOWN, buff=0.7)
        up = VGroup(Arrow(nl.n2p(0) + UP * 1.6, nl.n2p(5) + UP * 1.6, buff=0, color=YOU_C),
                    Arrow(nl.n2p(5) + UP * 1.1, nl.n2p(1) + UP * 1.1, buff=0, color=CURRENT_C))
        upl = T("into a 4 kn ebb:  1 knot", 30, YELLOW).next_to(up, UP)
        dn = VGroup(Arrow(nl.n2p(0) + UP * 1.6, nl.n2p(5) + UP * 1.6, buff=0, color=YOU_C),
                    Arrow(nl.n2p(5) + UP * 1.1, nl.n2p(9) + UP * 1.1, buff=0, color=CURRENT_C))
        dnl = T("with it:  9 knots", 30, YELLOW).next_to(dn, UP)
        res = Dot(nl.n2p(1), color=YELLOW, radius=0.12)
        with self.voice("Head straight into a four-knot ebb at five knots, and you make one knot "
                        "over the ground. Barely moving. Turn around, and you're doing nine. Plan "
                        "your trips so the current carries you, especially on the way home."):
            self.play(Create(nl), FadeIn(ticks), FadeIn(kn))
            self.play(GrowArrow(up[0]))
            self.play(GrowArrow(up[1]), FadeIn(upl), FadeIn(res))
            self.wait(1)
            self.play(ReplacementTransform(up, dn), ReplacementTransform(upl, dnl),
                      res.animate.move_to(nl.n2p(9)))
        self.clear_all()

        # --- buoy streaming
        buoy = Triangle(fill_color=RED_L, fill_opacity=1, stroke_width=0).scale(0.3).shift(UP * 0.4)
        streaks = VGroup(*[Line([0.2, 0.4 + s * 0.15, 0], [-2.8, 0.4 + s * 0.6, 0],
                                color=CURRENT_C, stroke_width=2).set_opacity(0.6)
                           for s in (-1, 1)])
        flow = VGroup(*[Arrow(RIGHT * 0.4, LEFT * 0.4, buff=0, color=CURRENT_C, stroke_width=3,
                              max_tip_length_to_length_ratio=0.3).set_opacity(0.35)
                        .move_to([x, y, 0]) for x in np.arange(-6, 7, 2) for y in (-2.0, 2.8)])
        self.add(flow)
        lab = T("the wake streaming off a buoy shows you the current", 28).to_edge(DOWN, buff=1.0)
        drift = Boat(YOU_C).place([4.0, 1.6, 0], -PI / 2)
        with self.voice("Current will also push you sideways into things that don't move: buoys, "
                        "piers, anchored ships, bridge towers. You can read it right off the "
                        "water. A buoy in current trails a little wake downstream, like a rock "
                        "in a river.") as d:
            self.play(FadeIn(buoy), Create(streaks), FadeIn(lab))
            self.play(FadeIn(drift))
            self.play(drive(drift, seg([4.0, 1.6, 0], [1.0, 0.9, 0]), run_time=d - 3.2,
                            heading=-PI / 2 + 0.05))
        self.clear_all()

        # --- wind against current
        A = ValueTracker(0.25)
        k = ValueTracker(1.2)
        ph = ValueTracker(0)
        wave_ = always_redraw(lambda: FunctionGraph(
            lambda x: A.get_value() * np.sin(k.get_value() * x - ph.get_value()),
            x_range=[-6.5, 6.5, 0.02], color=CURRENT_C, stroke_width=4).shift(DOWN * 0.5))
        wind = Arrow(LEFT * 5 + UP * 2.2, LEFT * 2 + UP * 2.2, buff=0, color=BLUE_B, stroke_width=6)
        wl = T("wind (westerly)", 26, BLUE_B).next_to(wind, UP)
        cur = Arrow(RIGHT * 5 + DOWN * 2.6, RIGHT * 2 + DOWN * 2.6, buff=0, color=CURRENT_C,
                    stroke_width=6)
        cl = T("current (ebb)", 26, CURRENT_C).next_to(cur, DOWN)
        steep = T("short, steep, nasty", 40, YELLOW, weight=BOLD).to_edge(UP, buff=0.4)
        with self.voice("And when wind blows against current, waves stack up. The opposing current "
                        "squeezes them closer together while the wind keeps building them taller. "
                        "They get short, steep, and nasty. At the Gate, the classic setup is the "
                        "afternoon westerly wind blowing in against a strong ebb flowing out.") as d:
            self.add(wave_)
            self.play(GrowArrow(wind), FadeIn(wl), ph.animate.set_value(3), run_time=2,
                      rate_func=linear)
            self.play(GrowArrow(cur), FadeIn(cl), A.animate.set_value(0.95), k.animate.set_value(3.2),
                      ph.animate.set_value(3 + (d - 3.5) * 2.5), run_time=d - 3.5, rate_func=linear)
            self.play(FadeIn(steep), ph.animate.increment_value(3.5), run_time=1.5, rate_func=linear)
        self.clear_all()

        # --- daily wind
        ax = Axes(x_range=[6, 20, 3], y_range=[0, 30, 10], x_length=10, y_length=4.6,
                  axis_config={"include_numbers": False, "color": GREY_B}, tips=False).shift(DOWN * 0.4)
        xl = VGroup(*[T(s, 22, GREY_B).next_to(ax.c2p(h, 0), DOWN) for h, s in
                      [(6, "6am"), (9, "9am"), (12, "noon"), (15, "3pm"), (18, "6pm")]])
        yl = VGroup(*[T(f"{v} kn", 22, GREY_B).next_to(ax.c2p(6, v), LEFT) for v in (10, 20, 30)])
        grid = VGroup(*[DashedLine(ax.c2p(6, v), ax.c2p(20, v), color=GREY_D, stroke_width=1)
                        for v in (10, 20, 30)])
        f = lambda h: 4 + 19 / (1 + np.exp(-(h - 12.8) / 1.1)) - 12 / (1 + np.exp(-(h - 19.0) / 0.8))
        curve = ax.plot(f, x_range=[6, 20], color=BLUE_B, stroke_width=5)
        ttl = T("a typical summer day in \"the Slot\"", 32, weight=BOLD).to_edge(UP, buff=0.4)
        calm = T("calm-ish morning", 24, GREY_A).next_to(ax.c2p(8, f(8)), UP, buff=0.3)
        blow = T("afternoon westerly, often 20+ kn", 24, YELLOW).next_to(ax.c2p(16.5, f(16.5)), UP, buff=0.3)
        with self.voice("That afternoon westerly is the other big pattern on the Bay. Especially in "
                        "summer, mornings are often fairly calm. Then, as the inland valleys heat "
                        "up, cold ocean air pours in through the Gate. By afternoon, twenty-plus "
                        "knots is routine in the Slot, the stretch from the Gate past Alcatraz "
                        "toward Berkeley. Fog often rides in with it.") as d:
            self.play(Write(ttl), Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(grid))
            self.play(Create(curve), run_time=d * 0.45, rate_func=linear)
            self.play(FadeIn(calm), FadeIn(blow))
        tips = VGroup(T("Check current predictions, not just tide heights.", 30),
                      T("Go out in the morning. Come home with wind and current behind you.", 30)
                      ).arrange(DOWN, buff=0.25).to_edge(DOWN, buff=0.3)
        with self.voice("So check the current predictions, not just the tide heights. Go out in the "
                        "morning, and plan to come home with the wind and current behind you."):
            self.play(VGroup(ax, xl, yl, grid, curve, calm, blow).animate.scale(0.8).shift(UP * 0.7),
                      run_time=0.8)
            self.play(FadeIn(tips, shift=UP * 0.2))
        self.clear_all()


class S9_Recap(VScene):
    def construct(self):
        hdr = T("What to carry in your head", 44, weight=BOLD).to_edge(UP, buff=0.4)
        items = [
            ("Steady bearing + shrinking range = collision course.", WHITE),
            ("Give-way: early, big, obvious.  Stand-on: hold course, but act if needed.", WHITE),
            ("Head-on: both turn right.  Boat on your right: you give way.  Overtaking: you keep clear.", WHITE),
            ("See red, stop.  See green, go.", WHITE),
            ("Less maneuverable boats stand on.  Engine on = powerboat.", WHITE),
            ("In the channels, big ships win.  Cross behind, fast, at right angles.", YELLOW),
            ("Five short blasts: it's probably you.", WHITE),
            ("Red, right, returning.", WHITE),
            ("Respect the current and the afternoon wind.", YELLOW),
        ]
        rows = VGroup(*[
            VGroup(Dot(radius=0.06, color=c), T(s, 24, c)).arrange(RIGHT, buff=0.25)
            for s, c in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rows.next_to(hdr, DOWN, buff=0.45)
        with self.voice("So, here's what to carry in your head. Steady bearing and shrinking range "
                        "means collision course. Give-way boats act early and obviously; stand-on "
                        "boats hold steady. Head on, both turn right. The boat on your right stands "
                        "on. Overtakers keep clear. See red, stop; see green, go. Less maneuverable "
                        "boats stand on. In the channels, big ships win. Five short blasts means "
                        "you. Red, right, returning. And respect the current and the wind.") as d:
            self.play(Write(hdr))
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.9),
                      run_time=d * 0.85)
        self.clear_all()

        final = T("The rules never excuse a collision.", 44, weight=BOLD)
        doubt = T("When in doubt: slow down, turn early and obviously, pass behind.", 30, YELLOW)
        VGroup(final, doubt).arrange(DOWN, buff=0.5)
        fine = T("Not a substitute for the USCG Navigation Rules, NOAA current predictions, "
                 "or local instruction.", 20, GREY_B).to_edge(DOWN, buff=0.4)
        with self.voice("And above all of them sits rule two: the rules never excuse a collision. "
                        "When in doubt, slow down, turn early and obviously, and pass behind. "
                        "Have fun out there."):
            self.play(Write(final))
            self.play(FadeIn(doubt, shift=UP * 0.2))
            self.play(FadeIn(fine))
        self.wait(1.5)
        self.play(FadeOut(VGroup(final, doubt, fine)))
