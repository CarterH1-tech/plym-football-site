---
title: "Majoring in Football"
subtitle: "Do particular academic majors produce better football players? Evidence from the 2026 Plymouth State opponents"
author: "Carter H1-tech"
date: "October 2026"
abstract: |
  We ask whether particular college majors produce better football players. Using the
  Plymouth State University 2026 schedule as a sampling frame, we assembled roster and
  season statistics for every opponent that publishes player majors (7 of 10 teams) and
  matched 530 players, 253 of whom recorded a 2026 statistic, to a position-normalised
  production score. Business, Finance & Accounting is by far the largest major (199 of
  530 declared-major players, 37.6%) yet sits slightly below average in per-player
  production (mean z = -0.04). The majors that appear "best" are small ones whose
  averages rest on one or two standouts. We find no strong evidence that major choice
  predicts on-field production; the clearest pattern is volume, not quality. A side note
  shows a +0.72 correlation between a team's business-major share and its conference win
  rate, which we treat as an artefact of small samples rather than a causal effect.
---

# Introduction

Ask a football fan which college major produces the best players and you will get a
confident answer -- business, sport management, or perhaps kinesiology. The intuition is
not unreasonable: athletes may gravitate toward flexible majors, conditioning programmes
may attract athletic students, and a well-resourced school may steer recruits toward
particular programmes. But a plausible story is not evidence. Casual claims ignore two
stubborn problems: football production depends first on *position* (quarterbacks
accumulate yardage; offensive linemen rarely appear on a stat sheet), and any
major-level comparison confounds major choice with recruiting and roster composition.

This paper takes the smallest honest version of the question. Using a real, bounded
sampling frame -- the ten opponents on Plymouth State University's 2026 football
schedule -- we ask: **among the teams that publish player majors, does any major produce
measurably more on-field production per player?** Our contribution is not a definitive
ranking but a transparent, reproducible measurement showing how fragile the intuitive
answer becomes once position and sample size are taken seriously.

# Data and Methods

**Sampling frame.** Plymouth State's 2026 opponents were taken from the university's
official athletics schedule feed. Three of the ten opponents -- New England College,
Mass. Maritime, and Bridgewater State -- do not publish a major for individual players,
so they are excluded. The remaining seven teams (Plymouth State, Dean,
Mass.-Dartmouth, Worcester State, Framingham State, Fitchburg State, and Westfield
State) form the analysis sample (Table 1).

**Majors.** Player majors and positions were scraped from each team's public roster or
player-bio pages (Sidearm for Plymouth State, Dean, and Mass.-Dartmouth; PrestoSports
for the rest). Dean lists a major for only 14 of 78 players and Westfield State for 41 of
80, an important source of missingness. Blank majors are reported as "Not reported" and
excluded from major-level averages; explicitly undeclared students are kept as their own
category.

**Statistics.** Per-player season totals were reconstructed from the 20 MASCAC game
box scores involving the seven teams (through 3 October 2026). Each box score's paired
category tables and defensive table were parsed and summed by player. As a validity
check, the reconstructed totals reproduce Plymouth State's official cumulative statistics
exactly -- for example, Jayden Graham (335 rushing yards, 2 touchdowns) and TJ Taveras
(19 tackles, 6.0 tackles for loss, 3.5 sacks).

**Production score.** For each player we compute

$$P = P_{\text{off}} + P_{\text{def}} + P_{\text{st}}$$

where $P_{\text{off}}$ = passing + rushing + receiving yards + 6 x (passing + rushing +
receiving touchdowns); $P_{\text{def}}$ = 4 x total tackles + 6 x tackles for loss + 10 x
sacks + 16 x interceptions + 6 x forced fumbles + 6 x fumble recoveries + 3 x pass
breakups; and $P_{\text{st}}$ = 20 x field goals + 4 x extra points + 0.5 x return yards.
These weights are a judgement, not a law; they are stated so that readers can re-weight
them.

