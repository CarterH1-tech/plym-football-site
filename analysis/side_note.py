#!/usr/bin/env python3
"""Team major composition vs. conference results (the paper's side note).

Writes analysis/out/team_mix.csv
"""
import csv
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

joined = list(csv.DictReader(open(os.path.join(OUT, "players_joined.csv"))))
standings = {r["team"]: r for r in csv.DictReader(open(os.path.join(OUT, "standings.csv")))}

by_team = {}
for r in joined:
    by_team.setdefault(r["team"], []).append(r)


def win_pct(wl):
    try:
        w, l = wl.split("-")
        return int(w) / (int(w) + int(l)) if (int(w) + int(l)) else 0
    except Exception:
        return 0


rows = []
for team, ps in sorted(by_team.items()):
    declared = [p for p in ps if p["major"] not in ("Not reported",)]
    n = len(declared)
    if not n:
        continue
    counts = Counter(p["major"] for p in declared)
    top, top_n = counts.most_common(1)[0]
    business = counts.get("Business, Finance & Accounting", 0)
    sport = counts.get("Sport Management & Recreation", 0)
    std = standings.get(team, {})
    rows.append({
        "team": team,
        "roster_declared": n,
        "top_major": top,
        "top_major_pct": round(100 * top_n / n, 1),
        "business_pct": round(100 * business / n, 1),
        "sport_pct": round(100 * sport / n, 1),
        "conf": std.get("conf_wl", ""),
        "overall": std.get("overall_wl", ""),
        "conf_pct": round(win_pct(std.get("conf_wl", "0-0")), 3),
    })

with open(os.path.join(OUT, "team_mix.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# Pearson correlation between business share and conference win %
xs = [r["business_pct"] for r in rows]
ys = [r["conf_pct"] for r in rows]
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
corr = num / den if den else 0

print(f"{'team':18s} {'declared':>8} {'top major':38s} {'biz%':>6} {'sport%':>7} {'conf':>6} {'overall':>8}")
for r in rows:
    print(f"{r['team']:18s} {r['roster_declared']:8d} {r['top_major'][:38]:38s} {r['business_pct']:6.1f} {r['sport_pct']:7.1f} {r['conf']:>6} {r['overall']:>8}")
print(f"\nPearson r(Business share, conference win%) = {corr:+.2f}  (n={n})")
