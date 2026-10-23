#!/usr/bin/env python3
"""Convert Astro writing/ articles into the working/Blog/Content/ archive.

Reads each article's frontmatter, writes the archive format required by
working/Blog/Content/AGENTS.md (YAML metadata block, then `## title`, then the
`Meta:` line, then the body verbatim), and prepends wikilinks to the folder
index (newest first) without touching existing entries.

Usage:
    python3 backup-to-working-content.py <slug> [<slug> ...]
    python3 backup-to-working-content.py --project <personal-blog-dir> \
        --archive <working/Blog/Content/news> --date 2026-09-29 <slug> ...

The blog repo and the archive both live under ~/julius-workspace; defaults are
resolved relative to that root. Local-only: the archive is not git-tracked, so
never stage it.
"""

import argparse
from pathlib import Path

DEFAULT_ROOT = Path.home() / "julius-workspace"
DEFAULT_PROJECT = "ai-labs/projects/personal-blog"
DEFAULT_ARCHIVE = "working/Blog/Content/news"
DEFAULT_DATE = None  # fall back to each article's publishedAt

CATEGORY_TAG = {
    "ai": "#ai",
    "tech": "#tech",
    "crypto": "#crypto",
    "finance": "#finance",
}


def parse_frontmatter(block):
    fields = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key == "sources":
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key] = value
    return fields


def parse_sources(block):
    urls, in_sources, current = [], False, None
    for line in block.splitlines():
        if not line.startswith(" "):
            in_sources = line.strip() == "sources:"
            continue
        if not in_sources:
            continue
        stripped = line.strip()
        if stripped.startswith("- http"):
            urls.append(stripped[2:].strip())
        elif stripped.startswith("- ") and current:
            urls.append(current)
        elif "http" in stripped:
            current = stripped.split("http", 1)[1]
            current = "http" + current
    return [u for u in urls if u.startswith("http")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="+")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--archive", default=DEFAULT_ARCHIVE)
    parser.add_argument("--date", default=DEFAULT_DATE)
    args = parser.parse_args()

    project = Path(args.root) / args.project
    archive = Path(args.root) / args.archive
    archive.mkdir(parents=True, exist_ok=True)

    written = []
    for slug in args.slugs:
        source = project / "src" / "content" / "writing" / f"{slug}.md"
        raw = source.read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        if len(parts) < 3:
            raise SystemExit(f"{slug}: no frontmatter found")
        fields = parse_frontmatter(parts[1])
        sources = parse_sources(parts[1])
        body = parts[2].lstrip("\n")

        date = args.date or fields.get("publishedAt", "")
        kind = fields.get("kind", "news")
        category = CATEGORY_TAG.get(fields.get("category", ""), f"#{fields.get('category', 'ai')}")

        header = f"---\n- Ng\u00e0y \u0111\u0103ng: {date}\n- Lo\u1ea1i b\u00e0i: {kind}\n- Category: {category}\n"
        for url in sources:
            header += f"- Ngu\u1ed3n: {url}\n"
        header += "---\n\n"

        title = fields.get("title", slug)
        description = fields.get("description", "")
        target = archive / f"{slug}.md"
        target.write_text(
            header + f"## {title}\n\nMeta: {description}\n\n" + body,
            encoding="utf-8",
        )
        written.append(slug)
        print(f"wrote {target}")

    index = archive / f"{archive.name.rstrip('s') if archive.name.endswith('s') else archive.name}.md"
    if not index.exists():
        for candidate in sorted(archive.glob("*.md")):
            if candidate.stem not in written and candidate.stem in {
                "news", "essays", "options"
            }:
                index = candidate
                break
    if index.exists():
        lines = index.read_text(encoding="utf-8").splitlines(keepends=True)
        new_links = "".join(f"- [[{slug}]]\n" for slug in written)
        position = next(
            (i for i, line in enumerate(lines) if line.strip().startswith("- [[")), len(lines)
        )
        lines[position:position] = [new_links]
        index.write_text("".join(lines), encoding="utf-8")
        print(f"index updated: {index} (inserted at line {position + 1})")
    else:
        print("note: no index file found; create "
              f"{archive.name.rstrip('s')}.md per working/Blog/Content/AGENTS.md")


if __name__ == "__main__":
    main()
