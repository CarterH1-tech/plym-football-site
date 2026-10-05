// Renders the static index.html from structured season data + curated team data.

const MONTH_ABBR = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function dateLabel(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return `${MONTH_ABBR[m - 1]} ${d}`;
}

function initials(name) {
  return name
    .replace(/[^A-Za-z ]/g, " ")
    .split(/\s+/)
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 3)
    .toUpperCase();
}

function formatLocation(loc) {
  const m = /^(.*?)\s*\(([^)]+)\)\s*$/.exec(loc ?? "");
  if (!m) return loc ?? "";
  const city = m[1].trim();
  const venue = m[2].trim();
  return `${venue} · ${city}`;
}

function teamMark(team, { size = "" } = {}) {
  const cls = `teammark${size ? " teammark--" + size : ""}`;
  if (team?.logo) {
    return `<span class="${cls}" style="--c:${esc(team.color || "#333")}"><img src="${esc(
      team.logo
    )}" alt="" loading="lazy" onerror="this.style.display='none';this.parentElement.classList.add('teammark--fallback')" data-initials="${esc(
      initials(team.shortName || team.fullName || "?")
    )}"></span>`;
  }
  return `<span class="${cls} teammark--fallback" style="--c:${esc(
    team?.color || "#333"
  )}" data-initials="${esc(initials(team?.shortName || team?.fullName || "?"))}"></span>`;
}

function renderGame(g, teamsByKey) {
  const opp = teamsByKey.get(g.opponent);
  const isHome = g.homeAway === "home";
  const classes = [
    "game",
    g.status === "final" ? "game--final" : g.status === "exhibition" ? "game--exhibition" : "game--upcoming",
    g.status === "final" ? (g.result.code === "W" ? "game--win" : "game--loss") : "",
  ]
    .filter(Boolean)
    .join(" ");

  const tags = [];
  if (g.conference) tags.push('<span class="tag tag--conf">MASCAC</span>');
  if (g.exhibition) tags.push('<span class="tag tag--exh">Exhibition</span>');
  if (!g.conference && !g.exhibition) tags.push('<span class="tag">Non-conference</span>');

  let resultHtml;
  if (g.status === "final") {
    const won = g.result.code === "W";
    resultHtml = `
      <div class="game__result">
        <span class="badge ${won ? "badge--w" : "badge--l"}">${g.result.code}</span>
        <span class="score"><b>${g.result.teamScore}</b><span class="score__sep">–</span>${g.result.oppScore}</span>
      </div>`;
  } else if (g.status === "exhibition") {
    resultHtml = `<div class="game__result"><span class="muted">Scrimmage</span></div>`;
  } else {
    resultHtml = `<div class="game__result"><span class="upcoming">Upcoming</span></div>`;
  }

  return `
    <article class="${classes}"
      data-status="${g.status}" data-site="${g.homeAway}" data-conf="${g.conference ? "1" : "0"}">
      <div class="game__when">
        <span class="game__dow">${esc(g.dowShort)}</span>
        <span class="game__date">${esc(dateLabel(g.date))}</span>
        <span class="game__time">${esc(g.timeLabel)} ET</span>
      </div>
      <div class="game__matchup">
        <span class="game__ha">${isHome ? "vs" : "at"}</span>
        ${teamMark(opp)}
        <div class="game__opp">
          <span class="game__opp-name">${esc(opp?.fullName || g.opponent)}</span>
          <span class="game__venue">${esc(formatLocation(g.location))}</span>
        </div>
      </div>
      <div class="game__tags">${tags.join("")}</div>
      ${resultHtml}
    </article>`;
}

function renderPlayerCard(team) {
  const p = team.player;
  if (!p) return "";
  const meta = [p.position, p.classYear, p.hometown].filter(Boolean).join(" · ");
  return `
    <article class="pcard" style="--team:${esc(team.color || "#054e39")}">
      <header class="pcard__head">
        ${teamMark(team, { size: "lg" })}
        <div class="pcard__id">
          <h3 class="pcard__team">${esc(team.fullName)}</h3>
          <p class="pcard__mascot">${esc(team.mascot)}${team.self ? " · Home team" : ""}</p>
        </div>
      </header>
      <div class="pcard__player">
        <p class="pcard__kicker">Player to watch</p>
        <h4 class="pcard__name">${esc(p.name)}</h4>
        ${meta ? `<p class="pcard__meta">${esc(meta)}</p>` : ""}
        <p class="pcard__stat">${esc(p.statLine)}</p>
        <p class="pcard__blurb">${esc(p.blurb)}</p>
      </div>
    </article>`;
}

