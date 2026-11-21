"""Draws every Valorant-themed card in assets/.

Run from the repo root:  python scripts/profile.py
Art comes from valorant-api.com, the Anton font from Google Fonts. Everything is
embedded as base64, because GitHub shows README SVGs through <img>, which blocks
any external file an SVG tries to load.
"""
import base64, io, os, urllib.request
from html import escape
from PIL import Image

CACHE = os.path.join(os.path.dirname(__file__), ".cache")
OUT = "assets"
os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# Valorant palette
BG, PANEL, PANEL2 = "#0F1923", "#16232E", "#1F2D3A"
RED, TEAL, CREAM, MUTED, LINE = "#FF4655", "#5CDBD3", "#ECE8E1", "#8B978F", "#2A3B49"

MEDIA = "https://media.valorant-api.com"
AGENTS = {
    "Sage": "569fdd95-4d10-43ab-ca70-79becc718b46",
    "Brimstone": "9f0d8ba9-4140-b941-57d3-a7ad57c6b417",
    "Cypher": "117ed9e3-49f3-6512-3ccf-0cada7e3823b",
    "Killjoy": "1e58de9c-4950-5125-93e9-a0aee9f98746",
    "Sova": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
    "Astra": "41fb69c1-4189-7b37-f117-bcaf1e96f1bf",
}
WEAPONS = {
    "Vandal": "9c82e19d-4575-0200-1a81-3eacf00cf872",
    "Phantom": "ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a",
    "Operator": "a03b24d3-4319-996d-0f8c-94bbfba1dfc7",
    "Spectre": "462080d1-4035-2937-7c09-27aa2a5c27a7",
    "Odin": "63e6c2b6-4a8e-869c-3d4c-e38355226584",
    "Sheriff": "e336c6b8-418d-9340-d77f-7a9e4cfe0702",
}
FONT_URL = "https://fonts.gstatic.com/s/anton/v27/1Ptgg87LROyAm3Kz-C8.woff2"


def fetch(url, name):
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": "profile-card-builder"})
        with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def img(url, name, width=None, height=None):
    """Download, shrink to display size, return a PNG data URI."""
    im = Image.open(fetch(url, name)).convert("RGBA")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if height and im.height > height:
        im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def agent_icon(name, size=160):
    return img(f"{MEDIA}/agents/{AGENTS[name]}/displayicon.png", f"{name}.png", size)


FONT = base64.b64encode(open(fetch(FONT_URL, "anton.woff2"), "rb").read()).decode()
STYLE = (
    "<style>"
    f"@font-face{{font-family:'Anton';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
    ".d{font-family:'Anton',Impact,sans-serif;letter-spacing:.5px}"
    ".s{font-family:'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif}"
    ".fade{opacity:0;animation:fade .5s ease forwards}"
    "@keyframes fade{to{opacity:1}}"
    ".grow{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1.2s cubic-bezier(.2,.8,.2,1) .4s forwards}"
    "@keyframes grow{to{transform:scaleX(1)}}"
    ".pulse{animation:pulse 2.2s ease-in-out infinite}"
    "@keyframes pulse{50%{opacity:.35}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.fade{opacity:1}.grow{transform:none}}"
    "</style>"
)


def svg(w, h, label, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>{STYLE}{body}</svg>'
    )


def t(x, y, s, cls="s", size=13, fill=CREAM, anchor="start", weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}"{w} {extra}>{escape(s)}</text>'
    )


def corner(x, y, w, h, c=RED, n=10):
    """Valorant-style corner ticks around a box."""
    return (
        f'<path d="M{x} {y+n}V{y}H{x+n}M{x+w-n} {y}H{x+w}V{y+n}M{x+w} {y+h-n}V{y+h}H{x+w-n}'
        f'M{x+n} {y+h}H{x}V{y+h-n}" fill="none" stroke="{c}" stroke-width="2"/>'
    )


def stripes(id_, w, h):
    return (
        f'<defs><pattern id="{id_}" width="14" height="14" patternUnits="userSpaceOnUse" '
        f'patternTransform="rotate(45)"><rect width="1" height="14" fill="#FFFFFF" opacity=".025"/>'
        f"</pattern></defs><rect width=\"{w}\" height=\"{h}\" fill=\"url(#{id_})\"/>"
    )


