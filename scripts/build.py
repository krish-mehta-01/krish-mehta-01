"""
Builds every image on the profile README, in light and dark versions.

  python scripts/build.py            (GH_TOKEN env var enables live activity data)

Standard library only. Fonts in fonts/ are pre-subset WOFF files that get
inlined into each SVG, so the cards look the same on every machine and
GitHub's image proxy never has to fetch anything.
"""
import base64
import html
import json
import os
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = ROOT / "fonts"
LOGIN = "krish-mehta-01"

THEMES = {
    "light": dict(
        bg1="#f3f1fb", bg2="#e6e1f8", panel="#ffffff", panel_op=0.72, edge="#ffffff",
        ink="#121218", ink2="#34333f", muted="#6c6b7b", faint="#9a99a8", accent="#5a48f5",
        line="#e7e4f1", blob=0.85,
        heat=["#ebe8f5", "#d6cffb", "#ae9ff8", "#806cf3", "#5a48f5"],
    ),
    "dark": dict(
        bg1="#13121c", bg2="#1b1830", panel="#ffffff", panel_op=0.05, edge="#2c2a3d",
        ink="#f3f1ff", ink2="#d6d3ea", muted="#a9a6c2", faint="#77748f", accent="#a99bff",
        line="#2a2839", blob=0.28,
        heat=["#221f31", "#352d63", "#5243a8", "#7a66ea", "#a99bff"],
    ),
}
LANG_COLORS = ["#5a48f5", "#8f7bff", "#c2b6ff", "#f2a7d8", "#9cc3ff", "#cfd4e6"]


# ── helpers ──────────────────────────────────────────────────────────────────
def esc(s):
    return html.escape(str(s), quote=True)


def font_css(*names):
    faces = []
    for name in names:
        data = base64.b64encode((FONTS / f"{name}.woff").read_bytes()).decode()
        faces.append(f"@font-face{{font-family:'{name}';src:url(data:font/woff;base64,{data}) format('woff');}}")
    return "".join(faces)


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def svg(w, h, label, body, fonts):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}">'
        f"<style>{font_css(*fonts)}"
        ".d7{font-family:'display-700'} .d6{font-family:'display-600'} .s4{font-family:'sans-400'}"
        ".s5{font-family:'sans-500'} .m{font-family:'mono-500'} .i{font-family:'serif-italic'}"
        f"</style>{body}</svg>\n"
    )


def backdrop(t, w, h, blobs, uid):
    blob_svg = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in blobs)
    return (
        f'<defs><linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
        f'<filter id="soft{uid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="36"/></filter>'
        f'<clipPath id="clip{uid}"><rect width="{w}" height="{h}" rx="26"/></clipPath></defs>'
        f'<g clip-path="url(#clip{uid})"><rect width="{w}" height="{h}" fill="url(#bg{uid})"/>'
        f'<g opacity="{t["blob"]}" filter="url(#soft{uid})">{blob_svg}</g>'
    )


def frame(t, w, h):
    return f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="26" fill="none" stroke="{t["edge"]}"/></g>'


GLASS_DEFS = (
    '<linearGradient id="iri" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#ffffff"/><stop offset="0.35" stop-color="#d9ccff"/>'
    '<stop offset="0.6" stop-color="#f6c8ec"/><stop offset="0.85" stop-color="#bcd8ff"/>'
    '<stop offset="1" stop-color="#ffffff"/></linearGradient>'
    '<radialGradient id="pearl" cx="0.35" cy="0.3" r="0.75"><stop offset="0" stop-color="#ffffff"/>'
    '<stop offset="0.45" stop-color="#e6ddff"/><stop offset="0.8" stop-color="#f3cdec"/>'
    '<stop offset="1" stop-color="#b9d3ff"/></radialGradient>'
)