**Normalisation.** Raw $P$ is dominated by position. The position-group means below make
this concrete: quarterbacks average 237.0 production units, running backs 116.9, and
offensive linemen 7.2. We therefore convert each player's $P$ to a z-score within their
position group (QB, RB, WR/TE, OL, DL, LB, DB, K/P) and report the mean z for each
major. A player is counted as a *top producer* if they fall in the top quartile of their
own position group. This ensures that a major is judged by how its players perform
relative to positional peers, not by how many quarterbacks it happens to contain.

**Major grouping.** Cognate programmes were merged (all business, finance, accounting,
and management variants; all sport-management and recreation variants; all
exercise-science, movement-science, and physical-education variants; and so on). Rare
majors were folded into "Other". This grouping is a methodological choice; the raw
majors are retained in the released data.

| Team | Roster | Declared major | Declared & recorded stats |
|:---------------------|------:|---------------:|--------------------------:|
| Plymouth St.         |    99 |             99 |                        43 |
| Worcester St.        |    74 |             74 |                        37 |
| Framingham St.       |    95 |             95 |                        44 |
| Fitchburg St.        |    76 |             76 |                        43 |
| Westfield St.        |    80 |             41 |                        17 |
| Mass.-Dartmouth      |   131 |            131 |                        60 |
| Dean                 |    78 |             14 |                         9 |
| **Total**            |**633**|         **530**|                    **253**|

Table 1. Coverage of the analysis sample. Three schedule opponents (New England
College, Mass. Maritime, Bridgewater State) publish no player majors and are excluded.

# Results

Table 2 gives the headline result. Business, Finance & Accounting is both the largest
major (199 of 530 declared-major players) and, at mean z = -0.04, marginally below the
position-adjusted average. Marketing (mean z = +0.36, n = 12 with statistics),
Education (+0.33, n = 5), Nursing & Health (+0.15, n = 14) and Sport Management &
Recreation (+0.11, n = 18) sit modestly above average. Criminal Justice, Social
Sciences, and Business cluster near zero. The lowest per-player production belongs to
Undeclared students (mean z = -0.57) and to two small majors, Exercise & Sport Science
(-0.53, n = 7) and Natural Sciences (-0.56, n = 6).

The two majors at the top of the table -- Communications & Media (+1.79) and Computer
Science & IT (+1.10) -- illustrate the central caveat. Both have only **two** players who
recorded a statistic. Their averages are the averages of one or two individuals, not of a
population. The same fragility affects every small category. After position
normalisation, the spread between the largest major and the overall average is well
under one-tenth of a standard deviation: major choice, in these data, is a weak signal.

| Major | Players | Recorded stats | Mean production | Mean z | Top producers (per 100) |
|:----------------------------------|--------:|---------------:|----------------:|-------:|------------------------:|
| Communications & Media            |      10 |              2 |           267.0 | +1.79  |                2 (100) |
| Computer Science & IT             |      12 |              2 |            78.5 | +1.10  |                 1 (50) |
| Marketing                         |      20 |             12 |           102.8 | +0.36  |                 6 (50) |
| Education                         |       8 |              5 |            63.0 | +0.33  |                 2 (40) |
| Nursing & Health                  |      24 |             14 |            86.5 | +0.15  |               4 (28.6) |
| Sport Management & Recreation     |      38 |             18 |            83.4 | +0.11  |               5 (27.8) |
| Criminal Justice                  |      46 |             21 |            63.7 | +0.03  |               6 (28.6) |
| Other                             |      76 |             29 |            82.3 | +0.03  |               9 (31.0) |
| Social Sciences                   |      35 |             20 |            35.5 | -0.02  |                 4 (20) |
| **Business, Finance & Accounting**| **199** |        **102** |        **82.6** | **-0.04** |            **25 (24.5)** |
| Exercise & Sport Science          |      17 |              7 |            90.1 | -0.53  |               1 (14.3) |
| Natural Sciences                  |      16 |              6 |            16.5 | -0.56  |                  0 (0) |
| Undeclared                        |      29 |             15 |            21.5 | -0.57  |                  0 (0) |

