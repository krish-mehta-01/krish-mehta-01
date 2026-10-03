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
import math
import os
import urllib.request
from datetime import date
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
        heat=["#f1eff8", "#cfc6fb", "#a594f8", "#7a63f2", "#4f3be6"],
    ),
    "dark": dict(
        bg1="#13121c", bg2="#1b1830", panel="#ffffff", panel_op=0.05, edge="#2c2a3d",
        ink="#f3f1ff", ink2="#d6d3ea", muted="#b4b1cc", faint="#918da9", accent="#a99bff",
        line="#2f2c40", blob=0.28,
        heat=["#1e1c2c", "#3f3585", "#5f4fce", "#8a77fa", "#c4baff"],
    ),
}
LANG_COLORS = ["#5a48f5", "#8f7bff", "#c2b6ff", "#f2a7d8", "#9cc3ff", "#cfd4e6"]



# ── colour palettes ──────────────────────────────────────────────────────────
# Every SVG is drawn in the original violet "slots" below, then recoloured on
# the way out. To change the whole profile's colour, change PALETTE.
SLOTS = {
    "accent": "#5a48f5", "accent_dark": "#a99bff", "violet_card": "#6b5cff",
    "blob1": "#cfc3ff", "blob2": "#f5cbe9", "blob3": "#c3d8ff",
    "ring1": "#d9ccff", "ring2": "#f6c8ec", "ring3": "#bcd8ff",
    "pearl1": "#e6ddff", "pearl2": "#f3cdec", "pearl3": "#b9d3ff",
    "bg_l1": "#f3f1fb", "bg_l2": "#e6e1f8", "bg_d1": "#13121c", "bg_d2": "#1b1830",
    "hl0": "#f1eff8", "hl1": "#cfc6fb", "hl2": "#a594f8", "hl3": "#7a63f2", "hl4": "#4f3be6",
    "hd0": "#1e1c2c", "hd1": "#3f3585", "hd2": "#5f4fce", "hd3": "#8a77fa", "hd4": "#c4baff",
    "lang2": "#8f7bff", "lang3": "#c2b6ff",
    "line_l": "#e7e4f1", "line_d": "#2f2c40", "edge_d": "#2c2a3d", "stroke_l": "#e8e4f3", "stroke_l2": "#e3dff2",
    "empty_d": "#3d3955", "empty_l": "#dcd7ee", "muted_d": "#b4b1cc", "faint_d": "#918da9", "ink_d": "#f3f1ff", "ink2_d": "#d6d3ea",
}
PALETTES = {
    "violet": {},   # the original
    "teal": dict(
        accent="#0d8f84", accent_dark="#3fd6c4", violet_card="#0d9488",
        blob1="#a7efe4", blob2="#fde4b8", blob3="#bfe3fb",
        ring1="#c8f4ec", ring2="#fdebc8", ring3="#c4e6fb", pearl1="#dcf7f2", pearl2="#fdeccc", pearl3="#c9e7fb",
        bg_l1="#f2f8f7", bg_l2="#e4f1ee", bg_d1="#0e1615", bg_d2="#10201d",
        hl0="#eef4f3", hl1="#b4e5dd", hl2="#62cdbf", hl3="#1aa595", hl4="#0b7469",
        hd0="#192321", hd1="#16463f", hd2="#137568", hd3="#1fb09f", hd4="#6fe9d8",
        lang2="#3fbfb0", lang3="#a7e6dd",
        line_l="#e3ecea", line_d="#24302e", edge_d="#253230", stroke_l="#e1ebe9", stroke_l2="#dde8e6",
        empty_d="#2f3f3c", empty_l="#d6e4e1", muted_d="#a9bdb9", faint_d="#86a09b", ink_d="#eefaf8", ink2_d="#cfe3df"),
    "ocean": dict(
        accent="#2563eb", accent_dark="#7fabff", violet_card="#2563eb",
        blob1="#bfd7fe", blob2="#c7f0fb", blob3="#dcd3fe",
        ring1="#d3e3fe", ring2="#cdf3fb", ring3="#e0d8fe", pearl1="#e2ecff", pearl2="#d4f5fb", pearl3="#d6e0ff",
        bg_l1="#f2f6fd", bg_l2="#e3ebfa", bg_d1="#0e131f", bg_d2="#121b30",
        hl0="#eef2f9", hl1="#bdd3fb", hl2="#7fa9f6", hl3="#3b78ee", hl4="#1c4fd6",
        hd0="#192030", hd1="#1d3a6d", hd2="#2958bd", hd3="#4f86f2", hd4="#a3c4ff",
        lang2="#5f94f4", lang3="#b4cdfb",
        line_l="#e4eaf5", line_d="#232c40", edge_d="#253049", stroke_l="#e2e9f5", stroke_l2="#dde5f3",
        empty_d="#2e3a55", empty_l="#d5e0f2", muted_d="#aab6cf", faint_d="#8693ad", ink_d="#f0f5ff", ink2_d="#d0dbf0"),
    "sunset": dict(
        accent="#e2541b", accent_dark="#ff9a63", violet_card="#ea580c",
        blob1="#fed5b5", blob2="#fcd0da", blob3="#fde5a6",
        ring1="#ffe1cb", ring2="#fdd8e0", ring3="#feeab9", pearl1="#ffeadb", pearl2="#fde0e6", pearl3="#fff0c9",
        bg_l1="#fcf6f2", bg_l2="#f8ebe2", bg_d1="#18120f", bg_d2="#221813",
        hl0="#f8f1ec", hl1="#fcd3b6", hl2="#f99c61", hl3="#ec6a20", hl4="#bf400c",
        hd0="#251c17", hd1="#57301a", hd2="#8c4519", hd3="#d8661d", hd4="#ffb886",
        lang2="#f38a4c", lang3="#fbc7a4",
        line_l="#f1e7e0", line_d="#33271f", edge_d="#352920", stroke_l="#f0e5de", stroke_l2="#ede0d8",
        empty_d="#45362c", empty_l="#eaddd3", muted_d="#c8b6aa", faint_d="#a69283", ink_d="#fff6f0", ink2_d="#ebd9cd"),
    "graphite": dict(
        accent="#4d7c0f", accent_dark="#b5ec4f", violet_card="#65a30d",
        blob1="#e2e8d4", blob2="#e7e5e4", blob3="#dfe8c8",
        ring1="#eef2e2", ring2="#efedeb", ring3="#e6eed2", pearl1="#f4f6ec", pearl2="#f1efed", pearl3="#e9f0d8",
        bg_l1="#f6f6f4", bg_l2="#ececea", bg_d1="#111111", bg_d2="#18181a",
        hl0="#f0f0ee", hl1="#d6ef9e", hl2="#a4d64a", hl3="#6aa312", hl4="#3f6212",
        hd0="#1c1c1e", hd1="#2f4214", hd2="#4b7a10", hd3="#7fc31a", hd4="#c4f075",
        lang2="#86b83b", lang3="#cfe6a6",
        line_l="#e8e8e5", line_d="#2a2a2c", edge_d="#2c2c2e", stroke_l="#e6e6e3", stroke_l2="#e1e1de",
        empty_d="#3a3a3d", empty_l="#dddddb", muted_d="#b5b5b2", faint_d="#909090", ink_d="#f6f6f4", ink2_d="#dadad7"),
}
PALETTE = os.environ.get("PROFILE_PALETTE", "ocean")


