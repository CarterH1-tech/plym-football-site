#!/usr/bin/env python3
"""Download the public source pages used by the analysis into analysis/cache/.

Sources:
  * Sidearm rosters        (Plymouth State, Dean, UMass-Dartmouth)
  * PrestoSports bio pages  (Worcester, Framingham, Fitchburg, Westfield State)
    -- each embeds the full team roster, including majors
  * MASCAC team pages       -- used to discover that team's box-score URLs
  * MASCAC box scores       -- per-game, per-player statistics
  * MASCAC standings        -- conference / overall records

Run this once before the parse scripts. The cache is git-ignored.
"""
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

SIDEARM = {
    "roster_psu.html": "https://athletics.plymouth.edu/sports/football/roster/2026",
    "roster_dean.html": "https://deanbulldogs.com/sports/football/roster/2026",
    "roster_umassd.html": "https://corsairathletics.com/sports/football/roster/2026",
}
PRESTO_BIO = {
    "bio_worcester.html": "https://wsulancers.com/sports/fball/2026-27/players/lancewilliams1op5",
    "bio_framingham.html": "https://fsurams.com/sports/fball/2026-27/players/michaelmarcucellagi5o",
    "bio_fitchburg.html": "https://fscfalcons.com/sports/fball/2026-27/players/reshawnstewartl2fp",
    "bio_westfield.html": "https://westfieldstateowls.com/sports/fball/2026-27/players/malachihymesyxeo",
}
TEAM_PAGES = {
    "team_plymouth.html": "8jt6qb3dd3l2zda1",
    "team_worcester.html": "0b738pz4ixt3x4ox",
    "team_framingham.html": "fkw50v2t8fb14hf7",
    "team_fitchburg.html": "m6yxt1di5yg79abh",
    "team_westfield.html": "k38lonxps8mfdjdp",
    "team_massdartmouth.html": "njv6k3xplc6u873y",
    "team_dean.html": "eyah1jrbvszmzonz",
}
MASCAC = "https://mascac.com/sports/fball/2026-27/"


def get(url, attempts=4, min_bytes=1000):
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": MASCAC})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = r.read()
            if len(data) >= min_bytes:
                return data
        except Exception as e:
            print(f"    retry {i+1}: {e}")
        time.sleep(2 + 2 * i)
    return None


def save(name, url, min_bytes=1000):
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and os.path.getsize(path) >= min_bytes:
        return True
    data = get(url, min_bytes=min_bytes)
    if data is None:
        print(f"  FAILED {name}")
        return False
    open(path, "wb").write(data)
    print(f"  saved {name} ({len(data)} bytes)")
    return True


def main():
    for name, url in {**SIDEARM, **PRESTO_BIO}.items():
        save(name, url)

    for name, tid in TEAM_PAGES.items():
        save(name, f"{MASCAC}teams?id={tid}")

    save("standings.html", f"{MASCAC}standings")

    # discover box score URLs from the team pages
    box_urls = set()
    for name in TEAM_PAGES:
        path = os.path.join(CACHE, name)
        if os.path.exists(path):
            html = open(path, encoding="utf-8", errors="ignore").read()
            box_urls |= set(re.findall(r"boxscores/\d{8}_[a-z0-9]+\.xml", html))
    print(f"  discovered {len(box_urls)} box scores")

    open(os.path.join(HERE, "boxscore_urls.txt"), "w").write("\n".join(sorted(box_urls)) + "\n")

    for u in sorted(box_urls):
        save(f"box_{os.path.basename(u)}", MASCAC + u)

    print("done. cache at", CACHE)


if __name__ == "__main__":
    main()
