#!/usr/bin/env python3
"""Join player majors to 2026 production and aggregate by major.

Inputs : analysis/out/players_majors.csv, analysis/out/players_stats.csv
Outputs: analysis/out/players_joined.csv
         analysis/out/major_summary.csv
         analysis/out/summary.json
"""
import csv
import json
import os
import re
import statistics as st
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# ---- major canonicalisation (documented in the paper) ----
def canon_major(m):
    m = (m or "").strip()
    if not m:
        return "Not reported"
    s = m.lower()
    if s in {"undeclared", "undecided", "exploratory"}:
        return "Undeclared"
    if s.startswith("business") or s in {"finance", "accounting", "entrepreneurship", "management"}:
        return "Business, Finance & Accounting"
    if "marketing" in s:
        return "Marketing"
    if "sport" in s or "sports" in s:
        return "Sport Management & Recreation"
    if "exercise" in s or "movement science" in s or "physical education" in s or "physical and health" in s or "kinesiolog" in s:
        return "Exercise & Sport Science"
    if "criminal justice" in s or "homeland security" in s:
        return "Criminal Justice"
    if "communication" in s or "broadcast" in s:
        return "Communications & Media"
    if "computer science" in s or "information technology" in s or "cybersecurity" in s:
        return "Computer Science & IT"
    if "nursing" in s or "health" in s:
        return "Nursing & Health"
    if "education" in s:
        return "Education"
    if "biology" in s or "biotechnology" in s or "chemistry" in s or "science" in s:
        return "Natural Sciences"
    if "psycholog" in s or "sociolog" in s or "political science" in s or "history" in s or "criminology" in s or "economics" in s:
        return "Social Sciences"
    if "undeclared" in s or "exploratory" in s or "undecided" in s:
        return "Undeclared"
    return "Other"


POS_GROUPS = [
    ("QB", {"qb"}),
    ("RB", {"rb", "fb", "hb", "tb"}),
    ("WR/TE", {"wr", "te", "slot"}),
    ("OL", {"ol", "ot", "og", "c", "g", "t"}),
    ("DL", {"dl", "de", "dt", "nt", "edge"}),
    ("LB", {"lb", "ilb", "olb", "mlb"}),
    ("DB", {"db", "cb", "s", "fs", "ss", "saf", "safety"}),
    ("K/P", {"k", "p", "pk", "kp", "ls"}),
]

def pos_group(pos):
    s = re.sub(r"[^a-z ]", " ", (pos or "").lower())
    s = " ".join(s.split())
    long_map = [
        ("running back", "RB"), ("fullback", "RB"), ("halfback", "RB"),
        ("quarterback", "QB"),
        ("wide receiver", "WR/TE"), ("tight end", "WR/TE"), ("slot", "WR/TE"),
        ("offensive line", "OL"), ("offensive lineman", "OL"), ("offensive tackle", "OL"),
        ("offensive guard", "OL"), ("offensive center", "OL"), ("center", "OL"),
        ("defensive line", "DL"), ("defensive lineman", "DL"), ("defensive tackle", "DL"),
        ("defensive end", "DL"), ("defensive edge", "DL"), ("edge", "DL"),
        ("linebacker", "LB"),
        ("defensive back", "DB"), ("cornerback", "DB"), ("safety", "DB"),
        ("place kicker", "K/P"), ("kicker", "K/P"), ("punter", "K/P"),
    ]
    for phrase, grp in long_map:
        if phrase in s:
            return grp
    toks = set(s.split())
    for name, keys in POS_GROUPS:
        if toks & keys:
            return name
    return "Other"


def production(r):
    off = r["pass_yds"] + r["rush_yds"] + r["rec_yds"] + 6 * (r["pass_td"] + r["rush_td"] + r["rec_td"])
    dfn = 4 * r["tkl_tot"] + 6 * r["tfl"] + 10 * r["sacks"] + 16 * r["ints"] + 6 * r["ff"] + 6 * r["fr"] + 3 * r["pbu"]
    stm = 20 * r["fg"] + 4 * r["xp"] + 0.5 * (r["kr_yds"] + r["pr_yds"])
    return off, dfn, stm, off + dfn + stm