# ── hero ─────────────────────────────────────────────────────────────────────
def hero(t):
    w, h = 1280, 340
    body = backdrop(t, w, h, [(1040, 40, 150, "#cfc3ff"), (1210, 270, 120, "#f5cbe9"), (860, 320, 110, "#c3d8ff")], "h")
    body += f"<defs>{GLASS_DEFS}</defs>"
    # glass ring turning slowly in 3D (squash + rotate), pearls drifting
    body += (
        '<g transform="translate(1010 172)"><g>'
        '<animateTransform attributeName="transform" type="rotate" values="-24;-14;-24" dur="14s" repeatCount="indefinite"/>'
        '<ellipse rx="128" ry="62" fill="none" stroke="url(#iri)" stroke-width="30" opacity="0.94">'
        '<animate attributeName="ry" values="62;78;62" dur="14s" repeatCount="indefinite"/></ellipse>'
        '<ellipse rx="128" ry="54" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.7">'
        '<animate attributeName="ry" values="54;70;54" dur="14s" repeatCount="indefinite"/></ellipse>'
        "</g></g>"
        '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -10;0 0" dur="6s" repeatCount="indefinite"/>'
        '<circle cx="1182" cy="92" r="34" fill="url(#pearl)"/><ellipse cx="1172" cy="80" rx="10" ry="6" fill="#fff" opacity="0.85"/></g>'
        '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 8;0 0" dur="5s" repeatCount="indefinite"/>'
        '<circle cx="872" cy="256" r="16" fill="url(#pearl)"/></g>'
    )
    body += (
        f'<text x="72" y="92" class="m" font-size="15" letter-spacing="2" fill="{t["muted"]}">'
        "SHIMLA → CHENNAI · B.TECH (HONS) IT · RMKEC</text>"
        f'<text x="66" y="186" class="d7" font-size="92" letter-spacing="-3" fill="{t["ink"]}">Krish Mehta</text>'
        f'<text x="72" y="242" class="s5" font-size="30" letter-spacing="-0.5" fill="{t["ink2"]}">'
        f'I build technology for <tspan class="i" font-size="35" fill="{t["accent"]}" letter-spacing="0">'
        "the people it usually forgets.</tspan></text>"
        # status pill with a breathing dot
        f'<rect x="72" y="270" width="318" height="38" rx="19" fill="{t["panel"]}" fill-opacity="{t["panel_op"] + 0.1}" stroke="{t["edge"]}"/>'
        '<circle cx="94" cy="289" r="9" fill="#1fae5b" opacity="0.25">'
        '<animate attributeName="r" values="5;11;5" dur="2.4s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0.45;0;0.45" dur="2.4s" repeatCount="indefinite"/></circle>'
        '<circle cx="94" cy="289" r="5" fill="#1fae5b"/>'
        f'<text x="110" y="294" class="m" font-size="13.5" fill="{t["ink2"]}">Open to internships &amp; research</text>'
    )
    body += frame(t, w, h)
    return svg(w, h, "Krish Mehta — I build technology for the people it usually forgets.", body,
               ["display-700", "sans-500", "serif-italic", "mono-500"])


# ── section headers ──────────────────────────────────────────────────────────
def header(t, num, label, title_plain, title_italic):
    w, h = 1280, 120
    body = (
        f'<text x="8" y="40" class="m" font-size="15" letter-spacing="1.5" fill="{t["accent"]}">({num})'
        f'<tspan fill="{t["muted"]}" dx="10">{esc(label.upper())}</tspan></text>'
        f'<text x="4" y="98" class="d7" font-size="50" letter-spacing="-1.5" fill="{t["ink"]}">{esc(title_plain)} '
        f'<tspan class="i" font-size="56" letter-spacing="0" font-weight="400">{esc(title_italic)}</tspan></text>'
    )
    return svg(w, h, f"{title_plain} {title_italic}", body, ["display-700", "serif-italic", "mono-500"])


