#!/usr/bin/env python3
"""Pull Champions Cup games from MatchTrak into data/games.json.

Prints changed=true or changed=false.  Anything unclear is left alone, and a
page that does not look right stops the run without touching the data.
"""
import html, json, os, pathlib, re, sys, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

URL = ("https://s11l84-26-fall.matchtrak.com/11/main.nsf/schedule-regiongames-t-by-div"
       "?OpenView&Start=1&Count=200&ExpandView&RestrictToCategory=R84")
DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "games.json"
GAME = re.compile(r"(\d\d)/(\d\d)/2026 \w+ (\d\d):(\d\d) ([AP])M (\d{5}) (\w+) H: (.*?) A: (.*?) ?L84-"
                  r"(World Cup SS\d|Beebe|Gilleran \d|Youth Athletic Park [A-D]) Fall L84 (\w+)")
TEAM = re.compile(r"^L84-([^_(]+)_\w+(?: \( ?(\d+) ?\))?")


def page_text(raw):
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def clean(name):
    words = re.split(r"([ -])", name.strip())
    return "".join(w.capitalize() if w.isupper() else w[:1].upper() + w[1:] for w in words)


def parse(text):
    out = {}
    for m in GAME.finditer(text):
        mo, da, hh, mi, ap, gid, _, home, away, field, status = m.groups()
        hour = int(hh) % 12 + (12 if ap == "P" else 0)
        out[int(gid)] = dict(date=f"2026-{mo}-{da}", time=f"{hour:02d}:{mi}", home=home.strip(),
                             away=away.strip(), field=field, status=status)
    return out


def apply(games, live):
    changed = []
    for g in games:
        s = live.get(g["id"])
        if not s:
            print(f"::warning::Game {g['id']} not found on MatchTrak")
            continue
        before = dict(g)
        for key in ("date", "time", "field"):
            g[key] = s[key]
        h, a = TEAM.match(s["home"]), TEAM.match(s["away"])
        final = g["round"] == "Final"
        if final and (h or a):
            if not g["away"]:
                g["home"], g["away"] = "Semifinal winner", "Semifinal winner"
        if h:
            g["home"] = clean(h.group(1))
        if a:
            g["away"] = clean(a.group(1))
        if h and a and h.group(2) is not None and a.group(2) is not None:
            g["home_score"], g["away_score"] = int(h.group(2)), int(a.group(2))
        if s["status"] == "Forfeited":
            g["note"] = "Forfeit"
        elif s["status"] == "Canceled":
            g["note"] = "Canceled"
        elif s["status"] == "Postponed":
            g["note"] = "Postponed"
        elif g["note"] in ("Canceled", "Postponed"):
            g["note"] = ""
        if g != before:
            changed.append(g["id"])
    return changed


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else None
    if source:
        raw = pathlib.Path(source).read_text()
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 Region84ScheduleSync"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8", "replace")
    live = parse(page_text(raw))
    print(f"Read {len(live)} games from MatchTrak")
    data = json.loads(DATA.read_text())
    if len(live) < 50:
        print("::error::Too few games read, so nothing was changed")
        return 1
    changed = apply(data["games"], live)
    if changed:
        data["updated"] = datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="minutes")
        DATA.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        print("Changed games:", changed)
    flag = f"changed={'true' if changed else 'false'}"
    print(flag)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(flag + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
