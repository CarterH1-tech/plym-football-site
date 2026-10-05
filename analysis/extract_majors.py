#!/usr/bin/env python3
"""Extract player majors and positions from cached roster / bio pages.

Sources (cached under analysis/cache/):
  roster_plymouth.html, roster_dean.html, roster_umassd.html  -> Sidearm rosters
  bio_worcester.html, bio_framingham.html, bio_fitchburg.html,
  bio_westfield.html                                          -> Presto bio pages
     (each embeds the full team roster as headshots.push({...}) with "attrs")

Writes: analysis/out/players_majors.csv
"""
import csv
import json
import os
import re
import sys

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# cache file -> canonical team name (matches MASCAC box score names)
SIDEARM = {
    "roster_psu.html": "Plymouth St.",
    "roster_dean.html": "Dean",
    "roster_umassd.html": "Mass.-Dartmouth",
}
PRESTO = {
    "bio_worcester.html": "Worcester St.",
    "bio_framingham.html": "Framingham St.",
    "bio_fitchburg.html": "Fitchburg St.",
    "bio_westfield.html": "Westfield St.",
}

ATTR_KEYS = [
    "last_name", "first_name", "major", "minor", "position_abbr", "position",
    "position_stat", "year", "height", "weight", "number", "hometown", "highschool",
]
ATTR_RE = re.compile(r"(?:(?<=\s)|^)(" + "|".join(ATTR_KEYS) + r")=")


def parse_presto_attrs(s):
    """Parse the 'last_name=X, major=Y, hometown=Peabody, MA, ...' attr string."""
    s = s.strip().strip("{}")
    matches = list(ATTR_RE.finditer(s))
    out = {}
    for i, m in enumerate(matches):
        key = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(s)
        val = s[start:end].strip().rstrip(",").strip()
        out[key] = val
    return out


def norm_name(name):
    """Normalize a person's name to 'first last' lowercase for joining."""
    import unicodedata
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    if "," in name:  # some box scores list "Last, First"
        last, first = name.split(",", 1)
        name = first + " " + last
    name = name.replace(".", " ").replace("'", "").replace("\u2019", "").replace("-", " ")
    name = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", name, flags=re.I)
    parts = [p for p in re.split(r"\s+", name) if p]
    if not parts:
        return ""
    return parts[0].lower() if len(parts) == 1 else (parts[0] + " " + parts[-1]).lower()


def norm_major(m):
    m = (m or "").strip()
    if not m or m.lower() in {"n/a", "na", "none", "-"}:
        return ""  # not reported
    return m


rows = []

# ---- Sidearm rosters ----
for fn, team in SIDEARM.items():
    path = os.path.join(CACHE, fn)
    soup = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "lxml")
    players = soup.select(".sidearm-roster-player")
    for p in players:
        def txt(sel):
            el = p.select_one(sel)
            return el.get_text(" ", strip=True) if el else ""
        name = txt(".sidearm-roster-player-name h3 a") or txt(".sidearm-roster-player-name h3")
        if not name:
            continue
        rows.append({
            "team": team,
            "name": name,
            "norm": norm_name(name),
            "jersey": txt(".sidearm-roster-player-jersey-number"),
            "position": txt(".sidearm-roster-player-position .text-bold"),
            "class_year": txt(".sidearm-roster-player-academic-year"),
            "major": norm_major(txt(".sidearm-roster-player-major")),
            "source": "sidearm",
        })

# ---- Presto bio blobs ----
for fn, team in PRESTO.items():
    path = os.path.join(CACHE, fn)
    html = open(path, encoding="utf-8", errors="ignore").read()
    # each: headshots.push({ "uni": N, "name": "...", ..., "attrs": "{...}" });
    blocks = re.findall(r"headshots\.push\(\{(.*?)\}\);", html, re.S)
    for block in blocks:
        nm = re.search(r'"name":\s*"([^"]*)"', block)
        am = re.search(r'"attrs":\s*"([^"]*)"', block)
        if not nm:
            continue
        name = nm.group(1)
        a = parse_presto_attrs(am.group(1)) if am else {}
        if not name:
            continue
        rows.append({
            "team": team,
            "name": name.strip(),
            "norm": norm_name(name),
            "jersey": a.get("number", ""),
            "position": a.get("position_abbr", "") or a.get("position", ""),
            "class_year": a.get("year", ""),
            "major": norm_major(a.get("major", "")),
            "source": "presto",
        })

# de-dup on (team, norm)
seen = set()
deduped = []
for r in rows:
    k = (r["team"], r["norm"])
    if k in seen:
        continue
    seen.add(k)
    deduped.append(r)

with open(os.path.join(OUT, "players_majors.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["team", "name", "norm", "jersey", "position", "class_year", "major", "source"])
    w.writeheader()
    w.writerows(deduped)

by_team = {}
for r in deduped:
    by_team.setdefault(r["team"], []).append(r)
print("[majors] players with a major per team:")
for t, rs in sorted(by_team.items()):
    real = [r for r in rs if r["major"]]
    print(f"  {t:18s} {len(rs):3d} players, {len(real):3d} with a declared major")
print(f"[majors] total {len(deduped)} rows -> analysis/out/players_majors.csv")