# ── project cards ────────────────────────────────────────────────────────────
def illo_mansakha(t):
    rows = [("Jaipur", 0.82, "#e2483d"), ("Bharatpur", 0.64, "#e2483d"), ("Ajmer", 0.41, "#e6a23c"), ("Kota", 0.27, t["accent"])]
    bars = "".join(
        f'<text x="318" y="{78 + i * 26}" class="s4" font-size="12.5" fill="{t["ink2"]}">{n}</text>'
        f'<rect x="388" y="{68 + i * 26}" width="170" height="9" rx="4.5" fill="{t["line"]}"/>'
        f'<rect x="388" y="{68 + i * 26}" width="{170 * v:.0f}" height="9" rx="4.5" fill="{c}"/>'
        for i, (n, v, c) in enumerate(rows)
    )
    return (
        '<rect x="60" y="22" width="190" height="210" rx="30" fill="#121218"/>'
        '<rect x="76" y="50" width="158" height="54" rx="14" fill="#ffffff" fill-opacity="0.12"/>'
        '<text x="88" y="72" class="s5" font-size="12.5" fill="#fff">Good morning. How are</text>'
        '<text x="88" y="90" class="s5" font-size="12.5" fill="#fff">you feeling today?</text>'
        + "".join(f'<circle cx="{98 + i * 38}" cy="130" r="13" fill="{c}"/>' for i, c in enumerate(["#e57373", "#f2b366", "#ffd36b", "#7fd18b"]))
        + '<text x="82" y="168" class="m" font-size="10.5" fill="#ffffff" fill-opacity="0.5">private · daily check-in</text>'
        + f'<rect x="296" y="36" width="284" height="150" rx="16" fill="{t["panel"]}" fill-opacity="{0.9 if t is THEMES["light"] else 0.08}"/>'
        + f'<text x="318" y="56" class="m" font-size="10.5" letter-spacing="1" fill="{t["muted"]}">DISTRICT DISTRESS · LIVE</text>'
        + bars
    )


def illo_health(t):
    roles = [("ASHA worker", "#fde7d3"), ("Facility head", "#e7e1fd"), ("District officer", "#dde8fd"), ("State dept.", "#d8f2ec")]
    out = ""
    for i, (r, c) in enumerate(roles):
        x, y = 60 + i * 132, 92
        out += f'<rect x="{x}" y="{y}" width="118" height="44" rx="12" fill="{c}"/>'
        out += f'<text x="{x + 59}" y="{y + 27}" text-anchor="middle" class="s5" font-size="13" fill="#222">{r}</text>'
        if i < 3:
            out += f'<text x="{x + 125}" y="{y + 28}" text-anchor="middle" class="s5" font-size="15" fill="{t["faint"]}">→</text>'
    out += (
        f'<text x="60" y="64" class="m" font-size="11" letter-spacing="1" fill="{t["muted"]}">REPORTS FLOW UP · DECISIONS FLOW BACK DOWN</text>'
        '<rect x="60" y="160" width="300" height="40" rx="12" fill="#fdecea"/>'
        '<text x="76" y="185" class="s5" font-size="13" fill="#8a2b20">Zia AI flagged 1 urgent case</text>'
        '<rect x="372" y="160" width="208" height="40" rx="12" fill="#dcf3e4"/>'
        '<text x="388" y="185" class="s5" font-size="13" fill="#1d7a45">offline · Hindi / English</text>'
    )
    return out


def illo_leaf(t):
    return (
        '<g transform="translate(300 128) rotate(-14)">'
        '<path d="M-120 0 C-80 -86 70 -96 130 -6 C70 82 -80 76 -120 0Z" fill="#79b05a"/>'
        '<path d="M-118 0 L128 -6" stroke="#5f9445" stroke-width="3" fill="none"/>'
        '<circle cx="34" cy="-30" r="15" fill="#b4823f"/><circle cx="-28" cy="26" r="10" fill="#a77a3e"/>'
        '<circle cx="74" cy="12" r="7" fill="#b4823f"/></g>'
        '<rect x="318" y="62" width="62" height="54" rx="4" fill="none" stroke="#e2483d" stroke-width="2.5"/>'
        '<rect x="318" y="44" width="92" height="18" rx="3" fill="#e2483d"/>'
        '<text x="324" y="57" class="m" font-size="11" fill="#fff">blight 0.94</text>'
        '<rect x="246" y="134" width="44" height="40" rx="4" fill="none" stroke="#d98a1c" stroke-width="2.5"/>'
        '<rect x="246" y="116" width="86" height="18" rx="3" fill="#d98a1c"/>'
        '<text x="252" y="129" class="m" font-size="11" fill="#fff">red rust 0.81</text>'
        f'<text x="60" y="210" class="m" font-size="11" fill="{t["muted"]}">8 classes · YOLOv26m crop → ConvNeXtV2 + Swin</text>'
    )


