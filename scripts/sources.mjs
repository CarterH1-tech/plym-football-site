// Data sources for the Plymouth State 2026 football season.
// Primary source is the official athletics feed (plain text, easy to parse).

const UA =
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " +
  "Chrome/124.0.0.0 Safari/537.36";

// The schedule id for the 2026 football season on athletics.plymouth.edu.
export const OFFICIAL_SCHEDULE_URL =
  "https://athletics.plymouth.edu/services/schedule_txt.ashx?schedule=695";

// New England College is not a MASCAC football member, and Norwich is a
// preseason exhibition. Everything else on the slate is a conference game.
const NON_CONFERENCE = new Set(["New England College", "Norwich"]);

const MONTHS = {
  Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5,
  Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11,
};

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export async function fetchText(url, { timeoutMs = 20000 } = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      headers: { "user-agent": UA, accept: "*/*" },
      signal: ctrl.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
    return await res.text();
  } finally {
    clearTimeout(t);
  }
}

// Eastern Time offset for a 2026 date. DST ends Sun Nov 1, 2026.
function etOffsetHours(month, day) {
  if (month < 10) return -4; // Jan–Oct (DST)
  if (month === 10) return day < 1 ? -4 : -5; // November
  return -5;
}

function toIso2026(monthIndex, day, hour24, minute) {
  const off = etOffsetHours(monthIndex, day);
  const sign = off < 0 ? "-" : "+";
  const oh = String(Math.abs(off)).padStart(2, "0");
  const mm = String(monthIndex + 1).padStart(2, "0");
  const dd = String(day).padStart(2, "0");
  const hh = String(hour24).padStart(2, "0");
  const mi = String(minute).padStart(2, "0");
  return `2026-${mm}-${dd}T${hh}:${mi}:00${sign}${oh}:00`;
}

function parse12h(timeStr) {
  const m = /^(\d{1,2}):(\d{2})\s*(AM|PM)$/i.exec(timeStr.trim());
  if (!m) return { hour24: 0, minute: 0 };
  let h = parseInt(m[1], 10) % 12;
  if (/pm/i.test(m[3])) h += 12;
  return { hour24: h, minute: parseInt(m[2], 10) };
}

// Parse the fixed-width official text feed into structured games + record.
export function parseOfficialSchedule(text) {
  const lines = text.replace(/\r\n|\n\r|\r/g, "\n").split("\n");

  const record = {};
  for (const line of lines) {
    let m;
    if ((m = /^Overall\s+(\S+)/.exec(line))) record.overall = m[1];
    else if ((m = /^Conference\s+(\S+)/.exec(line))) record.conference = m[1];
    else if ((m = /^Streak\s+(\S+)/.exec(line))) record.streak = m[1];
    else if ((m = /^Home\s+(\S+)/.exec(line))) record.home = m[1];
    else if ((m = /^Away\s+(\S+)/.exec(line))) record.away = m[1];
    else if ((m = /^Neutral\s+(\S+)/.exec(line))) record.neutral = m[1];
  }

  const games = [];
  const dateRe = /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\s+\((\w{3})\)\s{2,}(.*)$/;

  for (const raw of lines) {
    const m = dateRe.exec(raw);
    if (!m) continue;
    const [, mon, dayStr, dow, restRaw] = m;
    const rest = restRaw.trim();

    // "2:00 PM    Away   Opponent   Location   [Tournament]   [Result]"
    const parts = rest.split(/\s{2,}/).map((p) => p.trim()).filter(Boolean);
    if (parts.length < 4) continue;

    const timeStr = parts[0];
    const homeAway = parts[1];
    let opponent = parts[2];
    const location = parts[3];
    const tail = parts.slice(4).join(" ");

    let result = null;
    let tournament = "";
    const rm = /([WL])\s*(\d+)\s*-\s*(\d+)\s*$/.exec(tail);
    if (rm) {
      result = { code: rm[1], teamScore: parseInt(rm[2], 10), oppScore: parseInt(rm[3], 10) };
      tournament = tail.slice(0, rm.index).trim();
    } else {
      tournament = tail.trim();
    }

    const exhibition = /EXHIBITION/i.test(opponent) || /scrimmage/i.test(tournament);
    opponent = opponent.replace(/\s*-\s*EXHIBITION\s*$/i, "").trim();

    const monthIndex = MONTHS[mon];
    const day = parseInt(dayStr, 10);
    const { hour24, minute } = parse12h(timeStr);

    games.push({
      date: `2026-${String(monthIndex + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`,
      dowShort: dow,
      dow,
      timeLabel: timeStr,
      kickoff: toIso2026(monthIndex, day, hour24, minute),
      homeAway: homeAway.toLowerCase(),
      opponent,
      location,
      conference: !NON_CONFERENCE.has(opponent) && !exhibition,
      exhibition,
      status: result ? "final" : exhibition ? "exhibition" : "upcoming",
      result,
    });
  }

  return { record, games };
}

export function summarize(games) {
  const played = games.filter((g) => g.status === "final");
  const wins = played.filter((g) => g.result.code === "W").length;
  const losses = played.filter((g) => g.result.code === "L").length;
  return { played: played.length, wins, losses };
}
