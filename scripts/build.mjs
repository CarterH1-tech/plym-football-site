#!/usr/bin/env node
// Build script: fetch the 2026 season data, merge curated team/player content,
// and render a static index.html for GitHub Pages.
//
// Usage: node scripts/build.mjs [--offline]
//   --offline  skip network fetches and rebuild from the last committed data.

import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import {
  fetchText,
  parseOfficialSchedule,
  summarize,
  OFFICIAL_SCHEDULE_URL,
} from "./sources.mjs";
import { renderPage } from "./render.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const OFFLINE = process.argv.includes("--offline");

const readJson = async (p) => JSON.parse(await readFile(join(ROOT, p), "utf8"));
const write = (p, s) => writeFile(join(ROOT, p), s, "utf8");

async function loadSeasonFromNetwork() {
  const text = await fetchText(OFFICIAL_SCHEDULE_URL);
  const { record, games } = parseOfficialSchedule(text);
  if (!games.length) throw new Error("parsed 0 games from official schedule feed");
  return { record, games, source: "network" };
}

async function loadSeasonFromDisk() {
  const saved = await readJson("data/season.json");
  return { record: saved.record, games: saved.games, source: "cache", generatedAt: saved.generatedAt };
}

async function main() {
  const teamsFile = await readJson("data/teams.json");
  const teams = teamsFile.teams;

  let season;
  if (OFFLINE) {
    season = await loadSeasonFromDisk();
  } else {
    try {
      season = await loadSeasonFromNetwork();
    } catch (err) {
      console.warn(`[build] live fetch failed (${err.message}); using cached data/season.json`);
      season = await loadSeasonFromDisk();
    }
  }

  const generatedAt = season.generatedAt || new Date().toISOString();

  // Derive summary + the next upcoming (non-exhibition) game.
  season.summary = summarize(season.games);
  season.nextGame =
    season.games
      .filter((g) => g.status === "upcoming")
      .sort((a, b) => a.date.localeCompare(b.date))[0] || null;

  // Validation: every scheduled opponent should have curated content.
  const keys = new Set(teams.map((t) => t.key));
  const missing = [...new Set(season.games.filter((g) => !g.exhibition).map((g) => g.opponent))].filter(
    (o) => !keys.has(o)
  );
  if (missing.length) console.warn(`[build] no team entry for: ${missing.join(", ")}`);
  for (const t of teams) {
    if (!t.player && !t.exhibition) console.warn(`[build] no featured player for: ${t.key}`);
  }

  const out = {
    generatedAt,
    source: season.source,
    sources: {
      schedule: OFFICIAL_SCHEDULE_URL,
    },
    team: {
      name: teams.find((t) => t.self)?.fullName || "Plymouth State Panthers",
      conference: "MASCAC",
      division: "NCAA Division III",
    },
    record: season.record,
    summary: season.summary,
    nextGame: season.nextGame,
    games: season.games,
  };

  await write("data/season.json", JSON.stringify(out, null, 2) + "\n");

  // Inline CSS/JS into index.html so the page renders identically everywhere
  // (file previews, file://, and GitHub Pages) with no extra requests.
  const css = await readFile(join(ROOT, "assets/css/styles.css"), "utf8");
  const js = await readFile(join(ROOT, "assets/js/main.js"), "utf8");
  await write("index.html", renderPage({ season: out, teams, generatedAt, css, js }));

  const played = season.summary.played;
  console.log(
    `[build] ${out.team.name}: ${season.record.overall} (${season.record.conference} MASCAC) · ` +
      `${played} played, ${out.games.length - played} to go · source=${out.source}`
  );
  console.log(`[build] wrote index.html and data/season.json`);
}

main().catch((err) => {
  console.error("[build] fatal:", err);
  process.exit(1);
});