def recolor(svg_text, palette=None):
    pal = PALETTES[palette or PALETTE]
    for slot, new in pal.items():
        old = SLOTS[slot]
        svg_text = svg_text.replace(old, new).replace(old.upper(), new)
    return svg_text


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
    return recolor(
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
    dict(slug="tealeaf", name="Tea Leaf Disease Detection", kind="RESEARCH · UNDER REVIEW, SPRINGER", illo=illo_leaf,
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


# ── repository cards (live data) ────────────────────────────────────────────
# Shown first, in this order; every other public repo follows, newest push first.
PRIORITY = ["TOP", "Swasthya-Sathi", "Mansakha", "FarmConnect"]
HIDDEN = {"Farm-Connect-"}   # teammate copies I'd rather not link to
# Private repos to show anyway: (name, link visitors get, description)
PRIVATE_SHOWCASE = [
    ("FarmConnect", "https://www.krishmehta.xyz/#work",
     "A marketplace where farmers sell directly to buyers, with a dashboard for managing listings and orders."),
]
REPO_FIELDS = """name description url stargazerCount forkCount pushedAt owner { login }
  primaryLanguage { name }
  languages(first: 5, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }"""
LANG_TINT = {
    "Python": (("#e3e9f7", "#eee8fb"), ("#1c2233", "#221e33")),
    "TypeScript": (("#e2ebfb", "#ece6fa"), ("#1b2236", "#211e34")),
    "JavaScript": (("#f8f3dc", "#eee8fb"), ("#2a2720", "#221e33")),
    "HTML": (("#fbeee8", "#f3ebdf"), ("#2a2226", "#2a2420")),
    "Jupyter Notebook": (("#f7ecdf", "#eee8fb"), ("#2a2420", "#221e33")),
}
SHORT_LANG = {"Jupyter Notebook": "Notebook", "TypeScript": "TypeScript"}
CACHE = OUT / "repos.json"


def gql(token, query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req, timeout=30))["data"]


def flatten(cal):
    return {"total": cal["totalContributions"],
            "days": [d for wk in cal["weeks"] for d in wk["contributionDays"]]}


SHOW_PAST_YEARS = False   # flip to True to add a "Previous years" toggle under the heatmap


def fetch_past_years(token):
    """One calendar per finished year, newest first (current year is the rolling card)."""
    years = gql(token, f'query {{ user(login: "{LOGIN}") {{ contributionsCollection {{ contributionYears }} }} }}')
    this_year = date.today().year
    past = [y for y in years["user"]["contributionsCollection"]["contributionYears"] if y < this_year]
    if not past:
        return []
    parts = "\n".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
        f'{{ contributionCalendar {{ totalContributions weeks {{ contributionDays {{ contributionCount date }} }} }} }}'
        for y in past
    )
    user = gql(token, f'query {{ user(login: "{LOGIN}") {{ {parts} }} }}')["user"]
    out = []
    for y in sorted(past, reverse=True):
        cal = flatten(user[f"y{y}"]["contributionCalendar"])
        cal["days"] = [d for d in cal["days"] if d["date"].startswith(str(y))]
        out.append(dict(cal, year=y))
    return out


def fetch_repos():
    """All public, non-fork repos (minus this profile repo) plus the contribution calendar."""
    token = os.environ.get("GH_TOKEN")
    if not token:
        return json.loads(CACHE.read_text()) if CACHE.exists() else None
    query = f"""query {{
      user(login: "{LOGIN}") {{
        repositories(privacy: PUBLIC, isFork: false, first: 50, orderBy: {{field: PUSHED_AT, direction: DESC}}) {{
          nodes {{ {REPO_FIELDS} }}
        }}
        farm: repository(name: "FarmConnect") {{ {REPO_FIELDS} }}
        contributionsCollection {{
          contributionCalendar {{ totalContributions weeks {{ contributionDays {{ contributionCount date }} }} }}
        }}
      }}
    }}"""
    user = gql(token, query)["user"]
    repos = [r for r in user["repositories"]["nodes"]
             if r["name"].lower() != LOGIN.lower() and r["name"] not in HIDDEN]
    for name, link, desc in PRIVATE_SHOWCASE:
        node = user.get("farm") if name == "FarmConnect" else None
        if node:
            repos.append(dict(node, url=link, description=node.get("description") or desc))
    repos.sort(key=lambda r: (PRIORITY.index(r["name"]) if r["name"] in PRIORITY else len(PRIORITY)))
    cal = user["contributionsCollection"]["contributionCalendar"]
    data = {"repos": repos, "calendar": flatten(cal), "years": fetch_past_years(token) if SHOW_PAST_YEARS else []}
    CACHE.write_text(json.dumps(data, indent=1))   # fallback for runs where the API fails
    return data


def seeded(text):
    """Tiny deterministic PRNG so each repo always gets the same code-line pattern."""
    x = sum(ord(c) * (i + 1) for i, c in enumerate(text)) or 1
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x / 0x7FFFFFFF


def icon_star(x, y, c):
    return (f'<path transform="translate({x} {y})" d="M7 0.8l1.9 3.9 4.3.6-3.1 3 .7 4.3L7 10.6l-3.8 2 .7-4.3-3.1-3 '
            f'4.3-.6z" fill="none" stroke="{c}" stroke-width="1.4" stroke-linejoin="round"/>')


def icon_fork(x, y, c):
    return (f'<g transform="translate({x} {y})" fill="none" stroke="{c}" stroke-width="1.4">'
            '<circle cx="3" cy="2.5" r="1.8"/><circle cx="11" cy="2.5" r="1.8"/><circle cx="7" cy="12" r="1.8"/>'
            '<path d="M3 4.3v1.5c0 1.6 1 2.4 2.5 2.4h3c1.5 0 2.5-.8 2.5-2.4V4.3M7 8.2v2"/></g>')