Table 2. Production by major, sorted by mean position-normalised z-score. "Mean
production" is the raw composite; "Mean z" is position-adjusted and is the fairer
comparison.

![Mean position-normalised production per player by major. Bars are annotated with the
number of players who recorded a statistic. The two highest bars rest on two players
each.](figures/fig1_production_by_major.png){width=47%}

The identity of the top individual producers reinforces the point. The ten highest
individual production scores belong to six different majors: two Business quarterbacks,
an undeclared quarterback, two "Other" skill players, a Nursing & Health receiver, and a
Sport Management receiver. Excellence is spread across majors, not concentrated in one.

# Side note: roster mix and team results

Readers often extend the question to *teams*: do programmes whose rosters lean toward a
particular major win more? Among the seven teams, the share of declared-major players in
Business, Finance & Accounting correlates with conference win rate at r = +0.72 (Figure
2). The correlation is not evidence of a mechanism. It is carried almost entirely by two
points -- Dean, with the fewest declared majors (14) and no conference wins, and
Framingham State, undefeated with a 43% business share -- while the five teams between
33% and 46% business share span every result from 33% to 67% winning. With seven teams,
one partial roster, and four to five games each, this is a story about noise.

![Roster business-major share against conference win rate. The apparent relationship is
driven by two teams and is not causal.](figures/fig2_business_vs_wins.png){width=47%}

# Discussion and limitations

The honest summary is that **we did not find a major that produces clearly better
football players.** Business is the most common major and is roughly average;
Sport Management, Marketing, Nursing, and Education are slightly above average but on
small samples; the apparent leaders are statistical artefacts. The strongest single
pattern is that Undeclared players produce least -- which is better read as a proxy for
experience (undeclared status and youth travel together) than as an academic effect.

Several limitations bound these conclusions. Three of Plymouth State's ten opponents
publish no majors, and Dean and Westfield State publish majors for only part of their
rosters, so the sample over-represents schools with complete public data. Majors are
self-reported and undated; the production weights are arbitrary; and one season of four
to five games is a sample in which a single player can move a major's average by a
standard deviation. Finally, name-matching covered 253 of 530 declared-major players;
unmatched players are disproportionately backups who recorded no statistics.

None of this is a reason to dismiss the question -- it is a reason to answer it with
position-adjusted, sample-size-aware measures rather than raw leaderboards, and to be
candid that in a single conference season the answer is mostly "no detectable
difference."

# Conclusion

Using real 2026 data from the seven Plymouth State opponents that publish player majors,
we found no meaningful association between academic major and position-adjusted football
production. Business, Finance & Accounting supplies the largest share of players but only
average production per player; the majors that top the table do so through one or two
individuals, and the apparent link between business share and win rate is a small-sample
artefact. On this evidence, the claim that a particular major "produces the best football
players" is closer to folklore than to fact.

# Data availability

All code and derived data are in the project repository. The pipeline
(`analysis/*.py`) rebuilds the player tables from cached public pages, joins them to
production scores, and generates the figures. Sources are the Plymouth State athletics
schedule feed, the MASCAC box scores, and each team's public roster or bio pages.

# References

\small

1. Massachusetts State Collegiate Athletic Conference. *2026 Football Statistics &
   Box Scores.* <https://mascac.com/sports/fball/2026-27/>.
2. Plymouth State University Athletics. *2026 Football Schedule, Roster, and Cumulative
   Statistics.* <https://athletics.plymouth.edu/sports/football>.
3. Dean College, Framingham State, Fitchburg State, UMass Dartmouth, Westfield State, and
   Worcester State athletics sites (public 2026 football rosters and player bios).
