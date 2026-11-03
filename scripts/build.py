#!/usr/bin/env python3
"""Rebuild the site and PDFs from data/games.json.  Run: python3 scripts/build.py"""
import html, json, pathlib
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / "pdf"
TITLE = "2026 AYSO Region 84 Champions Cup Invitational"
NAVY, GOLD = colors.HexColor("#0B2250"), colors.HexColor("#FDC917")
BAND, RULE, MUTED = colors.HexColor("#EEF1F7"), colors.HexColor("#D5DBE8"), colors.HexColor("#566079")
GIRLS = ["GU09", "GU10", "GU12", "GU14"]
BOYS = ["BU09", "BU10", "BU12", "BU14"]
PDF_NAME = "2026-champions-cup-"
FIELDS = ["World Cup SS1", "World Cup SS2", "Youth Athletic Park A", "Youth Athletic Park B", "Gilleran 1", "Beebe"]

pdfmetrics.registerFont(TTFont("Body", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Bold", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))


def div_name(d):
    return f"{'Girls' if d[0] == 'G' else 'Boys'} {int(d[2:])}U"


def field_name(f):
    return f"{f} (Marty Russo)" if f.startswith("Youth Athletic") else f


def field_slug(f):
    return "".join(ch if ch.isalnum() else "-" for ch in f.lower())


def short_div(d):
    return f"{d[0]}{int(d[2:])}U"


def day(g):
    dt = datetime.strptime(g["date"], "%Y-%m-%d")
    return f"{dt:%a} {dt.month}/{dt.day}"


def clock(g):
    dt = datetime.strptime(g["time"], "%H:%M")
    return f"{dt.hour % 12 or 12}:{dt.minute:02d} {'PM' if dt.hour >= 12 else 'AM'}"


def teams(g):
    return f"{g['home']} vs. {g['away']}" if g["away"] else g["home"]


def result(g):
    if g["home_score"] is not None and g["away_score"] is not None:
        r = f"{g['home_score']}-{g['away_score']}"
        return f"{r} ({g['note']})" if g["note"] else r
    return g["note"]


def winner(g):
    """Return 'home' or 'away'.  A tie on the score needs an explicit winner field."""
    if g.get("winner") in ("home", "away"):
        return g["winner"]
    hs, aws = g["home_score"], g["away_score"]
    if hs is None or aws is None or hs == aws:
        return None
    return "home" if hs > aws else "away"


def team_cell(g):
    w = winner(g)
    if not w:
        return teams(g)
    return [(g["home"], "Bold" if w == "home" else "Body", NAVY if w == "home" else MUTED),
            (" vs. ", "Body", MUTED),
            (g["away"], "Bold" if w == "away" else "Body", NAVY if w == "away" else MUTED)]


def teams_html(g):
    w, e = winner(g), html.escape
    if not w:
        return e(teams(g))
    side = lambda k: f'<span class="{"win" if w == k else "lose"}">{e(g[k])}</span>'
    return f'{side("home")} <span class="lose">vs.</span> {side("away")}'


def result_pdf(g):
    r = result(g)
    return r.replace(" (Forfeit)", " FF").replace("Forfeit", "FF").split(" (PK")[0] + (" PK" if "(PK" in r else "")


def result_html(g):
    w, r = winner(g), result(g)
    return f"{g[w]} wins {r}" if w else r


def sort_key(g):
    return (g["date"], g["time"], g["div"], g["field"])


# ---------- PDF ----------
def header(c, subtitle, updated, page_w, y_top):
    logo = ROOT / "assets" / "logo-256.png"
    c.drawImage(ImageReader(str(logo)), 36, y_top - 44, 46, 46, mask="auto")
    c.setFillColor(NAVY)
    c.setFont("Bold", 15)
    c.drawString(90, y_top - 16, TITLE)
    c.setFont("Body", 10.5)
    c.drawString(90, y_top - 31, subtitle)
    c.setFillColor(MUTED)
    c.setFont("Body", 8)
    c.drawString(90, y_top - 42, f"Updated {updated}.  Home team listed first.  Check MatchTrak for last-minute changes.")
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.5)
    c.line(36, y_top - 52, page_w - 36, y_top - 52)
    return y_top - 60


def fit(c, text, font, size, width):
    t = text
    while pdfmetrics.stringWidth(t, font, size) > width and len(t) > 3:
        t = t[:-2].rstrip() + "…" if not t.endswith("…") else t[:-2].rstrip() + "…"
    return t


def table(c, y, rows, cols, font, row_h, pad=4):
    """cols: [(label, x, width)].  rows: list of value lists."""
    right = cols[-1][1] + cols[-1][2]
    c.setFillColor(NAVY)
    c.rect(36, y - row_h - 1, right - 36, row_h + 1, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Bold", font)
    base = (row_h - font) / 2 + 1.2
    for label, x, _ in cols:
        c.drawString(x + pad, y - row_h + base - 1, label)
    y -= row_h + 1
    last, shade = None, False
    for r in rows:
        if r[0] != last:
            shade, last = (not shade if last is not None else False), r[0]
        if shade:
            c.setFillColor(BAND)
            c.rect(36, y - row_h, right - 36, row_h, fill=1, stroke=0)
        c.setFillColor(NAVY)
        for i, (val, (_, x, w)) in enumerate(zip(r, cols)):
            face = "Bold" if i == len(r) - 1 and val else "Body"
            if isinstance(val, list):
                cx = x + pad
                for text, part_face, color in val:
                    c.setFont(part_face, font)
                    c.setFillColor(color)
                    c.drawString(cx, y - row_h + base, text)
                    cx += pdfmetrics.stringWidth(text, part_face, font)
                c.setFillColor(NAVY)
                continue
            c.setFont(face, font)
            c.drawString(x + pad, y - row_h + base, fit(c, str(val), face, font, w - pad * 2))
        c.setStrokeColor(RULE)
        c.setLineWidth(0.3)
        c.line(36, y - row_h, right, y - row_h)
        y -= row_h
    return y


def footer(c, w):
    c.setFillColor(MUTED)
    c.setFont("Body", 7.5)
    c.drawString(36, 24, "“Winner QF1” means the winner of Quarterfinal 1 in that division.  FF means forfeit.  PK means decided by penalty kicks.  Source: MatchTrak.")


def cols_for(widths, labels):
    x, out = 36, []
    for l, w in zip(labels, widths):
        out.append((l, x, w))
        x += w
    return out


def pdf_all(games, updated):
    w, h = letter
    c = canvas.Canvas(str(PDF / f"{PDF_NAME}all-games.pdf"), pagesize=letter)
    c.setTitle(f"{TITLE}: All Games")
    y = header(c, "All Games by Date and Time", updated, w, h - 28)
    cols = cols_for([50, 46, 34, 74, 193, 89, 54],
                    ["Date", "Time", "Div.", "Game Type", "Teams", "Park-Field", "Result"])
    rows = [[day(g), clock(g), short_div(g["div"]), g["round"], team_cell(g), g["field"], result_pdf(g)] for g in games]
    table(c, y, rows, cols, 7.6, (y - 40) / (len(rows) + 1.1))
    footer(c, w)
    c.save()


def div_rows(gs):
    return [[day(g), clock(g), g["round"], team_cell(g), g["field"], result_pdf(g)] for g in gs]


DIV_COLS = cols_for([56, 52, 84, 196, 96, 56], ["Date", "Time", "Game Type", "Teams", "Park-Field", "Result"])


def pdf_div(d, gs, updated):
    w, h = letter
    c = canvas.Canvas(str(PDF / f"{PDF_NAME}{short_div(d).lower()}.pdf"), pagesize=letter)
    c.setTitle(f"{TITLE}: {div_name(d)}")
    y = header(c, div_name(d), updated, w, h - 28)
    table(c, y - 6, div_rows(gs), DIV_COLS, 10, 24)
    footer(c, w)
    c.save()


def pdf_divisions(by_div, updated):
    w, h = letter
    c = canvas.Canvas(str(PDF / f"{PDF_NAME}all-divisions.pdf"), pagesize=letter)
    c.setTitle(f"{TITLE}: All Divisions")
    for label, divs in (("Girls Divisions", GIRLS), ("Boys Divisions", BOYS)):
        y = header(c, label, updated, w, h - 28)
        rows = sum(len(by_div[d]) for d in divs)
        row_h = min(19, (y - 40 - len(divs) * 26) / (rows + len(divs)))
        for d in divs:
            y -= 4
            c.setFillColor(NAVY)
            c.setFont("Bold", 11)
            c.drawString(36, y - 12, div_name(d))
            y = table(c, y - 17, div_rows(by_div[d]), DIV_COLS, 8.6, row_h) - 2
        footer(c, w)
        c.showPage()
    c.save()


def field_rows(gs):
    return [[day(g), clock(g), short_div(g["div"]), g["round"], team_cell(g), result_pdf(g)] for g in gs]


FIELD_COLS = cols_for([56, 52, 40, 84, 232, 76], ["Date", "Time", "Div.", "Game Type", "Teams", "Result"])


def pdf_field(f, gs, updated):
    w, h = letter
    c = canvas.Canvas(str(PDF / f"{PDF_NAME}field-{field_slug(f)}.pdf"), pagesize=letter)
    c.setTitle(f"{TITLE}: {f}")
    y = header(c, field_name(f), updated, w, h - 28)
    table(c, y - 6, field_rows(gs), FIELD_COLS, 10, 24)
    footer(c, w)
    c.save()


def pdf_fields(by_field, order, updated):
    w, h = letter
    c = canvas.Canvas(str(PDF / f"{PDF_NAME}all-fields.pdf"), pagesize=letter)
    c.setTitle(f"{TITLE}: All Fields")
    wc = [f for f in order if f.startswith("World Cup")]
    pages = (("World Cup", wc), ("Youth Athletic Park, Gilleran, and Beebe", [f for f in order if f not in wc]))
    for label, fields in pages:
        y = header(c, label, updated, w, h - 28)
        rows = sum(len(by_field[f]) for f in fields)
        row_h = min(19, (y - 40 - len(fields) * 26) / (rows + len(fields)))
        for f in fields:
            y -= 4
            c.setFillColor(NAVY)
            c.setFont("Bold", 11)
            c.drawString(36, y - 12, field_name(f))
            y = table(c, y - 17, field_rows(by_field[f]), FIELD_COLS, 8.6, row_h) - 2
        footer(c, w)
        c.showPage()
    c.save()


# ---------- HTML ----------
CSS = """
:root{--navy:#0B2250;--navy2:#16346F;--gold:#FDC917;--red:#C8102E;--ink:#17233D;--muted:#566079;
--line:#D5DBE8;--band:#EEF1F7;--bg:#F7F8FB;--card:#FFFFFF;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 Barlow,'Helvetica Neue',Arial,sans-serif}
a{color:inherit}
.top{background:var(--navy);color:#fff;border-bottom:4px solid var(--gold)}
.wrap{max-width:1040px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.top .wrap{display:flex;align-items:center;gap:14px;padding-block:12px}
.top img{width:52px;height:52px;flex:none}
.brand{min-width:0}
.brand .yr{font:600 14px/1.1 'Barlow Condensed',Arial,sans-serif;letter-spacing:.09em;text-transform:uppercase;color:var(--gold)}
.brand .nm{font:700 25px/1.08 'Barlow Condensed',Arial,sans-serif;text-wrap:balance}
main{padding-block:22px 40px}
h1{font:700 32px/1.1 'Barlow Condensed',Arial,sans-serif;color:var(--navy);margin:0;text-wrap:balance}
h2{font:700 25px/1.1 'Barlow Condensed',Arial,sans-serif;color:var(--navy);margin:0}
h3{font:700 21px/1.1 'Barlow Condensed',Arial,sans-serif;color:var(--navy);margin:0}
.lead{color:var(--muted);margin:6px 0 0}
.bar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin:0 0 16px}
.back{display:inline-block;margin-bottom:14px;font-weight:600;color:var(--navy);text-decoration:none}
.back:hover{text-decoration:underline}
.btn{display:inline-block;background:var(--gold);color:var(--navy);border-radius:6px;padding:9px 14px;font-weight:700;text-decoration:none;white-space:nowrap}
.btn:hover{background:#FFD845}
.btn.sm{padding:5px 10px;font-size:14px}
a:focus-visible{outline:3px solid var(--red);outline-offset:2px}
.choices{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:20px}
.choice{display:block;background:var(--navy);color:#fff;border-radius:8px;padding:24px;text-decoration:none;border-bottom:5px solid var(--gold)}
.choice:hover{background:var(--navy2)}
.choice b{display:block;font:700 28px/1.1 'Barlow Condensed',Arial,sans-serif}
.choice span{display:block;margin-top:6px;color:#D6DDEC}
.jump{display:flex;flex-wrap:wrap;gap:6px 14px;margin:6px 0 0}
.jump b{min-width:44px}
.jump a{color:var(--navy);font-weight:600}
.group{margin-top:28px}
.group>h2{border-bottom:3px solid var(--gold);padding-bottom:5px}
.dv{margin-top:20px;scroll-margin-top:12px}
.dvh{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px}
.tw{background:var(--card);border:1px solid var(--line);border-radius:6px;overflow:hidden}
table{border-collapse:collapse;width:100%;font-size:15px;font-variant-numeric:tabular-nums}
th{background:var(--navy);color:#fff;text-align:left;font-weight:600;padding:8px 10px;white-space:nowrap}
td{padding:7px 10px;border-top:1px solid var(--line);vertical-align:top}
tr.alt td{background:var(--band)}
td.r{font-weight:700;color:#14632E}
.win{font-weight:700;color:var(--navy)}
.win::after{content:" \\2713";color:#14632E}
.lose{color:var(--muted);font-weight:400}
td.nw{white-space:nowrap}
.foot{margin-top:24px;color:var(--muted);font-size:14px}
@media (max-width:720px){
.choices{grid-template-columns:minmax(0,1fr)}
.brand .nm{font-size:21px}
table,tbody,tr,td{display:block;width:100%}
thead{display:none}
tr{padding:10px 12px;border-top:1px solid var(--line)}
tr:first-child{border-top:0}
tr.alt{background:var(--band)}
td,tr.alt td{padding:0;border:0;background:none}
td[data-l]{color:var(--muted);font-size:14px}
td.tm{color:var(--ink);font-weight:700;font-size:16px;margin:2px 0}
td.gt{color:var(--ink);font-size:14px}
td.when{font-weight:600;color:var(--navy);font-size:15px}
td.r:empty{display:none}
td.r{font-size:15px;margin-top:2px}
}
"""


def page(title, body, updated, stamp):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<link rel="icon" href="assets/logo-64.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;600;700&display=swap">
<link rel="stylesheet" href="assets/site.css?v={stamp}">
</head><body>
<header class="top"><div class="wrap"><img src="assets/logo-256.png" alt="AYSO Region 84 Mission Viejo logo">
<div class="brand"><div class="yr">2026 AYSO Region 84</div><div class="nm">Champions Cup Invitational</div></div></div></header>
<main class="wrap">
{body}
<p class="foot">Updated {updated}.  Home team listed first.  &ldquo;Winner QF1&rdquo; means the winner of Quarterfinal 1 in that division.  Scores come from <a href="https://s11l84-26-fall.matchtrak.com/11/main.nsf/schedule-regiongames-t-by-div?OpenView&amp;Start=1&amp;Count=200&amp;ExpandView&amp;RestrictToCategory=R84">MatchTrak</a>, which has any last-minute changes.</p>
</main></body></html>
"""


def rows_html(gs, with_div, with_field=True):
    out, last, alt = [], None, False
    for g in gs:
        if g["date"] != last:
            alt, last = (not alt if last is not None else False), g["date"]
        e = html.escape
        div = f'<td class="nw gt">{short_div(g["div"])}</td>' if with_div else ""
        fld = f'<td data-l="Field">{e(g["field"])}</td>' if with_field else ""
        out.append(f'<tr{" class=alt" if alt else ""}><td class="nw when">{e(day(g))}</td>'
                   f'<td class="nw when">{e(clock(g))}</td>{div}<td class="gt">{e(g["round"])}</td>'
                   f'<td class="tm">{teams_html(g)}</td>{fld}'
                   f'<td class="r">{e(result_html(g))}</td></tr>')
    return "\n".join(out)


def table_html(gs, with_div, with_field=True):
    div = "<th>Div.</th>" if with_div else ""
    fld = "<th>Park-Field</th>" if with_field else ""
    return (f'<div class="tw"><table><thead><tr><th>Date</th><th>Time</th>{div}<th>Game Type</th>'
            f'<th>Teams</th>{fld}<th>Result</th></tr></thead><tbody>\n'
            f'{rows_html(gs, with_div, with_field)}\n</tbody></table></div>')


def build():
    data = json.loads((ROOT / "data" / "games.json").read_text())
    games = sorted(data["games"], key=sort_key)
    dt = datetime.fromisoformat(data["updated"])
    updated = f"{dt:%a}, {dt:%b}. {dt.day}, {dt.year}, at {dt.hour % 12 or 12}:{dt.minute:02d} {'PM' if dt.hour >= 12 else 'AM'} PT"
    stamp = dt.strftime("%m%d%H%M")
    PDF.mkdir(exist_ok=True)
    by_div = {d: [g for g in games if g["div"] == d] for d in GIRLS + BOYS}

    order = [f for f in FIELDS if any(g["field"] == f for g in games)]
    order += sorted({g["field"] for g in games} - set(order))
    by_field = {f: [g for g in games if g["field"] == f] for f in order}

    pdf_all(games, updated)
    pdf_fields(by_field, order, updated)
    for f, gs in by_field.items():
        pdf_field(f, gs, updated)
    pdf_divisions(by_div, updated)
    for d, gs in by_div.items():
        pdf_div(d, gs, updated)

    (ROOT / "assets" / "site.css").write_text(CSS)
    (ROOT / ".nojekyll").write_text("")
    (ROOT / "index.html").write_text(page(TITLE, f"""<h1>Tournament Schedule and Results</h1>
<p class="lead">Nov. 2 through Nov. 12, 2026.  Choose how you want to view the games.</p>
<div class="choices">
<a class="choice" href="divisions.html"><b>By Division</b><span>Girls and boys, 9U through 14U</span></a>
<a class="choice" href="schedule.html"><b>By Date</b><span>All games by date and time</span></a>
<a class="choice" href="fields.html"><b>By Field</b><span>World Cup, Marty Russo, Gilleran, and Beebe</span></a>
</div>""", updated, stamp))

    (ROOT / "schedule.html").write_text(page(f"All Games | {TITLE}", f"""<a class="back" href="index.html">&larr; Back to home</a>
<div class="bar"><h1>All Games by Date and Time</h1>
<a class="btn" href="pdf/{PDF_NAME}all-games.pdf?v={stamp}" download>Download PDF</a></div>
{table_html(games, True)}""", updated, stamp))

    jump = lambda label, ds: (f'<div class="jump"><b>{label}</b>' +
                              "".join(f'<a href="#{d.lower()}">{int(d[2:])}U</a>' for d in ds) + "</div>")

    def section(label, ds):
        s = f'<section class="group"><h2>{label}</h2>'
        for d in ds:
            s += (f'<div class="dv" id="{d.lower()}"><div class="dvh"><h3>{div_name(d)}</h3>'
                  f'<a class="btn sm" href="pdf/{PDF_NAME}{short_div(d).lower()}.pdf?v={stamp}" download>PDF</a></div>'
                  f'{table_html(by_div[d], False)}</div>')
        return s + "</section>"

    (ROOT / "divisions.html").write_text(page(f"By Division | {TITLE}", f"""<a class="back" href="index.html">&larr; Back to home</a>
<div class="bar"><div><h1>Schedule by Division</h1>{jump("Girls", GIRLS)}{jump("Boys", BOYS)}</div>
<a class="btn" href="pdf/{PDF_NAME}all-divisions.pdf?v={stamp}" download>Download All Divisions PDF</a></div>
{section("Girls", GIRLS)}{section("Boys", BOYS)}""", updated, stamp))
    fjump = '<div class="jump">' + "".join(f'<a href="#{field_slug(f)}">{html.escape(f)}</a>' for f in order) + "</div>"
    fsec = "".join(f'''<div class="dv" id="{field_slug(f)}"><div class="dvh"><h3>{html.escape(field_name(f))}</h3>
<a class="btn sm" href="pdf/{PDF_NAME}field-{field_slug(f)}.pdf?v={stamp}" download>PDF</a></div>{table_html(by_field[f], True, False)}</div>''' for f in order)
    (ROOT / "fields.html").write_text(page(f"By Field | {TITLE}", f"""<a class="back" href="index.html">&larr; Back to home</a>
<div class="bar"><div><h1>Schedule by Field</h1>{fjump}</div>
<a class="btn" href="pdf/{PDF_NAME}all-fields.pdf?v={stamp}" download>Download All Fields PDF</a></div>
{fsec}""", updated, stamp))
    print(len(games), "games built")


if __name__ == "__main__":
    build()
