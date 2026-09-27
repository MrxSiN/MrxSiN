#!/usr/bin/env node
// Refreshes the two generated bits of README.md from live GitHub data:
//   1. the daily-use extension list, ordered by bytes of code, same source as the language card
//   2. the Brainfuck "hours on record", where 1 hour = 1 KB of Brainfuck committed,
//      and "hrs at review time" = commits pushed to Brainfuck repos in the last 14 days
// Run: node scripts/update-readme.mjs   (GITHUB_TOKEN optional, raises the rate limit)

import { readFileSync, writeFileSync } from "node:fs";

const USER = process.env.README_USER ?? "MrxSiN";
const BYTES_PER_HOUR = 1024;
const RECENT_DAYS = 14;

const EXT = {
  Brainfuck: "bf", C: "c", "C++": "cpp", "C#": "cs", Kotlin: "kt", Java: "java",
  Python: "py", JavaScript: "js", TypeScript: "ts", Shell: "sh", PowerShell: "ps1",
  Lua: "lua", Go: "go", Rust: "rs", Ruby: "rb", HTML: "html", CSS: "css",
  QML: "qml", HLSL: "hlsl", Smali: "smali", Dart: "dart", Swift: "swift",
};

const ext = (lang) => EXT[lang] ?? lang.toLowerCase().replace(/[^a-z0-9]/g, "");

export function renderLangs(totals, limit = 6) {
  return Object.entries(totals)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([lang]) => "`." + ext(lang) + "`")
    .join(", ");
}

export const hoursOnRecord = (bytes) => Math.round(bytes / BYTES_PER_HOUR);

const api = async (path) => {
  const res = await fetch("https://api.github.com" + path, {
    headers: {
      accept: "application/vnd.github+json",
      "user-agent": "readme-updater",
      ...(process.env.GITHUB_TOKEN ? { authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {}),
    },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`);
  return res.json();
};

async function collect() {
  const repos = (await api(`/users/${USER}/repos?per_page=100&type=owner`)).filter((r) => !r.fork);
  const totals = {};
  const bfRepos = [];

  for (const repo of repos) {
    const langs = await api(`/repos/${USER}/${repo.name}/languages`);
    for (const [lang, bytes] of Object.entries(langs)) totals[lang] = (totals[lang] ?? 0) + bytes;
    if (langs.Brainfuck) bfRepos.push(repo.name);
  }

  const since = new Date(Date.now() - RECENT_DAYS * 864e5).toISOString();
  let recent = 0;
  for (const name of bfRepos) {
    recent += (await api(`/repos/${USER}/${name}/commits?since=${since}&per_page=100`)).length;
  }

  return { totals, recent };
}

function replaceBlock(text, id, body) {
  const open = `<!-- ${id}:start -->`;
  const close = `<!-- ${id}:end -->`;
  const i = text.indexOf(open);
  const j = text.indexOf(close, i);
  if (i < 0 || j < 0) throw new Error(`marker ${id} missing from README.md`);
  return text.slice(0, i + open.length) + body + text.slice(j);
}

function selftest() {
  const totals = { Brainfuck: 81430, C: 6440, Kotlin: 6090, Java: 3690, "C#": 1450, Python: 900, Ruby: 10 };
  const got = renderLangs(totals);
  const want = "`.bf`, `.c`, `.kt`, `.java`, `.cs`, `.py`";
  if (got !== want) throw new Error(`renderLangs: got ${got}\nwant ${want}`);
  if (hoursOnRecord(81430) !== 80) throw new Error("hoursOnRecord off");
  const md = replaceBlock("a<!-- x:start -->old<!-- x:end -->b", "x", "new");
  if (md !== "a<!-- x:start -->new<!-- x:end -->b") throw new Error("replaceBlock off");
  console.log("selftest ok");
}

if (process.argv.includes("--selftest")) {
  selftest();
} else {
  const { totals, recent } = await collect();
  const hours = hoursOnRecord(totals.Brainfuck ?? 0).toLocaleString("en-US");
  let md = readFileSync("README.md", "utf8");
  md = replaceBlock(md, "langs", renderLangs(totals));
  md = replaceBlock(md, "hours", `${hours} hrs on record (${recent} hrs at review time)`);
  writeFileSync("README.md", md);
  console.log(`langs + ${hours} hrs / ${recent} recent`);
}