def illo_netsim(t):
    cx, cy = 300, 120
    devices = [(110, 70), (500, 60), (130, 190), (480, 186), (300, 214)]
    out = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["accent"]}" stroke-opacity="{0.55 - r / 260:.2f}" stroke-dasharray="2 6"/>'
        for r in (40, 75, 110)
    )
    out += f'<path d="M{cx} {cy} L{cx + 92} {cy - 62} A110 110 0 0 1 {cx + 108} {cy + 4} Z" fill="{t["accent"]}" fill-opacity="0.16"/>'
    for x, y in devices:
        out += f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{t["faint"]}" stroke-opacity="0.6"/>'
        out += f'<rect x="{x - 9}" y="{y - 9}" width="18" height="18" rx="5" fill="{t["panel"]}" stroke="{t["ink"]}" stroke-width="1.4"/>'
    out += f'<circle cx="{cx}" cy="{cy}" r="13" fill="{t["ink"]}"/>'
    out += f'<text x="60" y="34" class="m" font-size="11" fill="{t["muted"]}">digital twin · DQN state dim 10 · 2.4 GHz</text>'
    return out


PROJECTS = [
    dict(slug="mansakha", name="Mansakha", kind="SIH 2026 · AI FOR SOCIAL GOOD", illo=illo_mansakha,
         tint=("#f6e6ee", "#e3e6fa"), tint_dark=("#2a1f2e", "#1f2236"),
         desc="Distress prediction for survivors of atrocities under the SC/ST Act: private daily check-ins, every NHAA 14566 call on one timeline, a live district map."),
    dict(slug="healthconnect", name="HealthConnect Pro", kind="FULL-STACK · LIVE ON ZOHO CATALYST", illo=illo_health,
         tint=("#fbeee8", "#ece6fa"), tint_dark=("#2a2226", "#1f1e33"),
         desc="Connects village sub-centres to the state health department in both directions: 15+ roles, offline sync, and Zia AI to escalate urgent cases."),
    dict(slug="tealeaf", name="Tea Leaf Disease Detection", kind="RESEARCH · UNDER REVIEW, MDPI AGRICULTURE", illo=illo_leaf,
         tint=("#eef4e4", "#f3ebdf"), tint_dark=("#1e2a1f", "#2a2420"),
         desc="YOLOv26m-guided lesion cropping with a ConvNeXtV2–Swin Transformer ensemble. 97.3% mAP across eight disease classes."),
    dict(slug="qnetsim", name="Q-NETSIM Distributor", kind="CAPSTONE · REINFORCEMENT LEARNING", illo=illo_netsim,
         tint=("#e3e9f7", "#eee8fb"), tint_dark=("#1c2233", "#221e33"),
         desc="A digital twin of our 5G RF testbed where a DQN agent learns beam, power and resource decisions before touching real hardware."),
]


def project(t, p, dark):
    w, h = 640, 390
    c1, c2 = p["tint_dark"] if dark else p["tint"]
    uid = p["slug"]
    body = (
        f'<defs><clipPath id="c{uid}"><rect width="{w}" height="{h}" rx="26"/></clipPath>'
        f'<linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
        f'<g clip-path="url(#c{uid})">'
        f'<rect width="{w}" height="{h}" fill="{t["bg1"]}"/>'
        f'<rect width="{w}" height="{h}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}"/>'
        f'<rect x="14" y="14" width="{w - 28}" height="236" rx="18" fill="url(#g{uid})"/>'
        f'<g transform="translate(14 14)">{p["illo"](t)}</g>'
        f'<text x="30" y="286" class="m" font-size="12" letter-spacing="1.2" fill="{t["faint"]}">{esc(p["kind"])}</text>'
        f'<text x="28" y="320" class="d6" font-size="28" letter-spacing="-0.6" fill="{t["ink"]}">{esc(p["name"])}</text>'
        f'<text x="{w - 34}" y="320" text-anchor="end" class="d6" font-size="26" fill="{t["accent"]}">↗</text>'
    )
    for i, line in enumerate(wrap(p["desc"], 76)[:2]):
        body += f'<text x="30" y="{348 + i * 22}" class="s4" font-size="15" fill="{t["muted"]}">{esc(line)}</text>'
    body += f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="26" fill="none" stroke="{t["edge"]}"/></g>'
    return svg(w, h, f'{p["name"]}: {p["desc"]}', body, ["display-600", "sans-400", "sans-500", "mono-500"])


