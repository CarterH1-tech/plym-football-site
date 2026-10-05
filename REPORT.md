# Report

## Summary

Built two deliverables for the Plymouth State Panthers 2026 football season, and pushed
them to <https://github.com/CarterH1-tech/plym-football-site>:

1. a static **website** with the full schedule, results, and a player spotlight for every
   team; and
2. a 4-page **research paper** (Markdown + PDF) on whether academic majors produce better
   football players, backed by a reproducible data pipeline.

## 1. Website

A self-contained static site (`index.html`) with inlined CSS/JS — no server, no runtime
API calls.

- **Schedule & results** for all 10 games, with final scores for games played, plus
  home/away, venue, and MASCAC tags.
- **Team Spotlights**: a "player to watch" for each of the 10 teams, with a real 2026
  stat line and a written blurb.
- Record chips (2–2 / 1–2 / W1), a next-game countdown, and filters
  (All / Home / Away / Conference / Completed / Upcoming).
- Data is fetched at build time from the official Plymouth State athletics feed
  (`services/schedule_txt.ashx`); if the fetch fails, the build falls back to the last
  committed `data/season.json`.

## 2. Research paper

`paper/majors-and-football.pdf` — *Majoring in Football: Do particular academic majors
produce better football players? Evidence from the 2026 Plymouth State opponents.*

- **Sample:** the 7 of 10 opponents that publish player majors (633 players, 530 with a
  declared major, 253 matched to a 2026 stat line).
- **Method:** a position-normalised production score built from MASCAC box scores;
  players are z-scored within their position group so quarterbacks don't dominate.
- **Findings:** Business, Finance & Accounting is the largest major (37.6%) but only
  average per player; the apparent top majors rest on one or two players; no strong
  evidence that major predicts production.
- **Side note:** team business-major share correlates +0.72 with conference win rate —
  flagged as a small-sample artefact, not causal.
- Built with pandoc + tectonic via `paper/build.sh`.

## 3. Analysis pipeline

`analysis/` reproduces everything from public sources:

```
fetch.py -> extract_majors.py -> parse_stats.py -> parse_records.py
        -> parse_standings.py -> analyze.py -> side_note.py -> make_figures.py
```

`./analysis/run_all.sh --fetch` runs the whole chain and rebuilds the PDF. Raw HTML
sources are cached (git-ignored); derived CSVs and figures are committed.

Validation: the reconstructed season totals reproduce Plymouth State's official
cumulative stats exactly (e.g., Jayden Graham 335 rushing yards; TJ Taveras 19 tackles,
6.0 TFL, 3.5 sacks).

## 4. Deployment status

The code is pushed and correct, but the GitHub Pages deploy is currently blocked by an
**active GitHub incident** ("Incident with Actions", degraded performance). The build and
Pages jobs are queued and not being picked up; earlier legacy Pages builds returned
"Page build failed". This is platform-side, not a repository problem.

Stopgap to view the site immediately (the page is self-contained, so it renders as-is):

<https://raw.githack.com/CarterH1-tech/plym-football-site/main/index.html>

Expected Pages URL once GitHub recovers:
<https://carterh1-tech.github.io/plym-football-site/>

## 5. Repository layout

```
index.html                 self-contained site (generated)
assets/                    CSS/JS source for the site
data/                      season.json (generated) + teams.json (curated)
scripts/                   build.mjs, sources.mjs, render.mjs
.github/workflows/         build + deploy workflow (daily score refresh)
paper/                     majors-and-football.md / .pdf, figures, build.sh
analysis/                  data + paper pipeline, derived CSVs, README
```

## How to build

```bash
node scripts/build.mjs                 # rebuild the website
./analysis/run_all.sh --fetch          # rerun the analysis + PDF
PDF_ENGINE=tectonic ./paper/build.sh   # rebuild the PDF only
```

Requires Node 18+, Python 3 with `beautifulsoup4`/`lxml`/`matplotlib`, pandoc, and a
LaTeX engine (tectonic).