# ---------------------------------------------------------------- header
def header():
    W, H = 1000, 420
    sage_full = img(f"{MEDIA}/agents/{AGENTS['Sage']}/fullportrait.png", "sage_full.png", 560)
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>', stripes("hs", W, H)]
    b.append(
        '<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5">'
        f'<stop offset="0" stop-color="{TEAL}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="fadeR" x1="0" x2="1"><stop offset=".55" stop-color="#0F1923" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#0F1923"/></linearGradient>'
        f'<clipPath id="hc"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>'
    )
    # portrait side
    b.append('<g clip-path="url(#hc)">')
    b.append(t(-10, 300, "SAGE", "d", 210, TEAL, extra='opacity=".06"'))
    b.append('<ellipse cx="190" cy="210" rx="210" ry="210" fill="url(#glow)"/>')
    b.append(f'<image href="{sage_full}" x="-90" y="-20" width="560" height="560" class="fade"/>')
    b.append(f'<rect x="0" y="0" width="390" height="{H}" fill="url(#fadeR)"/>')
    b.append("</g>")
    b.append(f'<rect x="0" y="0" width="{W}" height="5" fill="{RED}"/>')

    X = 380
    b.append(f'<rect x="{X}" y="34" width="118" height="22" fill="{RED}"/>')
    b.append(t(X + 59, 50, "PLAYER CARD", "d", 13, CREAM, "middle", extra='letter-spacing="2"'))
    b.append(t(X + 130, 50, "AGENT LOCKED IN", "d", 13, TEAL, extra='letter-spacing="2"'))
    b.append(f'<circle cx="{X+252}" cy="45" r="4" fill="{TEAL}" class="pulse"/>')
    b.append(t(X - 3, 122, "AYAAN GOEL", "d", 64, CREAM))
    b.append(t(X + 330, 122, "#PDEU", "d", 26, MUTED))
    b.append(t(X, 150, "SAGE  //  SENTINEL  ·  FULL-STACK & BACKEND DEVELOPER", "d", 15, TEAL, extra='letter-spacing="1.5"'))

    stats = [
        ("ROLE", "Backend + Full-stack"),
        ("BASE", "PDEU, Gujarat"),
        ("PUBLIC REPOS", "26"),
        ("CGPA", "8.99 / 10"),
        ("CODEFORCES", "1228"),
        ("GFG SOLVED", "275+"),
    ]
    for i, (k, v) in enumerate(stats):
        cx, cy = X + (i % 3) * 196, 172 + (i // 3) * 62
        b.append(f'<g class="fade" style="animation-delay:{.15+i*.08:.2f}s">')
        b.append(f'<rect x="{cx}" y="{cy}" width="186" height="52" fill="{PANEL}" stroke="{LINE}"/>')
        b.append(f'<rect x="{cx}" y="{cy}" width="3" height="52" fill="{RED}"/>')
        b.append(t(cx + 14, cy + 19, k, "d", 11, MUTED, extra='letter-spacing="1.5"'))
        b.append(t(cx + 14, cy + 41, v, "s", 16, CREAM, weight=700))
        b.append("</g>")

    abilities = [
        ("C", "Barrier Orb", "grenade", "Holds up under load"),
        ("Q", "Slow Orb", "ability1", "ML that explains itself"),
        ("E", "Healing Orb", "ability2", "Builds that self-repair"),
        ("X", "Resurrection", "ultimate", "Revives legacy code"),
    ]
    for i, (key, name, slot, desc) in enumerate(abilities):
        ax, ay = X + i * 148, 312
        icon = img(f"{MEDIA}/agents/{AGENTS['Sage']}/abilities/{slot}/displayicon.png", f"ab_{slot}.png", 64)
        ult = key == "X"
        col = TEAL if ult else CREAM
        b.append(f'<g class="fade" style="animation-delay:{.6+i*.1:.2f}s">')
        b.append(f'<rect x="{ax}" y="{ay}" width="140" height="84" fill="{PANEL}" stroke="{TEAL if ult else LINE}"/>')
        if ult:
            b.append(f'<rect x="{ax}" y="{ay}" width="140" height="84" fill="none" stroke="{TEAL}" stroke-width="2" class="pulse"/>')
        b.append(f'<rect x="{ax+10}" y="{ay+12}" width="22" height="22" fill="{PANEL2}" stroke="{MUTED}"/>')
        b.append(t(ax + 21, ay + 28, key, "d", 13, col, "middle"))
        b.append(f'<image href="{icon}" x="{ax+40}" y="{ay+8}" width="30" height="30"/>')
        if ult:
            for d in range(7):
                b.append(f'<rect x="{ax+80+d*7}" y="{ay+22}" width="5" height="3" fill="{TEAL}"/>')
        b.append(t(ax + 10, ay + 58, name.upper(), "d", 14, col, extra='letter-spacing="1"'))
        b.append(t(ax + 10, ay + 74, desc, "s", 11.5, MUTED, weight=600))
        b.append("</g>")

    # team strip
    b.append(t(24, 400, "SQUAD", "d", 11, MUTED, extra='letter-spacing="2"'))
    for i, name in enumerate(["Sage", "Brimstone", "Cypher", "Killjoy", "Sova", "Astra"]):
        sx = 70 + i * 46
        b.append(f'<rect x="{sx}" y="378" width="38" height="30" fill="{PANEL2}" stroke="{TEAL if i==0 else LINE}"/>')
        b.append(f'<image href="{agent_icon(name, 64)}" x="{sx+5}" y="379" width="28" height="28"/>')
    b.append(corner(10, 10, W - 20, H - 20, RED, 18))
    return svg(W, H, "Player card: Ayaan Goel as Sage, full-stack and backend developer", "".join(b))


# ---------------------------------------------------------------- comms
def comms():
    W, H = 1000, 118
    lines = [
        "I build backend systems that stay correct when everyone clicks at once,",
        "and explainable ML that shows its work. Healing the build, holding the site.",
    ]
    css = ""
    b = [f'<rect x="4" y="4" width="{W-8}" height="{H-8}" rx="10" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>',
         f'<rect x="4" y="4" width="6" height="{H-8}" fill="{TEAL}"/>',
         t(30, 40, "[TEAM]", "d", 15, TEAL, extra='letter-spacing="1"'),
         t(92, 40, "Ayaan (Sage):", "d", 15, CREAM, extra='letter-spacing="1"'),
         f'<clipPath id="cb"><rect x="20" y="46" width="{W-40}" height="62"/></clipPath>']
    start = 0.3
    for i, ln in enumerate(lines):
        y = 72 + i * 26
        width = len(ln) * 8.3 + 20
        dur = len(ln) * 0.035
        css += (f".c{i}{{animation:ty{i} {dur:.2f}s steps({len(ln)}) {start:.2f}s forwards}}"
                f"@keyframes ty{i}{{to{{transform:translateX({width:.0f}px)}}}}")
        b.append(t(30, y, ln, "s", 15.5, CREAM, weight=600))
        b.append(f'<g clip-path="url(#cb)"><rect class="c{i}" x="26" y="{y-20}" width="{width:.0f}" height="26" fill="{PANEL}"/></g>')
        start += dur + 0.25
    css += f".cur{{opacity:0;animation:blink .9s steps(1) {start:.2f}s infinite}}@keyframes blink{{50%{{opacity:1}}}}"
    b.append(f'<rect class="cur" x="{W-40}" y="86" width="10" height="16" fill="{TEAL}"/>')
    b.append(t(W - 30, 40, "COMMS", "d", 12, MUTED, "end", extra='letter-spacing="2"'))
    return svg(W, H, "Team comms: " + " ".join(lines), f"<style>{css}</style>" + "".join(b))


# ---------------------------------------------------------------- loadout
def loadout():
    W, H = 1000, 330
    kit = [
        ("Python", "Vandal", "PRIMARY", 92, "ML, tooling, automation"),
        ("TypeScript", "Phantom", "PRIMARY", 85, "NestJS + Next.js apps"),
        ("Node.js", "Operator", "SNIPER", 84, "REST APIs, auth, workers"),
        ("PostgreSQL", "Odin", "HEAVY", 78, "Locks, versioning, Prisma"),
        ("React / Next.js", "Spectre", "SMG", 72, "Dashboards and UIs"),
        ("Java / C++", "Sheriff", "SIDEARM", 70, "DSA and competitive"),
    ]
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>', stripes("ls", W, H),
         f'<rect x="0" y="0" width="{W}" height="5" fill="{RED}"/>',
         t(28, 46, "LOADOUT", "d", 28, CREAM, extra='letter-spacing="2"'),
         t(150, 46, "BUY PHASE", "d", 13, TEAL, extra='letter-spacing="2"'),
         t(W - 28, 46, "◈ 9000 CREDS", "d", 15, CREAM, "end", extra='letter-spacing="1"')]
    for i, (tech, gun, cls, lvl, note) in enumerate(kit):
        x, y = 28 + (i % 3) * 318, 66 + (i // 3) * 128
        gimg = img(f"{MEDIA}/weapons/{WEAPONS[gun]}/displayicon.png", f"w_{gun}.png", height=60)
        b.append(f'<g class="fade" style="animation-delay:{.1+i*.08:.2f}s">')
        b.append(f'<rect x="{x}" y="{y}" width="302" height="116" fill="{PANEL}" stroke="{LINE}"/>')
        b.append(f'<image href="{gimg}" x="{x+150}" y="{y+12}" width="140" height="44" preserveAspectRatio="xMaxYMid meet" opacity=".9"/>')
        b.append(t(x + 14, y + 26, f"{gun.upper()} // {cls}", "d", 11, MUTED, extra='letter-spacing="1.5"'))
        b.append(t(x + 14, y + 56, tech.upper(), "d", 24, CREAM))
        b.append(t(x + 14, y + 78, note, "s", 12, MUTED, weight=600))
        b.append(f'<rect x="{x+14}" y="{y+92}" width="226" height="6" fill="{PANEL2}"/>')
        b.append(f'<rect x="{x+14}" y="{y+92}" width="{226*lvl/100:.0f}" height="6" fill="{TEAL if i else RED}" class="grow" style="animation-delay:{.4+i*.1:.2f}s"/>')
        b.append(t(x + 288, y + 99, f"{lvl}", "d", 15, CREAM, "end"))
        b.append("</g>")
    return svg(W, H, "Loadout: Python, TypeScript, Node.js, PostgreSQL, React/Next.js, Java/C++", "".join(b))


# ---------------------------------------------------------------- match cards
PROJECTS = [
    dict(slug="kitchen-ops", n=1, name="Kitchen Ops", agent="Brimstone", role="Controller",
         tags=["FULL-STACK", "CONCURRENCY"], status="LIVE",
         head="Runs a lunch kitchen's whole day: orders, cooking board, dispatch, billing.",
         bullets=["Row locks + version checks: one winner", "Money in cents, invoices never change", "Busiest day loads in 0.8 s live"],
         stats=[("99", "API ENDPOINTS"), ("45", "DB TABLES"), ("159", "TESTS IN CI")],
         tech="Next.js · NestJS · PostgreSQL · Prisma"),
    dict(slug="workzen", n=2, name="WorkZen", agent="Cypher", role="Sentinel",
         tags=["BACKEND", "PAYROLL"], status="SHIPPED",
         head="HR portal backend: attendance, leave and automated monthly payroll.",
         bullets=["Leave checks balance + date overlaps", "Pay runs: Draft → Validated → Paid", "Payslips from salary + attendance"],
         stats=[("51", "API ENDPOINTS"), ("4", "ROLES"), ("20,725", "ATTENDANCE ROWS")],
         tech="Node.js · TypeScript · MySQL · Prisma · JWT"),
    dict(slug="expense-mgmt", n=3, name="Expense Mgmt", agent="Killjoy", role="Sentinel",
         tags=["BACKEND", "WORKFLOW"], status="SHIPPED",
         head="Expense-claim system: employees submit, managers approve, admins set rules.",
         bullets=["Routes claims by amount ($50 / $200)", "Reads receipts with OCR", "Converts currency via cached rates"],
         stats=[("37", "API ENDPOINTS"), ("3", "ROLES"), ("3", "APPROVAL TIERS")],
         tech="Node.js · Express · SQLite · JWT · OCR"),
    dict(slug="resumagic", n=4, name="ResuMAGIC", agent="Sova", role="Initiator",
         tags=["GEN AI", "PARSING"], status="LIVE",
         head="Turns any resume into structured data with a chained Gemini pipeline.",
         bullets=["PDF, DOCX, HTML, TXT or a photo", "Maps job titles to O*NET standards", "Draws each career path in order"],
         stats=[("6", "FILE TYPES"), ("1,000+", "O*NET TITLES"), ("4", "SECTIONS PARSED")],
         tech="Python · LangChain · Gemini · Streamlit"),
    dict(slug="heritage3d", n=5, name="heritage3D", agent="Astra", role="Controller",
         tags=["3D VISION", "RESEARCH"], status="RESEARCH",
         head="How many photos does a good 3D scan of an artifact really need?",
         bullets=["COLMAP SfM → OpenMVS dense mesh", "Quality vs runtime, RAM and size", "Walkable web virtual museum"],
         stats=[("40", "ARTIFACTS"), ("5", "IMAGE LEVELS"), ("44", "EXHIBITS")],
         tech="Python · COLMAP · OpenMVS · GLB"),
    dict(slug="ml-heart-disease", n=6, name="Heart Risk ML", agent="Sage", role="Sentinel",
         tags=["ML", "HEALTHCARE"], status="COMPLETE",
         head="Predicts 10-year coronary heart disease on the Framingham study.",
         bullets=["Imputation, SMOTE, MI + RFE", "LR, SVM, Random Forest, XGBoost", "Voting + stacking ensembles, PCA"],
         stats=[("4,240", "PATIENTS"), ("15", "RISK FACTORS"), ("4", "MODEL FAMILIES")],
         tech="Python · scikit-learn · XGBoost · pandas"),
]


def wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    return out + [line]


def match(p):
    W, H = 490, 340
    live = p["status"] == "LIVE"
    b = [f'<defs><clipPath id="mc"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>',
         f'<g clip-path="url(#mc)"><rect width="{W}" height="{H}" fill="{BG}"/>', stripes(f"s{p['n']}", W, H),
         f'<rect width="{W}" height="54" fill="{PANEL2}"/>',
         f'<rect width="6" height="54" fill="{RED}"/>',
         f'<path d="M{W-110} 0H{W}V54H{W-130}Z" fill="{TEAL if live else RED}" opacity=".16"/></g>',
         t(22, 22, f"MATCH {p['n']:02d}", "d", 11, MUTED, extra='letter-spacing="2"'),
         t(22, 44, p["name"].upper(), "d", 22, CREAM, extra='letter-spacing="1"'),
         t(W - 20, 22, "VICTORY", "d", 11, MUTED, "end", extra='letter-spacing="2"'),
         t(W - 20, 44, p["status"], "d", 20, TEAL if live else RED, "end", extra='letter-spacing="1.5"')]
    if live:
        b.append(f'<circle cx="{W-20-len(p["status"])*11.5-12}" cy="37" r="4" fill="{TEAL}" class="pulse"/>')
    # agent panel
    b.append(f'<rect x="18" y="70" width="128" height="150" fill="{PANEL}" stroke="{LINE}"/>')
    b.append(f'<image href="{agent_icon(p["agent"], 200)}" x="30" y="78" width="104" height="104" class="fade"/>')
    b.append(f'<rect x="18" y="186" width="128" height="34" fill="{PANEL2}"/>')
    b.append(t(82, 201, p["agent"].upper(), "d", 13, CREAM, "middle", extra='letter-spacing="1"'))
    b.append(t(82, 214, p["role"].upper(), "d", 9, RED, "middle", extra='letter-spacing="1.5"'))
    b.append(corner(18, 70, 128, 150, TEAL, 8))
    # right side
    x = 162
    for tag in p["tags"]:
        w = len(tag) * 6.6 + 18
        b.append(f'<rect x="{x}" y="72" width="{w:.0f}" height="18" fill="none" stroke="{TEAL}"/>')
        b.append(t(x + w / 2, 85, tag, "d", 10, TEAL, "middle", extra='letter-spacing="1"'))
        x += w + 8
    for i, ln in enumerate(wrap(p["head"], 40)[:2]):
        b.append(t(162, 114 + i * 18, ln, "s", 14, CREAM, weight=600))
    for i, bl in enumerate(p["bullets"]):
        y = 160 + i * 21
        b.append(f'<rect x="162" y="{y-7}" width="6" height="6" fill="{RED}" transform="rotate(45 165 {y-4})"/>')
        b.append(t(176, y, bl, "s", 12.5, MUTED, weight=600))
    # scoreboard
    for i, (num, lab) in enumerate(p["stats"]):
        sx = 18 + i * 154
        b.append(f'<g class="fade" style="animation-delay:{.3+i*.12:.2f}s">')
        b.append(f'<rect x="{sx}" y="234" width="146" height="58" fill="{PANEL}" stroke="{LINE}"/>')
        b.append(f'<rect x="{sx}" y="234" width="146" height="2" fill="{TEAL if i==0 else RED}"/>')
        b.append(t(sx + 73, 266, num, "d", 26, CREAM, "middle"))
        b.append(t(sx + 73, 283, lab, "d", 9.5, MUTED, "middle", extra='letter-spacing="1.5"'))
        b.append("</g>")
    b.append(t(20, 318, p["tech"], "s", 12, MUTED, weight=600))
    b.append(corner(4, 4, W - 8, H - 8, RED, 12))
    label = f"Match {p['n']:02d}: {p['name']}. {p['head']}"
    return svg(W, H, label, "".join(b))


def write(name, s):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    print(f"{name}: {len(s)/1024:.0f} KB")


if __name__ == "__main__":
    write("header.svg", header())
    write("comms.svg", comms())
    write("loadout.svg", loadout())
    for p in PROJECTS:
        write(f"match-{p['n']:02d}-{p['slug']}.svg", match(p))
