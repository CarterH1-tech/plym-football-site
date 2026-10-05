#!/usr/bin/env python3
"""Parse the cached MASCAC standings page into analysis/out/standings.csv."""
import csv
import os

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

soup = BeautifulSoup(open(os.path.join(HERE, "cache", "standings.html"), encoding="utf-8", errors="ignore").read(), "lxml")
table = soup.find("table")
rows = table.find_all("tr")[2:]  # first two rows are headers

out = []
for r in rows:
    ds = [c.get_text(" ", strip=True) for c in r.find_all(["th", "td"])]
    if len(ds) >= 7:
        out.append({"team": ds[0], "conf_wl": ds[2], "conf_pct": ds[3], "overall_wl": ds[5], "overall_pct": ds[6]})

with open(os.path.join(OUT, "standings.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["team", "conf_wl", "conf_pct", "overall_wl", "overall_pct"])
    w.writeheader()
    w.writerows(out)

print(f"[standings] {len(out)} teams -> analysis/out/standings.csv")