export function renderPage({ season, teams, generatedAt, css = "", js = "" }) {
  const teamsByKey = new Map(teams.map((t) => [t.key, t]));
  const self = teams.find((t) => t.self) || teams[0];
  const { record } = season;

  // Spotlight order: home team first, then opponents in schedule order (deduped).
  const seen = new Set();
  const spotlight = [];
  spotlight.push(self);
  for (const g of season.games) {
    const t = teamsByKey.get(g.opponent);
    if (t && !seen.has(t.key)) {
      seen.add(t.key);
      spotlight.push(t);
    }
  }

  const gamesHtml = season.games.map((g) => renderGame(g, teamsByKey)).join("");
  const spotlightHtml = spotlight.map(renderPlayerCard).join("");

  const next = season.nextGame;
  const nextHtml = next
    ? `
    <div class="nextgame" data-kickoff="${esc(next.kickoff)}">
      <span class="nextgame__label">Next game</span>
      <span class="nextgame__opp">${next.homeAway === "home" ? "vs" : "at"} ${esc(
        teamsByKey.get(next.opponent)?.fullName || next.opponent
      )}</span>
      <span class="nextgame__when">${esc(next.dowShort)} ${esc(dateLabel(next.date))} · ${esc(
        next.timeLabel
      )} ET</span>
      <span class="nextgame__countdown" aria-live="polite"></span>
    </div>`
    : "";

  const chips = [
    ["Overall", record.overall],
    ["MASCAC", record.conference],
    ["Streak", record.streak],
  ]
    .filter(([, v]) => v && v !== "-")
    .map(
      ([label, value]) => `
      <div class="chip"><span class="chip__num">${esc(value)}</span><span class="chip__lbl">${esc(
        label
      )}</span></div>`
    )
    .join("");

  const dataJson = JSON.stringify(season).replace(/</g, "\\u003c");
  const inlineJs = String(js).replace(/<\/script/gi, "<\\/script");

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plymouth State Panthers · 2026 Football Schedule &amp; Scores</title>
<meta name="description" content="Plymouth State Panthers 2026 football schedule, live scores and results, plus a player to watch from every team on the slate.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='18' fill='%23054e39'/%3E%3Ctext x='50' y='68' font-size='52' text-anchor='middle' fill='white' font-family='Arial'%3EPS%3C/text%3E%3C/svg%3E">
<style>
${css}
</style>
</head>
<body>
<a class="skip" href="#schedule">Skip to schedule</a>

<header class="hero">
  <div class="wrap hero__inner">
    <div class="hero__brand">
      <img class="hero__logo" src="${esc(self.logo)}" alt="${esc(self.fullName)} logo" onerror="this.remove()">
      <div>
        <p class="eyebrow">NCAA Division III · MASCAC</p>
        <h1>Plymouth State Panthers</h1>
        <p class="hero__sub">2026 Football Season</p>
      </div>
    </div>
    <div class="chips">${chips}</div>
  </div>
  ${nextHtml}
</header>

<main class="wrap">

  <section id="schedule" class="section">
    <div class="section__head">
      <h2>Schedule &amp; Results</h2>
      <p class="section__lede">All ${season.games.length} games of the 2026 season${
        season.summary ? ` · ${season.summary.wins}–${season.summary.losses} so far` : ""
      }.</p>
    </div>
    <div class="filters" role="group" aria-label="Filter games">
      <button type="button" class="filter is-active" data-filter="all" aria-pressed="true">All</button>
      <button type="button" class="filter" data-filter="home" aria-pressed="false">Home</button>
      <button type="button" class="filter" data-filter="away" aria-pressed="false">Away</button>
      <button type="button" class="filter" data-filter="conf" aria-pressed="false">Conference</button>
      <button type="button" class="filter" data-filter="final" aria-pressed="false">Completed</button>
      <button type="button" class="filter" data-filter="upcoming" aria-pressed="false">Upcoming</button>
    </div>
    <div class="games" id="games">${gamesHtml}</div>
    <p class="empty" id="empty" hidden>No games match this filter.</p>
  </section>

  <section id="teams" class="section">
    <div class="section__head">
      <h2>Team Spotlights</h2>
      <p class="section__lede">One player from each team and what they've done so far this season.</p>
    </div>
    <div class="pcards">${spotlightHtml}</div>
  </section>

</main>

<footer class="footer">
  <div class="wrap">
    <p>Unofficial fan page for Plymouth State University Panthers football. Not affiliated with or endorsed by Plymouth State University or the NCAA.</p>
    <p class="footer__meta">Schedule &amp; scores: <a href="https://athletics.plymouth.edu/sports/football/schedule/2026">athletics.plymouth.edu</a>. Player stats: MASCAC conference leaders and each school's official stats. Last updated <time datetime="${esc(
      generatedAt
    )}">${esc(generatedAt.replace("T", " ").replace(/\.\d+Z$/, " UTC"))}</time>.</p>
  </div>
</footer>

<script id="season-data" type="application/json">${dataJson}</script>
<script>
${inlineJs}
</script>
</body>
</html>
`;
}