# Each card gets its own hue so the grid doesn't read as one repeated tile.
# (accent, second, third, light bg pair, dark bg pair)
HUES = [
    ("#6b5cff", "#a99bff", "#d4ccff", ("#ece9ff", "#f4e9fb"), ("#221d3d", "#1b1830")),   # violet
    ("#ff6b57", "#ffa48f", "#ffd3c8", ("#ffece7", "#fdf3e6"), ("#3a1f22", "#2a1b22")),   # coral
    ("#10b3a3", "#5fd4c7", "#b5ece5", ("#e2f6f3", "#eaf4fb"), ("#12302d", "#152330")),   # teal
    ("#f2a20f", "#f8c45a", "#fbe2a9", ("#fff4dc", "#fbefe6"), ("#33270f", "#2a2016")),   # amber
    ("#3b82f6", "#7fb0fa", "#c3dafd", ("#e6effe", "#ecebfd"), ("#16233d", "#1a1d36")),   # blue
    ("#e5489a", "#f08cc0", "#f8cde3", ("#fde8f2", "#f4ebfb"), ("#371a2b", "#261a2e")),   # pink
    ("#22a85a", "#6cd292", "#bfeccf", ("#e4f6ea", "#eef6e4"), ("#15301f", "#1b2a1c")),   # green
]


def lang_mix(r):
    edges = (r.get("languages") or {}).get("edges", [])
    total = sum(e["size"] for e in edges) or 1
    return [(e["node"]["name"], e["size"] / total) for e in edges if e["size"] / total >= 0.01][:4]


def visual_code(t, r, hue, rnd, dark):
    acc, acc2, acc3 = hue[0], hue[1], hue[2]
    owner = (r.get("owner") or {}).get("login") or LOGIN
    out = (f'<rect x="20" y="20" width="360" height="132" rx="12" fill="{"#ffffff" if not dark else "#000000"}" fill-opacity="{0.85 if not dark else 0.25}"/>'
           '<circle cx="36" cy="36" r="4.5" fill="#f28b82"/><circle cx="50" cy="36" r="4.5" fill="#fbd27a"/><circle cx="64" cy="36" r="4.5" fill="#8fd19e"/>'
           f'<text x="84" y="40" class="m" font-size="11" fill="{t["muted"]}">{esc((owner + "/" + r["name"])[:36])}</text>')
    palette = [acc, acc2, t["faint"], acc]
    for line in range(6):
        y = 60 + line * 15
        out += f'<text x="36" y="{y + 4}" class="m" font-size="9.5" fill="{t["faint"]}">{line + 1}</text>'
        x = 56 + 14 * (1 if 0 < line < 5 and next(rnd) > 0.4 else 0)
        for _ in range(1 + int(next(rnd) * 3)):
            seg = 22 + int(next(rnd) * 70)
            if x + seg > 360:
                break
            out += f'<rect x="{x}" y="{y - 3}" width="{seg}" height="6" rx="3" fill="{palette[int(next(rnd) * 4)]}"/>'
            x += seg + 8
    # donut in the card's own hue
    mix = lang_mix(r)
    cx, cy, rad, sw = 486, 72, 44, 14
    shades = [acc, acc2, acc3, t["faint"]]
    start = -90.0
    for i, (_, frac) in enumerate(mix):
        sweep = frac * 360
        if frac > 0.999:
            out += f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{shades[i]}" stroke-width="{sw}"/>'
        else:
            a0, a1 = math.radians(start), math.radians(start + sweep - 1.2)
            out += (f'<path d="M{cx + rad * math.cos(a0):.1f} {cy + rad * math.sin(a0):.1f} A{rad} {rad} 0 {1 if sweep > 180 else 0} 1 '
                    f'{cx + rad * math.cos(a1):.1f} {cy + rad * math.sin(a1):.1f}" fill="none" stroke="{shades[i]}" stroke-width="{sw}"/>')
        start += sweep
    if mix:
        out += (f'<text x="{cx}" y="{cy + 3}" text-anchor="middle" class="d6" font-size="20" fill="{t["ink"]}">{round(mix[0][1] * 100)}%</text>'
                f'<text x="{cx}" y="{cy + 19}" text-anchor="middle" class="m" font-size="9.5" fill="{t["muted"]}">{esc(SHORT_LANG.get(mix[0][0], mix[0][0])[:12])}</text>')
    return out


def visual_terminal(t, r, hue, rnd, dark):
    acc, acc2 = hue[0], hue[1]
    owner = (r.get("owner") or {}).get("login") or LOGIN
    mix = lang_mix(r)
    out = ('<rect x="20" y="18" width="572" height="138" rx="14" fill="#0f0e17"/>'
           '<circle cx="38" cy="36" r="4.5" fill="#f28b82"/><circle cx="52" cy="36" r="4.5" fill="#fbd27a"/><circle cx="66" cy="36" r="4.5" fill="#8fd19e"/>'
           f'<text x="40" y="66" class="m" font-size="13" fill="{acc2}">$ <tspan fill="#e9e7f5">git clone github.com/{esc((owner + "/" + r["name"])[:40])}</tspan></text>'
           f'<text x="40" y="90" class="m" font-size="13" fill="#8f8ca6">Receiving objects: 100% · done.</text>')
    x = 40
    for i, (name, frac) in enumerate(mix[:3]):
        label = f"{SHORT_LANG.get(name, name)} {round(frac * 100)}%"
        wdt = 24 + len(label) * 7.9
        col = [acc, acc2, "#8f8ca6"][i]
        out += (f'<rect x="{x}" y="108" width="{wdt:.0f}" height="28" rx="8" fill="{col}" fill-opacity="0.18"/>'
                f'<circle cx="{x + 13}" cy="122" r="4" fill="{col}"/>'
                f'<text x="{x + 23}" y="127" class="m" font-size="12" fill="#e9e7f5">{esc(label)}</text>')
        x += wdt + 8
    out += f'<rect x="{x + 4}" y="112" width="9" height="18" fill="{acc2}"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>'
    return out


def visual_monogram(t, r, hue, rnd, dark):
    acc, acc2, acc3 = hue[0], hue[1], hue[2]
    words = [w for w in r["name"].replace("_", "-").split("-") if w and w.lower() != "krishmehta"]
    mono = (words[0][:2] if len(words) == 1 else words[0][0] + words[1][0]).upper()
    uid = "mg" + "".join(ch for ch in r["name"] if ch.isalnum())[:10]
    out = (f'<defs><linearGradient id="{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{acc}"/>'
           f'<stop offset="1" stop-color="{acc2}"/></linearGradient></defs>'
           f'<text x="40" y="128" class="d7" font-size="128" letter-spacing="-6" fill="url(#{uid})">{esc(mono)}</text>')
    y = 44
    for name, frac in lang_mix(r)[:3]:
        out += (f'<text x="330" y="{y + 12}" class="s5" font-size="14" fill="{t["ink2"]}">{esc(SHORT_LANG.get(name, name))}</text>'
                f'<text x="580" y="{y + 12}" text-anchor="end" class="m" font-size="12" fill="{t["muted"]}">{round(frac * 100)}%</text>'
                f'<rect x="330" y="{y + 20}" width="250" height="8" rx="4" fill="{acc3}" fill-opacity="{0.35 if dark else 0.6}"/>'
                f'<rect x="330" y="{y + 20}" width="{max(8, 250 * frac):.0f}" height="8" rx="4" fill="{acc}"/>')
        y += 40
    return out