# ── activity strip (live data) ───────────────────────────────────────────────
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}"""
IGNORED_LANGS = {"HTML", "CSS", "Jupyter Notebook", "PLpgSQL", "Dockerfile", "Shell", "Batchfile", "Procfile"}


def fetch_activity():
    token = os.environ.get("GH_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]
    cal = data["contributionsCollection"]["contributionCalendar"]
    days = [d for wk in cal["weeks"] for d in wk["contributionDays"]]
    sizes = {}
    for repo in data["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in IGNORED_LANGS:
                sizes[name] = sizes.get(name, 0) + e["size"]
    return dict(total=cal["totalContributions"], days=days, langs=sizes)


def activity(t, data):
    w, h = 1280, 330
    body = backdrop(t, w, h, [(120, 330, 140, "#cfc3ff"), (1240, 20, 130, "#f5cbe9")], "a")
    body += f'<rect x="0" y="0" width="{w}" height="{h}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}"/>'

    # left: numbers
    total = data["total"] if data else 0
    body += (
        f'<text x="56" y="76" class="m" font-size="12.5" letter-spacing="1.2" fill="{t["faint"]}">LAST 12 MONTHS</text>'
        f'<text x="52" y="152" class="d7" font-size="76" letter-spacing="-2.5" fill="{t["ink"]}">{total:,}</text>'
        f'<text x="56" y="182" class="s5" font-size="16" fill="{t["muted"]}">contributions on GitHub</text>'
    )
    for i, (v, l) in enumerate([("5", "internships"), ("3", "papers"), ("37", "certifications")]):
        x = 56 + i * 118
        body += (
            f'<text x="{x}" y="246" class="d6" font-size="32" letter-spacing="-1" fill="{t["ink"]}">{v}</text>'
            f'<text x="{x}" y="270" class="s4" font-size="13.5" fill="{t["muted"]}">{l}</text>'
        )
    body += f'<line x1="440" y1="52" x2="440" y2="{h - 52}" stroke="{t["line"]}"/>'

    # right: heatmap (last 52 weeks)
    x0, y0, cell, gap = 482, 70, 12, 2.6
    if data:
        days = data["days"][-364:]
        start = date.fromisoformat(days[0]["date"])
        offset = (start.weekday() + 1) % 7          # GitHub weeks start on Sunday
        peak = max(d["contributionCount"] for d in days) or 1
        last_month = None
        for i, d in enumerate(days):
            k = i + offset
            col, row = k // 7, k % 7
            n = d["contributionCount"]
            lvl = 0 if n == 0 else min(4, 1 + int(3.999 * (n / peak) ** 0.5))
            x, y = x0 + col * (cell + gap), y0 + row * (cell + gap)
            body += f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3.2" fill="{t["heat"][lvl]}"/>'
            dt = start + timedelta(days=i)
            if dt.day <= 7 and row == 0 and dt.month != last_month:
                body += f'<text x="{x:.1f}" y="{y0 - 12}" class="m" font-size="11" fill="{t["faint"]}">{dt.strftime("%b")}</text>'
                last_month = dt.month
    legend_y = y0 + 7 * (cell + gap) + 18
    body += f'<text x="{x0}" y="{legend_y + 9}" class="m" font-size="11" fill="{t["faint"]}">less</text>'
    for i, c in enumerate(t["heat"]):
        body += f'<rect x="{x0 + 36 + i * 16}" y="{legend_y}" width="12" height="12" rx="3" fill="{c}"/>'
    body += f'<text x="{x0 + 36 + 5 * 16 + 4}" y="{legend_y + 9}" class="m" font-size="11" fill="{t["faint"]}">more</text>'

    # right: languages
    if data and data["langs"]:
        ranked = sorted(data["langs"].items(), key=lambda kv: -kv[1])
        whole = sum(v for _, v in ranked)
        top = [(n, v) for n, v in ranked if v / whole >= 0.01][:5]   # hide <1% slivers
        s = sum(v for _, v in top)
        bx, by, bw = x0, legend_y + 40, w - x0 - 56
        body += f'<clipPath id="lb"><rect x="{bx}" y="{by}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#lb)">'
        cx = bx
        for i, (name, v) in enumerate(top):
            seg = bw * v / s
            body += f'<rect x="{cx:.1f}" y="{by}" width="{seg + 1:.1f}" height="10" fill="{LANG_COLORS[i]}"/>'
            cx += seg
        body += "</g>"
        lx = bx
        for i, (name, v) in enumerate(top):
            label = f"{name} {100 * v / s:.0f}%"
            body += (
                f'<circle cx="{lx + 5}" cy="{by + 34}" r="5" fill="{LANG_COLORS[i]}"/>'
                f'<text x="{lx + 16}" y="{by + 39}" class="s4" font-size="13.5" fill="{t["ink2"]}">{esc(label)}</text>'
            )
            lx += 22 + len(label) * 7.6 + 18
    body += frame(t, w, h)
    return svg(w, h, f"{total} contributions in the last year", body, ["display-700", "display-600", "sans-400", "sans-500", "mono-500"])


# ── buttons ──────────────────────────────────────────────────────────────────
ICONS = {
    "website": '<circle cx="0" cy="0" r="8.5" fill="none" stroke="currentColor" stroke-width="1.8"/><ellipse rx="3.6" ry="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><line x1="-8.5" y1="0" x2="8.5" y2="0" stroke="currentColor" stroke-width="1.6"/>',
    "linkedin": '<rect x="-9" y="-9" width="18" height="18" rx="4" fill="currentColor"/><rect x="-5.5" y="-2" width="2.6" height="7.5" fill="BG"/><circle cx="-4.2" cy="-5" r="1.6" fill="BG"/><path d="M-1 -2h2.4v1.1c.5-.8 1.3-1.3 2.5-1.3 2 0 2.8 1.2 2.8 3.4v4.3H4.2V1.8c0-1.1-.3-1.8-1.3-1.8s-1.5.7-1.5 1.8v3.7H-1z" fill="BG"/>',
    "email": '<rect x="-9.5" y="-7" width="19" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M-8.5 -5.5 L0 1 L8.5 -5.5" fill="none" stroke="currentColor" stroke-width="1.8"/>',
    "leetcode": '<path d="M-4.5 -6.5 L-10 0 L-4.5 6.5 M4.5 -6.5 L10 0 L4.5 6.5 M1.6 -9 L-1.6 9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
}
BUTTONS = [("website", "Website"), ("linkedin", "LinkedIn"), ("email", "Email"), ("leetcode", "LeetCode")]


def button(t, key, label, dark):
    w, h = 300, 64
    bg = t["bg1"]
    icon = ICONS[key].replace("currentColor", t["ink"]).replace("BG", bg)
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="32" fill="{bg}" stroke="{t["edge"] if dark else "#e3dff2"}"/>'
        f'<g transform="translate(36 32)">{icon}</g>'
        f'<text x="62" y="38" class="s5" font-size="17" fill="{t["ink"]}">{label}</text>'
        f'<text x="{w - 30}" y="39" text-anchor="end" class="d6" font-size="18" fill="{t["accent"]}">↗</text>'
    )
    return svg(w, h, label, body, ["sans-500", "display-600"])


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    OUT.mkdir(exist_ok=True)
    data = None
    try:
        data = fetch_activity()
    except Exception as e:  # never fail the whole build because the API hiccuped
        print("activity fetch failed:", e)
    for mode, t in THEMES.items():
        dark = mode == "dark"
        (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf8")
        (OUT / f"h-work-{mode}.svg").write_text(header(t, "01", "Selected work", "Things I've", "built"), encoding="utf8")
        (OUT / f"h-activity-{mode}.svg").write_text(header(t, "02", "Activity", "Lately on", "GitHub"), encoding="utf8")
        for p in PROJECTS:
            (OUT / f"p-{p['slug']}-{mode}.svg").write_text(project(t, p, dark), encoding="utf8")
        if data or not (OUT / f"activity-{mode}.svg").exists():
            (OUT / f"activity-{mode}.svg").write_text(activity(t, data), encoding="utf8")
        for key, label in BUTTONS:
            (OUT / f"b-{key}-{mode}.svg").write_text(button(t, key, label, dark), encoding="utf8")
    print("built", len(list(OUT.glob("*.svg"))), "svgs", "(live activity)" if data else "(no activity data)")


if __name__ == "__main__":
    main()
