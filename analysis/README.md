# Analysis: majors and on-field production

This directory produces the data behind the paper
[`../paper/majors-and-football.md`](../paper/majors-and-football.md).

## Question

Among the teams on Plymouth State's 2026 football schedule that publish player majors,
does any major produce measurably more on-field production per player?

## Pipeline

```
fetch.py            download source pages into cache/ (git-ignored)
extract_majors.py   parse majors + positions from rosters / bio pages  -> out/players_majors.csv
parse_stats.py      parse 20 MASCAC box scores into season totals     -> out/players_stats.csv
parse_records.py    derive W-L from box-score scoring tables          -> out/team_records.csv
parse_standings.py  parse MASCAC standings                            -> out/standings.csv
analyze.py          join majors + production, aggregate by major      -> out/players_joined.csv,
                                                                          out/major_summary.csv,
                                                                          out/summary.json
side_note.py        team major mix vs conference results              -> out/team_mix.csv
make_figures.py     render the two paper figures                      -> ../paper/figures/*.png
```

Run everything (assuming `cache/` is populated):

```bash
./run_all.sh
```

Download sources first (needs network; some hosts rate-limit):

```bash
./run_all.sh --fetch
```

Rebuild just the PDF (needs `pandoc` and a LaTeX engine such as `tectonic`):

```bash
PDF_ENGINE=tectonic ../paper/build.sh
```

## Production score

For each player, `P = P_off + P_def + P_st`:

- `P_off` = passing + rushing + receiving yards + 6 x (pass/rush/rec touchdowns)
- `P_def` = 4 x tackles + 6 x TFL + 10 x sacks + 16 x interceptions + 6 x forced fumbles
  + 6 x fumble recoveries + 3 x pass breakups
- `P_st` = 20 x field goals + 4 x extra points + 0.5 x return yards

Raw `P` is dominated by position (quarterbacks average ~237, offensive linemen ~7), so
players are scored as a **z-score within their position group** and flagged as a *top
producer* if they fall in their group's top quartile.

## Coverage and caveats

- 7 of Plymouth State's 10 opponents publish player majors; New England College,
  Mass. Maritime, and Bridgewater State do not and are excluded.
- Dean (14/78) and Westfield State (41/80) publish majors for only part of their rosters.
- Name-matching between rosters and box scores covers 253 of 530 declared-major players;
  unmatched players are mostly backups who recorded no statistics.
- Results are descriptive and confounded by position, recruiting, and sample size; they
  are not causal.
