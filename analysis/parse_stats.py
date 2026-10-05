#!/usr/bin/env python3
"""Parse all cached MASCAC box scores into per-player season totals.

Box score layout (Presto):
  * .stats-fullbox[3] is a 2-column table: col0 = away team, col1 = home team.
      row0      -> team names
      row1..N   -> one row per statistical category, each cell holding one table
  * .stats-fullbox[4] is the defensive table, with a team sub-header row per team.

Writes analysis/out/players_stats.csv
"""
import csv
import glob
import os
import re

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

STAT_FIELDS = [
    "pass_comp", "pass_att", "pass_yds", "pass_td", "pass_int",
    "rush_att", "rush_yds", "rush_td",
    "rec", "rec_yds", "rec_td",
    "fg", "xp", "pts",
    "tkl_solo", "tkl_ast", "tkl_tot", "tfl", "sacks", "ff", "fr", "ints", "pbu", "qbh", "blk",
    "kr_no", "kr_yds", "pr_no", "pr_yds", "ir_yds",
    "fum", "fum_lost",
]


def num(s):
    if s is None:
        return 0.0
    m = re.match(r"^-?\d+(\.\d+)?", str(s).strip())
    return float(m.group(0)) if m else 0.0


def frac(s):
    m = re.match(r"^(\d+)\s*[-/]\s*(\d+)", str(s).strip())
    if m:
        return int(m.group(1)), int(m.group(2))
    v = num(s)
    return int(v), int(v)


def norm_name(name):
    import unicodedata
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    if "," in name:
        last, first = name.split(",", 1)
        name = first + " " + last
    name = name.replace(".", " ").replace("'", "").replace("\u2019", "").replace("-", " ")
    name = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", name, flags=re.I)
    parts = [p for p in re.split(r"\s+", name) if p]
    if not parts:
        return ""
    return parts[0].lower() if len(parts) == 1 else (parts[0] + " " + parts[-1]).lower()


def clean(s):
    return " ".join((s or "").split())


def ensure(players, team, name):
    key = (team, norm_name(name))
    p = players.setdefault(key, {"team": team, "name": name, "gp": 0})
    for f in STAT_FIELDS:
        p.setdefault(f, 0.0)
    return key, p


def parse_detailed(box_soup, players, appear):
    boxes = box_soup.select(".stats-fullbox")
    if len(boxes) < 4:
        return []
    outer = None
    for t in boxes[3].find_all("table"):
        if t.find_parent("table") is None:
            outer = t
            break
    if outer is None:
        return []
    rows = outer.find_all("tr", recursive=False)
    if not rows:
        return []
    teams = [clean(c.get_text(" ", strip=True)) for c in rows[0].find_all("td", recursive=False)]

    for r in rows[1:]:
        for ci, cell in enumerate(r.find_all("td", recursive=False)):
            if ci >= len(teams):
                continue
            team = teams[ci]
            for tb in cell.find_all("table"):
                trs = tb.find_all("tr")
                if not trs:
                    continue
                h = [clean(c.get_text(" ", strip=True)) for c in trs[0].find_all(["th", "td"])]
                cat = h[0] if h else ""
                for tr in trs[1:]:
                    ds = [clean(c.get_text(" ", strip=True)) for c in tr.find_all(["th", "td"])]
                    if len(ds) < 2 or not ds[0]:
                        continue
                    name, v = ds[0], ds[1:]
                    if name.lower().startswith("team"):
                        continue
                    key, p = ensure(players, team, name)
                    appear.add(key)
                    if cat.startswith("Passing") and len(v) >= 5:
                        c, a = frac(v[0]); p["pass_comp"] += c; p["pass_att"] += a
                        p["pass_yds"] += num(v[1]); p["pass_td"] += num(v[3]); p["pass_int"] += num(v[4])
                    elif cat.startswith("Rushing") and len(v) >= 5:
                        p["rush_att"] += num(v[0]); p["rush_yds"] += num(v[1]); p["rush_td"] += num(v[4])
                    elif cat.startswith("Receiving") and len(v) >= 5:
                        p["rec"] += num(v[0]); p["rec_yds"] += num(v[1]); p["rec_td"] += num(v[4])
                    elif cat.startswith("Kicking") and len(v) >= 4:
                        fg, _ = frac(v[0]); p["fg"] += fg
                        xp, _ = frac(v[2]); p["xp"] += xp
                        p["pts"] += num(v[3])
                    elif cat.startswith("Kickoff Returns") and len(v) >= 2:
                        p["kr_no"] += num(v[0]); p["kr_yds"] += num(v[1])
                    elif cat.startswith("Punt Returns") and len(v) >= 2:
                        p["pr_no"] += num(v[0]); p["pr_yds"] += num(v[1])
                    elif cat.startswith("Interception Returns") and len(v) >= 2:
                        p["ir_yds"] += num(v[1])
                    elif cat.startswith("Fumbles") and len(v) >= 2:
                        p["fum"] += num(v[0]); p["fum_lost"] += num(v[1])
    return teams