def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def main():
    majors = {}
    maj_li = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(OUT, "players_majors.csv"))):
        majors[(r["team"], r["norm"])] = r
        parts = r["norm"].split()
        if len(parts) >= 2:
            maj_li[(r["team"], parts[-1], parts[0][0])].append(r)

    stats = {}
    for r in csv.DictReader(open(os.path.join(OUT, "players_stats.csv"))):
        stats[(r["team"], r["norm"])] = {k: fnum(v) for k, v in r.items() if k not in ("team", "name", "norm")}

    def resolve(team, norm):
        """Exact normalized match, else unique last-name + first-initial match."""
        mj = majors.get((team, norm))
        if mj:
            return mj
        parts = norm.split()
        if len(parts) >= 2:
            cand = maj_li.get((team, parts[-1], parts[0][0]), [])
            if len(cand) == 1:
                return cand[0]
        return None

    # Build the universe: every player with a major, plus any stat line we can
    # resolve back to a major (covers "Last,First" and abbreviated names).
    entries = {}
    for mk, mj in majors.items():
        entries[mk] = (mj, stats.get(mk))
    unresolved_stats = 0
    for sk, stt in stats.items():
        if sk in majors:
            continue
        mj = resolve(*sk)
        if mj:
            entries[sk] = (mj, stt)
        else:
            unresolved_stats += 1

    joined = []
    matched = 0
    for k, (mj, stt) in entries.items():
        base = {f: 0.0 for f in [
            "gp","pass_comp","pass_att","pass_yds","pass_td","pass_int","rush_att","rush_yds","rush_td",
            "rec","rec_yds","rec_td","fg","xp","pts","tkl_solo","tkl_ast","tkl_tot","tfl","sacks",
            "ff","fr","ints","pbu","qbh","blk","kr_no","kr_yds","pr_no","pr_yds","ir_yds","fum","fum_lost"]}
        if stt:
            base.update(stt)
            matched += 1
        off, dfn, stm, total = production(base)
        joined.append({
            "team": mj["team"], "name": mj["name"], "norm": mj["norm"],
            "position": mj["position"], "pos_group": pos_group(mj["position"]),
            "class_year": mj["class_year"], "major_raw": mj["major"], "major": canon_major(mj["major"]),
            "gp": base["gp"], "off": round(off, 1), "def": round(dfn, 1), "st": round(stm, 1),
            "total": round(total, 1),
            "pass_yds": base["pass_yds"], "rush_yds": base["rush_yds"], "rec_yds": base["rec_yds"],
            "pass_td": base["pass_td"], "rush_td": base["rush_td"], "rec_td": base["rec_td"],
            "tkl_tot": base["tkl_tot"], "tfl": base["tfl"], "sacks": base["sacks"], "ints": base["ints"],
        })

    # position-normalised z-scores across players who actually recorded stats
    played = [p for p in joined if p["gp"] > 0]
    by_group = defaultdict(list)
    for p in played:
        by_group[p["pos_group"]].append(p["total"])
    gstats = {g: (st.mean(v), st.pstdev(v) if len(v) > 1 else 0.0) for g, v in by_group.items()}
    for p in joined:
        m, sd = gstats.get(p["pos_group"], (0.0, 0.0))
        p["z"] = round((p["total"] - m) / sd, 3) if sd else 0.0

    # "top producer" = top quartile of production *within the player's position
    # group* (so skill-position players don't automatically dominate).
    group_totals = defaultdict(list)
    for p in played:
        group_totals[p["pos_group"]].append(p["total"])
    gq = {g: (sorted(v)[int(len(v) * 0.75)] if v else 0.0) for g, v in group_totals.items()}
    for p in joined:
        thr = gq.get(p["pos_group"], 0.0)
        p["top_quartile"] = 1 if (p["gp"] > 0 and p["total"] >= thr and p["total"] > 0) else 0

    with open(os.path.join(OUT, "players_joined.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(joined[0].keys()))
        w.writeheader()
        w.writerows(joined)

    # aggregate by major
    majors_grp = defaultdict(list)
    for p in joined:
        majors_grp[p["major"]].append(p)

    summary = []
    for m, ps in majors_grp.items():
        with_stats = [p for p in ps if p["gp"] > 0]
        msum = {
            "major": m,
            "players": len(ps),
            "with_stats": len(with_stats),
            "mean_total": round(st.mean([p["total"] for p in with_stats]), 1) if with_stats else 0,
            "median_total": round(st.median([p["total"] for p in with_stats]), 1) if with_stats else 0,
            "mean_z": round(st.mean([p["z"] for p in with_stats]), 3) if with_stats else 0,
            "top_quartile": sum(p["top_quartile"] for p in with_stats),
            "top_per_100": round(100 * sum(p["top_quartile"] for p in with_stats) / len(with_stats), 1) if with_stats else 0,
            "mean_gp": round(st.mean([p["gp"] for p in with_stats]), 1) if with_stats else 0,
        }
        summary.append(msum)
    summary.sort(key=lambda x: (-x["mean_z"], -x["with_stats"]))

    with open(os.path.join(OUT, "major_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    top = sorted(played, key=lambda p: -p["total"])[:20]
    payload = {
        "n_players_with_major": len(joined),
        "n_matched_to_stats": matched,
        "stats_not_matched_to_major": unresolved_stats,
        "n_played": len(played),
        "position_means": {g: round(v[0], 1) for g, v in gstats.items()},
        "major_summary": summary,
        "top20": [{k: p[k] for k in ("name","team","major","position","total","z","gp")} for p in top],
    }
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[analyze] {len(joined)} players with majors; {matched} matched to a stat line; {len(played)} recorded stats")
    print("\n# Major summary (sorted by mean position-normalised z):")
    print(f"{'major':38s} {'n':>3} {'w/stats':>7} {'meanTot':>8} {'meanZ':>7} {'topQ':>5} {'top/100':>7}")
    for s in summary:
        print(f"{s['major']:38s} {s['players']:3d} {s['with_stats']:7d} {s['mean_total']:8.1f} {s['mean_z']:7.3f} {s['top_quartile']:5d} {s['top_per_100']:7.1f}")
    print("\n# Top 10 producers overall:")
    for p in top[:10]:
        print(f"  {p['total']:7.1f}  z={p['z']:+.2f}  {p['name']:20s} {p['pos_group']:6s} {p['team']:16s} {p['major']}")


if __name__ == "__main__":
    main()