def visual_graph(t, r, hue, rnd, dark):
    acc, acc2, acc3 = hue[0], hue[1], hue[2]
    out = ""
    # a main line with two feature branches that merge back, dots as commits
    main_y, b1_y, b2_y = 96, 52, 138
    out += f'<line x1="36" y1="{main_y}" x2="576" y2="{main_y}" stroke="{acc}" stroke-width="4" stroke-linecap="round"/>'
    out += (f'<path d="M110 {main_y} C140 {main_y} 140 {b1_y} 170 {b1_y} L300 {b1_y} C330 {b1_y} 330 {main_y} 360 {main_y}" '
            f'fill="none" stroke="{acc2}" stroke-width="4" stroke-linecap="round"/>')
    out += (f'<path d="M330 {main_y} C360 {main_y} 360 {b2_y} 390 {b2_y} L480 {b2_y} C510 {b2_y} 510 {main_y} 540 {main_y}" '
            f'fill="none" stroke="{acc3}" stroke-width="4" stroke-linecap="round"/>')
    for x in (36, 110, 230, 360, 450, 540, 576):
        out += f'<circle cx="{x}" cy="{main_y}" r="8" fill="{t["bg1"]}" stroke="{acc}" stroke-width="3.5"/>'
    for x in (200, 260):
        out += f'<circle cx="{x}" cy="{b1_y}" r="7" fill="{t["bg1"]}" stroke="{acc2}" stroke-width="3.5"/>'
    for x in (420,):
        out += f'<circle cx="{x}" cy="{b2_y}" r="7" fill="{t["bg1"]}" stroke="{acc3}" stroke-width="3.5"/>'
    out += f'<text x="36" y="40" class="m" font-size="11" fill="{t["muted"]}">main</text>'
    return out


VISUALS = [visual_code, visual_terminal, visual_monogram, visual_graph]


