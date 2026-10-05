#!/usr/bin/env python3
"""Derive each team's current record from cached box-score scoring tables.

Writes analysis/out/team_records.csv
"""
import csv
import glob
import os
import re
from collections import defaultdict

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "out")

KNOWN = ["Plymouth St.", "Worcester St.", "Framingham St.", "Fitchburg St.",
         "Westfield St.", "Mass.-Dartmouth", "Dean", "Bridgewater St.", "Mass. Maritime"]


def clean(s):
    return " ".join((s or "").split())


def norm_team(name):
    n = name.replace("(", " (").split(" (")[0].strip()
    for k in KNOWN:
        if k.lower() in n.lower():
            return k
    return n


def main():
    games = []  # (date, teamA, scoreA, teamB, scoreB)
    for path in sorted(glob.glob(os.path.join(CACHE, "box_*.xml"))):
        if os.path.getsize(path) < 1000:
            continue
        soup = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "lxml")
        date = re.search(r"box_(\d{4})(\d{2})(\d{2})_", path)
        date = f"{date.group(1)}-{date.group(2)}-{date.group(3)}" if date else "?"
        # find a table containing a 'Final' header
        for t in soup.find_all("table"):
            rows = t.find_all("tr")
            if not rows:
                continue
            hdr = [clean(c.get_text(" ", strip=True)) for c in rows[0].find_all(["th", "td"])]
            if "Final" not in hdr:
                continue
            teams = []
            for r in rows[1:]:
                ds = [clean(c.get_text(" ", strip=True)) for c in r.find_all(["th", "td"])]
                if len(ds) < 2:
                    continue
                name = ds[0]
                if not name or name.lower().startswith("team"):
                    continue
                try:
                    score = int(ds[-1])
                except ValueError:
                    continue
                teams.append((norm_team(name), score))
            if len(teams) == 2:
                games.append((date, teams[0][0], teams[0][1], teams[1][0], teams[1][1]))
            break

    rec = defaultdict(lambda: {"w": 0, "l": 0, "pf": 0, "pa": 0, "games": 0})
    for _d, ta, sa, tb, sb in games:
        for team, sc, opp in ((ta, sa, sb), (tb, sb, sa)):
            rec[team]["games"] += 1
            rec[team]["pf"] += sc
            rec[team]["pa"] += opp
            if sc > opp:
                rec[team]["w"] += 1
            elif sc < opp:
                rec[team]["l"] += 1

    rows = []
    for team, r in sorted(rec.items()):
        rows.append({"team": team, "w": r["w"], "l": r["l"], "pf": r["pf"], "pa": r["pa"]})
    with open(os.path.join(OUT, "team_records.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["team", "w", "l", "pf", "pa"])
        w.writeheader()
        w.writerows(rows)

    print(f"[records] {len(games)} games parsed")
    for r in rows:
        print(f"  {r['team']:18s} {r['w']}-{r['l']}  (PF {r['pf']}, PA {r['pa']})")


if __name__ == "__main__":
    main()
