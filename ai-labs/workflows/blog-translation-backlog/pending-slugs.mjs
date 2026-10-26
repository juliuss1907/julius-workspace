// Prints up to N published article slugs (newest first) that have no English translation file,
// comma-separated, in the format scripts/translate-content.mjs --slugs expects.
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const [root, limit = "50"] = process.argv.slice(2);
if (!root) {
  console.error("Usage: node pending-slugs.mjs <blog-root> [limit]");
  process.exit(2);
}

const writing = join(root, "src/content/writing");
const english = join(root, "src/content/translations/en");
const disabled = new Set(JSON.parse(readFileSync(join(root, "src/content/disabled-articles.json"), "utf8")));
const pending = [];

for (const name of readdirSync(writing)) {
  if (!/\.mdx?$/.test(name)) continue;
  const slug = name.replace(/\.mdx?$/, "");
  // Stale translations already have a file; CI refreshes those when their source changes.
  if (disabled.has(slug) || existsSync(join(english, `${slug}.md`))) continue;
  const frontmatter = readFileSync(join(writing, name), "utf8").match(/^﻿?---\r?\n([\s\S]*?)\r?\n---/)?.[1] ?? "";
  if (/^draft:\s*true\s*$/m.test(frontmatter)) continue;
  pending.push({ slug, publishedAt: frontmatter.match(/^publishedAt:\s*['"]?([^'"\s]+)/m)?.[1] ?? "" });
}

pending.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt) || a.slug.localeCompare(b.slug));
console.log(pending.slice(0, Number(limit)).map(({ slug }) => slug).join(","));