def repo_card(t, r, dark, idx):
    w, h = 640, 340
    hue = HUES[idx % len(HUES)]
    acc = hue[0]
    c1, c2 = hue[4] if dark else hue[3]
    # rotate visual styles; offset per row so cards side by side never share a style
    visual = VISUALS[(idx + (idx // 2)) % len(VISUALS)]
    lang = (r.get("primaryLanguage") or {}).get("name", "Code")
    uid = f"r{idx}"
    rnd = seeded(r["name"])

    updated = date.fromisoformat(r["pushedAt"][:10]).strftime("%b %Y").upper()
    owner = (r.get("owner") or {}).get("login", LOGIN)
    team = owner.lower() != LOGIN.lower()
    if team and not r.get("description"):
        r = dict(r, description=f"Team project I contributed to, hosted by @{owner}.")

    body = (
        f'<defs><clipPath id="c{uid}"><rect width="{w}" height="{h}" rx="26"/></clipPath>'
        f'<linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
        f'<g clip-path="url(#c{uid})">'
        f'<rect width="{w}" height="{h}" fill="{t["bg1"]}"/>'
        f'<rect width="{w}" height="{h}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}"/>'
        f'<rect x="14" y="14" width="{w - 28}" height="172" rx="18" fill="url(#g{uid})"/>'
        f'<g transform="translate(14 14)">{visual(t, r, hue, rnd, dark)}</g>'
        f'<rect x="30" y="204" width="8" height="8" rx="2" fill="{acc}"/>'
        f'<text x="46" y="212" class="m" font-size="12" letter-spacing="1.2" fill="{t["faint"]}">{esc(lang.upper())} · UPDATED {updated}{" · WITH @" + esc(owner.upper()) if team else ""}</text>'
        f'<text x="28" y="246" class="d6" font-size="25" letter-spacing="-0.5" fill="{t["ink"]}">{esc(r["name"])}</text>'
        f'<text x="{w - 34}" y="246" text-anchor="end" class="d6" font-size="24" fill="{acc}">↗</text>'
    )
    lines = wrap(r.get("description") or "", 78)
    if len(lines) > 2:   # keep cards even: two lines, then an ellipsis
        lines = [lines[0], lines[1].rstrip(" ,.:;") + "…"]
    for i, line in enumerate(lines):
        body += f'<text x="30" y="{274 + i * 21}" class="s4" font-size="14.5" fill="{t["muted"]}">{esc(line)}</text>'
    body += (
        icon_star(30, 308, t["muted"]) + f'<text x="50" y="320" class="s5" font-size="13" fill="{t["ink2"]}">{r["stargazerCount"]}</text>'
        + icon_fork(82, 308, t["muted"]) + f'<text x="102" y="320" class="s5" font-size="13" fill="{t["ink2"]}">{r["forkCount"]}</text>'
        + f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="26" fill="none" stroke="{t["edge"]}"/></g>'
    )
    return svg(w, h, f'{r["name"]}: {r.get("description") or ""}', body,
               ["display-700", "display-600", "sans-400", "sans-500", "mono-500"])


# ── contribution heatmap (live data) ─────────────────────────────────────────
def streaks(days):
    longest = current = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    for d in reversed(days):
        if d["contributionCount"] > 0:
            current += 1
        elif current or d is not days[-1]:   # today may still be empty
            break
    return longest, current


def heatmap_card(t, cal, dark, year=None):
    w, h = 1280, 440
    days = cal["days"] if year else cal["days"][-371:]
    soft = dict(t, blob=t["blob"] * 0.4)
    body = backdrop(soft, w, h, [(80, 460, 150, "#cfc3ff"), (1250, -20, 140, "#f5cbe9")], "hm")
    body += f'<rect width="{w}" height="{h}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}"/>'

    longest, current = streaks(days)
    best = max(days, key=lambda d: d["contributionCount"])
    active = sum(1 for d in days if d["contributionCount"] > 0)
    if year:   # a finished year has no "current" streak; show its busiest month instead
        months = {}
        for d in days:
            months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["contributionCount"]
        busiest = max(months, key=months.get) if months else f"{year}-01"
        fourth = (date.fromisoformat(busiest + "-01").strftime("%b"), "busiest month")
    else:
        fourth = (f"{current}d", "current streak")
    stats = [(f'{cal["total"]:,}', "contributions"), (str(active), "active days"),
             (f"{longest}d", "longest streak"), fourth,
             (str(best["contributionCount"]), "best day")]
    title = f"CONTRIBUTIONS · {year}" if year else "CONTRIBUTIONS · LAST 12 MONTHS"
    body += f'<text x="56" y="62" class="m" font-size="13" letter-spacing="1.2" fill="{t["muted"]}">{title}</text>'
    for i, (v, l) in enumerate(stats):
        x = 56 + i * 200
        body += (f'<text x="{x}" y="116" class="d6" font-size="38" letter-spacing="-1" fill="{t["ink"]}">{v}</text>'
                 f'<text x="{x + 2}" y="142" class="s4" font-size="14.5" fill="{t["ink2"]}">{l}</text>')

    # the grid: big cells, visible empty days (outlined), readable labels
    x0, y0, cell, gap = 104, 196, 16, 4.6
    step = cell + gap
    start = date.fromisoformat(days[0]["date"])
    offset = (start.weekday() + 1) % 7          # GitHub weeks start on Sunday
    peak = max(d["contributionCount"] for d in days) or 1
    empty_stroke = "#3d3955" if dark else "#dcd7ee"
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        body += f'<text x="{x0 - 14}" y="{y0 + row * step + 12}" text-anchor="end" class="m" font-size="12.5" fill="{t["muted"]}">{label}</text>'
    last_month = None
    for i, d in enumerate(days):
        k = i + offset
        col, row = k // 7, k % 7
        n = d["contributionCount"]
        lvl = 0 if n == 0 else min(4, 1 + int(3.999 * (n / peak) ** 0.5))
        x, y = x0 + col * step, y0 + row * step
        stroke = f' stroke="{empty_stroke}" stroke-width="1"' if lvl == 0 else ""
        body += f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="4" fill="{t["heat"][lvl]}"{stroke}/>'
        dt = date.fromisoformat(d["date"])
        if row == 0 and dt.day <= 7 and dt.month != last_month:
            body += f'<text x="{x:.1f}" y="{y0 - 14}" class="m" font-size="13" fill="{t["ink2"]}">{dt.strftime("%b")}</text>'
            last_month = dt.month

    ly = y0 + 7 * step + 22
    lx = w - 56 - (5 * 22 + 84)
    body += f'<text x="{lx}" y="{ly + 12}" class="m" font-size="12.5" fill="{t["muted"]}">less</text>'
    for i, c in enumerate(t["heat"]):
        stroke = f' stroke="{empty_stroke}"' if i == 0 else ""
        body += f'<rect x="{lx + 40 + i * 22}" y="{ly}" width="16" height="16" rx="4" fill="{c}"{stroke}/>'
    body += f'<text x="{lx + 40 + 5 * 22 + 4}" y="{ly + 12}" class="m" font-size="12.5" fill="{t["muted"]}">more</text>'
    body += (f'<text x="{x0}" y="{ly + 12}" class="s4" font-size="13.5" fill="{t["muted"]}">'
             + (f'Best day: {best["contributionCount"]} contributions on {date.fromisoformat(best["date"]).strftime("%d %b %Y")}'
                if best["contributionCount"] else "No contributions this year") + '</text>')
    body += frame(t, w, h)
    return svg(w, h, f'{cal["total"]} contributions in {year or "the last 12 months"}', body,
               ["display-600", "sans-400", "mono-500"])


# ── LeetCode card (live data) ────────────────────────────────────────────────
LC_USER = "_krish_mehta_"
LC_CACHE = OUT / "leetcode.json"
LC_QUERY = """query($u: String!) {
  allQuestionsCount { difficulty count }
  matchedUser(username: $u) {
    profile { ranking }
    submitStats { acSubmissionNum { difficulty count submissions } totalSubmissionNum { difficulty count submissions } }
  }
  recentAcSubmissionList(username: $u, limit: 3) { title timestamp }
}"""
LC_COLORS = {"Easy": "#1cbaba", "Medium": "#ffb11b", "Hard": "#f0484a"}


def fetch_leetcode():
    try:
        req = urllib.request.Request(
            "https://leetcode.com/graphql",
            data=json.dumps({"query": LC_QUERY, "variables": {"u": LC_USER}}).encode(),
            headers={"Content-Type": "application/json", "Referer": f"https://leetcode.com/u/{LC_USER}/",
                     "User-Agent": "Mozilla/5.0 (profile-readme-builder)"},
        )
        data = json.load(urllib.request.urlopen(req, timeout=30))["data"]
        if not data.get("matchedUser"):
            raise ValueError("user not found")
        LC_CACHE.write_text(json.dumps(data, indent=1))
        return data
    except Exception as e:  # LeetCode sometimes blocks CI runners; fall back to the last good data
        print("leetcode fetch failed, using cache:", e)
        return json.loads(LC_CACHE.read_text()) if LC_CACHE.exists() else None


def leetcode_card(t, d):
    w, h = 1280, 380
    totals = {q["difficulty"]: q["count"] for q in d["allQuestionsCount"]}
    solved = {q["difficulty"]: q["count"] for q in d["matchedUser"]["submitStats"]["acSubmissionNum"]}
    ac = {q["difficulty"]: q["submissions"] for q in d["matchedUser"]["submitStats"]["acSubmissionNum"]}
    sub = {q["difficulty"]: q["submissions"] for q in d["matchedUser"]["submitStats"]["totalSubmissionNum"]}
    rank = d["matchedUser"]["profile"]["ranking"]

    soft = dict(t, blob=t["blob"] * 0.5)
    body = backdrop(soft, w, h, [(150, 380, 150, "#bfe9e6"), (1230, 0, 140, "#f5cbe9")], "lc")
    body += f'<rect width="{w}" height="{h}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}"/>'
    body += (f'<text x="56" y="66" class="m" font-size="13" letter-spacing="1.2" fill="{t["muted"]}">'
             f'LEETCODE · @{esc(LC_USER)}</text>')

    # difficulty ring
    cx, cy, rad, sw = 196, 214, 96, 22
    body += f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{t["line"]}" stroke-width="{sw}"/>'
    total_solved = max(1, solved.get("All", 0))
    start = -90.0
    for diff in ("Easy", "Medium", "Hard"):
        frac = solved.get(diff, 0) / total_solved
        if frac <= 0:
            continue
        sweep = frac * 360 - 3
        a0, a1 = math.radians(start + 1.5), math.radians(start + 1.5 + sweep)
        x0, y0 = cx + rad * math.cos(a0), cy + rad * math.sin(a0)
        x1, y1 = cx + rad * math.cos(a1), cy + rad * math.sin(a1)
        body += (f'<path d="M{x0:.1f} {y0:.1f} A{rad} {rad} 0 {1 if sweep > 180 else 0} 1 {x1:.1f} {y1:.1f}" '
                 f'fill="none" stroke="{LC_COLORS[diff]}" stroke-width="{sw}" stroke-linecap="round"/>')
        start += frac * 360
    body += (f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" class="d7" font-size="64" letter-spacing="-2" fill="{t["ink"]}">{solved.get("All", 0)}</text>'
             f'<text x="{cx}" y="{cy + 40}" text-anchor="middle" class="s5" font-size="15" fill="{t["muted"]}">solved</text>')

    # per-difficulty rows (bar = share of what I've solved, totals shown alongside)
    peak = max(1, max(solved.get(k, 0) for k in ("Easy", "Medium", "Hard")))
    for i, diff in enumerate(("Easy", "Medium", "Hard")):
        y = 140 + i * 72
        n = solved.get(diff, 0)
        body += (
            f'<circle cx="{358}" cy="{y - 6}" r="6" fill="{LC_COLORS[diff]}"/>'
            f'<text x="374" y="{y}" class="s5" font-size="17" fill="{t["ink2"]}">{diff}</text>'
            f'<text x="742" y="{y}" text-anchor="end" class="d6" font-size="26" fill="{t["ink"]}">{n}'
            f'<tspan class="s4" font-size="15" fill="{t["faint"]}"> / {totals.get(diff, 0):,}</tspan></text>'
            f'<rect x="352" y="{y + 14}" width="390" height="9" rx="4.5" fill="{t["line"]}"/>'
            f'<rect x="352" y="{y + 14}" width="{max(9, 390 * n / peak):.0f}" height="9" rx="4.5" fill="{LC_COLORS[diff]}"/>'
        )
    body += f'<line x1="800" y1="56" x2="800" y2="{h - 56}" stroke="{t["line"]}"/>'

    # headline stats + recent problems
    body += (
        f'<text x="844" y="132" class="d6" font-size="40" letter-spacing="-1" fill="{t["ink"]}">#{rank:,}</text>'
        f'<text x="846" y="158" class="s4" font-size="14" fill="{t["muted"]}">global rank</text>'
        f'<text x="846" y="212" class="m" font-size="12" letter-spacing="1.2" fill="{t["muted"]}">RECENTLY SOLVED</text>'
    )
    for i, sub_ in enumerate((d.get("recentAcSubmissionList") or [])[:3]):
        y = 246 + i * 34
        when = date.fromtimestamp(int(sub_["timestamp"])).strftime("%d %b")
        title = sub_["title"] if len(sub_["title"]) <= 30 else sub_["title"][:29] + "…"
        body += (
            f'<circle cx="852" cy="{y - 5}" r="3.5" fill="{t["accent"]}"/>'
            f'<text x="866" y="{y}" class="s5" font-size="15" fill="{t["ink2"]}">{esc(title)}</text>'
            f'<text x="1224" y="{y}" text-anchor="end" class="m" font-size="12" fill="{t["faint"]}">{when}</text>'
        )
    body += frame(t, w, h)
    return svg(w, h, f'LeetCode: {solved.get("All", 0)} problems solved, global rank {rank:,}',
               body, ["display-700", "display-600", "sans-400", "sans-500", "mono-500"])


# ── skills card ──────────────────────────────────────────────────────────────
ICON_PATHS = json.loads((ROOT / "icons" / "skills.json").read_text())
# (label, group, simple-icons slug or custom glyph, colour)
SKILLS = [
    ("Python", "LANGUAGE", "python", "#3776AB"),
    ("Java", "LANGUAGE", "openjdk", "#E76F00"),
    ("JavaScript", "LANGUAGE", "javascript", "#E3B90B"),
    ("TypeScript", "LANGUAGE", "typescript", "#3178C6"),
    ("React", "WEB", "react", "#2BB3D9"),
    ("Node.js", "WEB", "nodedotjs", "#4E9C3F"),
    ("Flask", "WEB", "flask", "#5B5B6B"),
    ("PostgreSQL", "DATABASE", "postgresql", "#336791"),
    ("MySQL", "DATABASE", "mysql", "#00758F"),
    ("Git", "TOOLS", "git", "#F05032"),
    ("YOLO", "AI / ML", "g:yolo", "#E5489A"),
    ("CNN", "AI / ML", "g:cnn", "#6B5CFF"),
    ("ViT", "AI / ML", "g:vit", "#10B3A3"),
    ("RL", "AI / ML", "g:rl", "#F2A20F"),
]
GLYPHS = {   # simple custom marks for concepts that have no logo (drawn in a 24x24 box)
    "yolo": '<rect x="2" y="4" width="13" height="11" rx="1.5" fill="none" stroke="C" stroke-width="2.2"/>'
            '<rect x="10" y="10" width="12" height="10" rx="1.5" fill="none" stroke="C" stroke-width="2.2"/>'
            '<rect x="2" y="1" width="7" height="3.4" rx="1" fill="C"/>',
    "cnn": ''.join(f'<rect x="{2 + c * 7}" y="{2 + r * 7}" width="5.5" height="5.5" rx="1.2" fill="C" opacity="{0.35 + 0.2 * ((r + c) % 3)}"/>'
                   for r in range(3) for c in range(3)),
    "vit": ''.join(f'<rect x="{1 + c * 6}" y="{6 + r * 6}" width="4.6" height="4.6" rx="1" fill="C"/>' for r in range(2) for c in range(4))
           + '<path d="M3 4 Q12 -2 21 4" fill="none" stroke="C" stroke-width="1.8"/>',
    "rl": '<path d="M5 12a7 7 0 1 1 3 5.7" fill="none" stroke="C" stroke-width="2.4" stroke-linecap="round"/>'
          '<path d="M3 15l2.2 3.4 3.6-2" fill="none" stroke="C" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
          '<circle cx="12" cy="12" r="2.6" fill="C"/>',
}


def lighten(hex_color, amount):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (round(v + (255 - v) * amount) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def skills_card(t, dark):
    cols, tw, th, gap = 7, 156, 132, 12
    w = 1280
    x0 = (w - (cols * tw + (cols - 1) * gap)) // 2
    rows = (len(SKILLS) + cols - 1) // cols
    top = 36
    h = top + rows * th + (rows - 1) * gap + 36
    soft = dict(t, blob=t["blob"] * 0.45)
    body = backdrop(soft, w, h, [(1220, -10, 140, "#cfc3ff"), (40, h + 20, 130, "#c3d8ff")], "sk")
    body += f'<rect width="{w}" height="{h}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}"/>'
    for i, (label, group, icon, color) in enumerate(SKILLS):
        col, row = i % cols, i // cols
        x, y = x0 + col * (tw + gap), top + row * (th + gap)
        cx, cy = x + tw / 2, y + 48
        body += (f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="20" fill="#ffffff" fill-opacity="{0.8 if not dark else 0.05}" '
                 f'stroke="{t["edge"] if dark else "#e8e4f3"}"/>')
        if dark:
            # logos sit on a white badge in their true brand colour, like app icons
            body += f'<circle cx="{cx}" cy="{cy}" r="32" fill="#ffffff"/>'
        else:
            body += f'<circle cx="{cx}" cy="{cy}" r="32" fill="{color}" fill-opacity="0.13"/>'
        if icon.startswith("g:"):
            glyph = GLYPHS[icon[2:]].replace("C", color)
        else:
            glyph = f'<path d="{ICON_PATHS[icon]}" fill="{color}"/>'
        body += (f'<g transform="translate({cx - 18} {cy - 18}) scale(1.5)">{glyph}</g>'
                 f'<text x="{cx}" y="{y + 104}" text-anchor="middle" class="d6" font-size="16.5" fill="{t["ink"]}">{esc(label)}</text>'
                 f'<text x="{cx}" y="{y + 121}" text-anchor="middle" class="m" font-size="10" letter-spacing="1" fill="{t["faint"]}">{group}</text>')
    body += frame(t, w, h)
    return svg(w, h, "Skills: " + ", ".join(s[0] for s in SKILLS), body, ["display-600", "mono-500"])


# ── chat buttons (each its own link) ─────────────────────────────────────────
CHATS = [
    ("whatsapp", "WhatsApp", "#1faa53", "https://wa.me/918580838656"),
    ("instagram", "Instagram", "#d62976", "https://www.instagram.com/_krish_mehta_/"),
    ("telegram", "Telegram", "#26A5E4", "https://www.krishmehta.xyz/telegram"),
    ("discord", "Discord", "#5865F2", "https://www.krishmehta.xyz/discord"),
]


def chat_button(t, label, color, dark):
    w, h = 300, 56
    body = (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="28" fill="{color}" fill-opacity="{0.12 if not dark else 0.18}" '
            f'stroke="{color}" stroke-opacity="0.35"/>'
            f'<circle cx="34" cy="28" r="7" fill="{color}"/>'
            f'<text x="54" y="34" class="s5" font-size="17" fill="{t["ink"]}">{label}</text>'
            f'<text x="{w - 28}" y="35" text-anchor="end" class="d6" font-size="18" fill="{color}">↗</text>')
    return svg(w, h, f"Message me on {label}", body, ["sans-500", "display-600"])


# ── contact card ─────────────────────────────────────────────────────────────
CONTACT = [
    ("email", "Email", "krish.mehta.0105@gmail.com"),
    ("phone", "Phone", "+91 85808 38656"),
    ("pin", "Based in", "Chennai · from Shimla"),
]
CONTACT_ICONS = {
    "email": '<rect x="-10" y="-7.5" width="20" height="15" rx="3" fill="none" stroke="C" stroke-width="1.9"/><path d="M-9 -6 L0 1 L9 -6" fill="none" stroke="C" stroke-width="1.9"/>',
    "phone": '<path d="M-6.5 -9.5h3.6l1.8 4.6-2.3 1.5a11 11 0 0 0 5.8 5.8l1.5-2.3 4.6 1.8v3.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1-8.5-7.3a2 2 0 0 1 2-2.2z" fill="none" stroke="C" stroke-width="1.8" stroke-linejoin="round"/>',
    "pin": '<path d="M0 10s-7.5-6.6-7.5-12.2a7.5 7.5 0 0 1 15 0C7.5 3.4 0 10 0 10z" fill="none" stroke="C" stroke-width="1.9"/><circle cx="0" cy="-2.3" r="2.6" fill="none" stroke="C" stroke-width="1.9"/>',
}


def contact_card(t):
    w, h = 1280, 184
    soft = dict(t, blob=t["blob"] * 0.5)
    body = backdrop(soft, w, h, [(1180, 214, 140, "#cfc3ff"), (60, -30, 120, "#c3d8ff")], "ct")
    body += f'<rect width="{w}" height="{h}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}"/>'
    for i, (key, label, value) in enumerate(CONTACT):
        x = 56 + i * 400
        body += (
            f'<circle cx="{x + 26}" cy="92" r="26" fill="{t["accent"]}" fill-opacity="0.12"/>'
            f'<g transform="translate({x + 26} 92)">{CONTACT_ICONS[key].replace("C", t["accent"])}</g>'
            f'<text x="{x + 70}" y="84" class="m" font-size="12.5" letter-spacing="1.2" fill="{t["muted"]}">{label.upper()}</text>'
            f'<text x="{x + 70}" y="112" class="d6" font-size="23" letter-spacing="-0.4" fill="{t["ink"]}">{esc(value)}</text>'
        )
    body += frame(t, w, h)
    return svg(w, h, "Contact: krish.mehta.0105@gmail.com, +91 85808 38656, Chennai", body,
               ["display-600", "sans-400", "sans-500", "mono-500"])


# ── buttons ──────────────────────────────────────────────────────────────────
ICONS = {
    "website": '<circle cx="0" cy="0" r="8.5" fill="none" stroke="currentColor" stroke-width="1.8"/><ellipse rx="3.6" ry="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><line x1="-8.5" y1="0" x2="8.5" y2="0" stroke="currentColor" stroke-width="1.6"/>',
    "portfolio": '<rect x="-9.5" y="-5" width="19" height="13.5" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M-4 -5v-2.2a1.8 1.8 0 0 1 1.8-1.8h4.4a1.8 1.8 0 0 1 1.8 1.8V-5M-9.5 0.5h19" fill="none" stroke="currentColor" stroke-width="1.8"/>',
    "linkedin": '<rect x="-9" y="-9" width="18" height="18" rx="4" fill="currentColor"/><rect x="-5.5" y="-2" width="2.6" height="7.5" fill="BG"/><circle cx="-4.2" cy="-5" r="1.6" fill="BG"/><path d="M-1 -2h2.4v1.1c.5-.8 1.3-1.3 2.5-1.3 2 0 2.8 1.2 2.8 3.4v4.3H4.2V1.8c0-1.1-.3-1.8-1.3-1.8s-1.5.7-1.5 1.8v3.7H-1z" fill="BG"/>',
    "email": '<rect x="-9.5" y="-7" width="19" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M-8.5 -5.5 L0 1 L8.5 -5.5" fill="none" stroke="currentColor" stroke-width="1.8"/>',
    "leetcode": '<path d="M-4.5 -6.5 L-10 0 L-4.5 6.5 M4.5 -6.5 L10 0 L4.5 6.5 M1.6 -9 L-1.6 9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
}
BUTTON_LINKS = [
    ("portfolio", "Portfolio", "https://www.krishmehta.xyz"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/-krish-mehta-01-05-/"),
    ("email", "Email", "mailto:krish.mehta.0105@gmail.com"),
    ("leetcode", "LeetCode", "https://leetcode.com/u/_krish_mehta_/"),
]
BUTTONS = [(k, l) for k, l, _ in BUTTON_LINKS]


def button(t, key, label, dark):
    if key == "portfolio":
        return primary_button(t, key, label)
    w, h = 240, 64
    bg = t["bg1"]
    icon = ICONS[key].replace("currentColor", t["ink"]).replace("BG", bg)
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="32" fill="{bg}" stroke="{t["edge"] if dark else "#e3dff2"}"/>'
        f'<g transform="translate(36 32)">{icon}</g>'
        f'<text x="60" y="38" class="s5" font-size="18" fill="{t["ink"]}">{label}</text>'
        f'<text x="{w - 30}" y="39" text-anchor="end" class="d6" font-size="18" fill="{t["accent"]}">↗</text>'
    )
    return svg(w, h, label, body, ["sans-500", "display-600"])


def primary_button(t, key, label):
    """The one call to action: filled in the accent colour, with the address on it."""
    w, h = 420, 64
    accent = SLOTS["accent"]          # recoloured to the palette's accent on output
    icon = ICONS[key].replace("currentColor", "#ffffff")
    body = (
        f'<defs><linearGradient id="cta" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{SLOTS["lang2"]}"/></linearGradient></defs>'
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="32" fill="url(#cta)"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h / 2}" rx="31" fill="#ffffff" fill-opacity="0.08"/>'
        f'<g transform="translate(38 32)">{icon}</g>'
        f'<text x="64" y="39" class="d6" font-size="21" fill="#ffffff">{label}</text>'
        f'<text x="{w - 60}" y="38" text-anchor="end" class="m" font-size="14" fill="#ffffff" fill-opacity="0.85">krishmehta.xyz</text>'
        f'<circle cx="{w - 32}" cy="32" r="16" fill="#ffffff" fill-opacity="0.18"/>'
        f'<text x="{w - 32}" y="39" text-anchor="middle" class="d6" font-size="18" fill="#ffffff">↗</text>'
    )
    return svg(w, h, f"{label}: krishmehta.xyz", body, ["display-600", "mono-500"])


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    OUT.mkdir(exist_ok=True)
    try:
        data = fetch_repos()
    except Exception as e:  # never fail the whole build because the API hiccuped
        print("github fetch failed, using cache:", e)
        data = json.loads(CACHE.read_text()) if CACHE.exists() else None
    repos = (data or {}).get("repos", [])
    cal = (data or {}).get("calendar")
    years = (data or {}).get("years", []) if SHOW_PAST_YEARS else []
    lc = fetch_leetcode()
    # clear everything generated before, so removed sections/repos don't linger
    for old in OUT.glob("*.svg"):
        old.unlink()
    for mode, t in THEMES.items():
        dark = mode == "dark"
        (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf8")
        (OUT / f"h-repos-{mode}.svg").write_text(header(t, "05", "Repositories", "Read the", "code"), encoding="utf8")
        for i, r in enumerate(repos):
            (OUT / f"r-{i}-{mode}.svg").write_text(repo_card(t, r, dark, i), encoding="utf8")
        (OUT / f"h-skills-{mode}.svg").write_text(header(t, "01", "Skills", "What I", "work with"), encoding="utf8")
        (OUT / f"skills-{mode}.svg").write_text(skills_card(t, dark), encoding="utf8")
        for key, label, color, _ in CHATS:
            (OUT / f"c-{key}-{mode}.svg").write_text(chat_button(t, label, color, dark), encoding="utf8")
        (OUT / f"h-heat-{mode}.svg").write_text(header(t, "02", "Contributions", "A year of", "showing up"), encoding="utf8")
        if cal:
            (OUT / f"heatmap-{mode}.svg").write_text(heatmap_card(t, cal, dark), encoding="utf8")
        for past in years:
            (OUT / f"heatmap-{past['year']}-{mode}.svg").write_text(
                heatmap_card(t, past, dark, year=past["year"]), encoding="utf8")
        (OUT / f"h-lc-{mode}.svg").write_text(header(t, "03", "Problem solving", "Daily", "practice"), encoding="utf8")
        if lc:
            (OUT / f"leetcode-{mode}.svg").write_text(leetcode_card(t, lc), encoding="utf8")
        (OUT / f"h-contact-{mode}.svg").write_text(header(t, "04", "Contact", "Let's", "talk"), encoding="utf8")
        (OUT / f"contact-{mode}.svg").write_text(contact_card(t), encoding="utf8")
        for key, label in BUTTONS:
            (OUT / f"b-{key}-{mode}.svg").write_text(button(t, key, label, dark), encoding="utf8")
    write_readme(repos, bool(cal), bool(lc), [y["year"] for y in years])
    print("built", len(list(OUT.glob("*.svg"))), "svgs,", len(repos), "repos")


def pic(name, alt, width):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
            f'<img src="assets/{name}-light.svg" alt="{esc(alt)}" width="{width}"></picture>')


NL = chr(10)


def repo_grid(repos, offset=0):
    out = ""
    for i, r in enumerate(repos):
        n = i + offset
        out += f'<a href="{r["url"]}">{pic(f"r-{n}", r["name"] + ": " + (r.get("description") or ""), "49%")}</a>'
        out += (NL + "<br>" + NL) if i % 2 else NL
    return out


def write_readme(repos, has_cal, has_lc, past_years=()):
    """README is generated too, so the repo grid always matches the repos that exist."""
    buttons = NL.join(f'<a href="{url}">{pic(f"b-{key}", label, "34%" if key == "portfolio" else "20.5%")}</a>' for key, label, url in BUTTON_LINKS)
    parts = [
        '<a href="https://www.krishmehta.xyz">'
        + pic("hero", "Krish Mehta — I build technology for the people it usually forgets.", "100%") + "</a>",
        "**I'm Krish: part curiosity, part chaos, fully dependable when it counts.**",
        "My browser has more open tabs than my brain has excuses, I learn whatever the problem needs, and I'd "
        "rather laugh through a midnight deploy than panic through it. Easygoing most days. Locked in when it matters.",
    ]
    parts += [pic("h-skills", "Skills", "100%"), pic("skills", "Skills: " + ", ".join(sk[0] for sk in SKILLS), "100%")]
    if has_cal:
        parts += [pic("h-heat", "Contributions", "100%"),
                  pic("heatmap", "Contribution heatmap for the last 12 months", "100%")]
        if past_years:
            label = " · ".join(str(y) for y in past_years)
            inner = (NL + "<br>" + NL).join(pic(f"heatmap-{y}", f"Contributions in {y}", "100%") for y in past_years)
            parts.append("<details>" + NL + f"<summary><b>Previous years ({label})</b></summary>" + NL
                         + "<br>" + NL + NL + inner + NL + "</details>")
    if has_lc:
        parts += [pic("h-lc", "Problem solving", "100%"),
                  f'<a href="https://leetcode.com/u/{LC_USER}/">{pic("leetcode", "LeetCode stats", "100%")}</a>']
    parts += [pic("h-contact", "Contact", "100%"),
              '<a href="mailto:krish.mehta.0105@gmail.com">'
              + pic("contact", "Email krish.mehta.0105@gmail.com · Phone +91 85808 38656 · Chennai", "100%") + "</a>",
              '<p align="center">' + NL
              + NL.join(f'<a href="{url}">{pic(f"c-{key}", "Message me on " + label, "24%")}</a>' for key, label, _, url in CHATS)
              + NL + "<br>" + NL + buttons + NL + "</p>"]
    # Repositories come last: four on show, the rest behind a native <details> toggle
    top, rest = repos[:4], repos[4:]
    parts += [pic("h-repos", "Repositories", "100%"),
              '<p align="center">' + NL + repo_grid(top) + "</p>"]
    if rest:
        parts.append("<details>" + NL
                     + f"<summary><b>Show all {len(repos)} repositories</b></summary>" + NL + "<br>" + NL + NL
                     + '<p align="center">' + NL + repo_grid(rest, offset=4) + "</p>" + NL + "</details>")
    (ROOT / "README.md").write_text((NL + NL).join(parts) + NL, encoding="utf8")


if __name__ == "__main__":
    main()