def parse_defense(box_soup, players, teams, appear):
    boxes = box_soup.select(".stats-fullbox")
    if len(boxes) < 5 or not teams:
        return
    tb = boxes[4].find("table")
    if not tb:
        return
    team_set = set(clean(t) for t in teams)
    current = None
    for tr in tb.find_all("tr"):
        ds = [clean(c.get_text(" ", strip=True)) for c in tr.find_all(["th", "td"])]
        if not ds:
            continue
        if len(ds) >= 2 and ds[1] in team_set and ds[0] in ("#", ""):
            current = ds[1]
            continue
        if current is None or len(ds) < 5:
            continue
        if len(ds) >= 13:
            name = ds[1]
            key, p = ensure(players, current, name)
            appear.add(key)
            p["tkl_solo"] += num(ds[2]); p["tkl_ast"] += num(ds[3]); p["tkl_tot"] += num(ds[4])
            p["sacks"] += num(ds[5]); p["tfl"] += num(ds[6])
            p["ff"] += num(ds[7]); p["fr"] += num(ds[8]); p["ints"] += num(ds[9])
            p["pbu"] += num(ds[10]); p["blk"] += num(ds[11]); p["qbh"] += num(ds[12])


def main():
    players = {}
    files = sorted(glob.glob(os.path.join(CACHE, "box_*.xml")))
    for path in files:
        soup = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "lxml")
        appear = set()
        teams = parse_detailed(soup, players, appear)
        parse_defense(soup, players, teams or [], appear)
        for key in appear:
            if key in players:
                players[key]["gp"] += 1

    rows = []
    for (team, norm), p in players.items():
        p = dict(p)
        p["norm"] = norm
        rows.append(p)

    with open(os.path.join(OUT, "players_stats.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["team", "name", "norm", "gp"] + STAT_FIELDS)
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x["team"], x["name"])):
            w.writerow({k: r.get(k, 0) for k in w.fieldnames})

    print(f"[stats] {len(files)} box scores -> {len(rows)} player-lines (analysis/out/players_stats.csv)")
    psu = [r for r in rows if r["team"] == "Plymouth St."]
    print("  sanity check vs official PSU stats:")
    for p in sorted(psu, key=lambda x: -x["rush_yds"])[:3]:
        print(f"    rush: {p['name']:18s} {int(p['rush_yds'])} yds, {int(p['rush_td'])} TD, {int(p['gp'])} gp")
    for p in sorted(psu, key=lambda x: -x["tkl_tot"])[:3]:
        print(f"    def : {p['name']:18s} {int(p['tkl_tot'])} tkl, {p['tfl']:.1f} TFL, {p['sacks']:.1f} sck")


if __name__ == "__main__":
    main()
