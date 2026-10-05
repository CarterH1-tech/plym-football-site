# Plymouth State Panthers — 2026 Football

A small static website for the **Plymouth State University Panthers 2026 football season**, built for **GitHub Pages**.

It shows:

- the **full 2026 schedule** (all 10 games), with **final scores** for every game played so far;
- each opponent's **team name**, home/away, venue, and whether the game is a **MASCAC** conference game;
- a **"player to watch" from every team** and what they've done this season;
- the Panthers' running **record**, streak, and a **next-game countdown**.

The season data is **fetched at build time** from the official Plymouth State athletics feed, then baked into static HTML — no server, no runtime API calls.

## Data sources

| What | Source |
| --- | --- |
| Schedule, results, record | Official Plymouth State feed: `athletics.plymouth.edu/services/schedule_txt.ashx?schedule=695` |
| Featured-player stats | MASCAC conference individual leaders + each school's official cumulative stats (2026) |
| Team logos / colors | ESPN team logos (with a colored-monogram fallback when a logo is unavailable) |
| Player blurbs (curated) | `data/teams.json` |

The build has a graceful fallback: if the live fetch fails, it rebuilds from the last committed `data/season.json`, so deploys never break.

## Project structure

```
.
├── index.html                 # generated output (self-contained; committed)
├── assets/
│   ├── css/styles.css         # Plymouth State green/white responsive styling (source)
│   └── js/main.js             # game filters + countdown (source)
├── data/
│   ├── season.json            # generated schedule/results snapshot
│   └── teams.json             # curated team + featured-player content
├── scripts/
│   ├── build.mjs              # orchestrator: fetch -> merge -> render
│   ├── sources.mjs            # fetch + parse the official feed
│   └── render.mjs             # HTML templating
└── .github/workflows/pages.yml# build + deploy to GitHub Pages
```

## Local development

Requires **Node.js 18+** (no dependencies to install).

```bash
npm run build          # fetch live data and regenerate index.html + data/season.json
npm run build:offline  # rebuild from the last committed data (no network)

# preview
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploying to GitHub Pages

1. Push this folder to a GitHub repository (default branch `main`).
2. In the repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The included workflow (`.github/workflows/pages.yml`) builds and deploys the site on every push to `main`, on a **daily schedule** (13:00 UTC) to refresh scores, and on manual dispatch.

All asset paths are relative, so the site works under `https://<user>.github.io/<repo>/` without extra configuration. A `.nojekyll` file is included so GitHub Pages serves the files as-is.

## Updating the curated content

Team names, colors, logos, and the featured player/blurb for each team live in **`data/teams.json`**. Edit that file and re-run `npm run build`.

For a new season, update the schedule id in `scripts/sources.mjs` (`OFFICIAL_SCHEDULE_URL`) and the `season.json` reference year, then refresh `teams.json`.

## Notes

- `index.html` is **self-contained**: the build inlines `assets/css/styles.css` and `assets/js/main.js` so the page renders the same in file previews, from `file://`, and on GitHub Pages, with no extra requests. Edit the files under `assets/` and re-run `npm run build`.
- This is an **unofficial fan page** and is not affiliated with or endorsed by Plymouth State University or the NCAA.
- Kickoff times are shown in **Eastern Time** (the feed's local time).
- The Aug. 28 Norwich game was a **preseason exhibition** and is labeled as such; it is excluded from the record and from the team spotlights.
- Player blurbs are written from real 2026 season-to-date statistics and are refreshed by editing `data/teams.json` (stats themselves are not auto-updated per player).
