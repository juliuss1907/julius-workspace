#!/usr/bin/env python3
"""Content validation for personal-blog articles (pre-build gate).

Checks the 11 rules in references/content-validation.md, a minimum body word
count and the SEO rules in references/seo-checklist.md (title and description
length, headings, sources, internal links, likely duplicate stories), and
prints per-file PASS/FAIL with line numbers plus related-article suggestions.

Usage:
    python3 validate-content.py src/content/writing/<slug>.md [more slugs ...]
    python3 validate-content.py --min-words 600 src/content/writing/*.md
    python3 validate-content.py --no-seo working/Blog/Content/<slug>.md

Exit code 1 if any file has an ERROR. WARNs never fail the run: the Oxford
comma rule produces false positives on ordinary Vietnamese compound
sentences (see references/oxford-comma-vietnamese-false-positive.md) and the
agent must read the flagged lines to decide.
"""

import argparse
import datetime
import difflib
import json
import os
import re
import sys
import unicodedata

EM_DASH = "\u2014"
EN_DASH = "\u2013"
CURLY_DOUBLE = "\u201c\u201d"
CURLY_SINGLE = "\u2018\u2019"
CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
ZERO_WIDTH = re.compile(r"[\u200b-\u200f\ufeff]")
MISSING_SPACE = re.compile(r"(?<=[a-z\u00e0-\u1ef9])([.,:])(?=[A-Za-z\u00c0-\u1ef9])")
OXFORD = re.compile(r",\s*(v\u00e0|and)\s", re.IGNORECASE)
SHORT_SENTENCE_SPLIT = re.compile(r"[.!?]\s+")
SENTENCE_SKIP = re.compile(r"^[-#*>\d]")

# English words allowed in Vietnamese prose: technical terms and bare verbs the
# checklist exempts. Proper nouns and acronyms are skipped separately.
ALLOWED_EN = {
    "token", "tokens", "llm", "llms", "ai", "api", "sdk", "cache", "framework",
    "pipeline", "deploy", "gpu", "cpu", "benchmark", "leaderboard", "web3",
    "blockchain", "stablecoin", "defi", "node", "validator", "hash", "wallet",
    "bridge", "staking", "yield", "tvl", "tps", "smart", "contract", "oracle",
    "airdrop", "mainnet", "testnet", "memecoin", "ordinal", "inscription",
    "cloud", "open", "source", "agent", "anthropic", "openai", "hugging",
    "face", "the", "and", "for", "that", "this", "with", "from", "have",
    "has", "are", "not", "but",
}

AI_CLICHES = [
    "thay \u0111\u1ed5i cu\u1ed9c ch\u01a1i", "thay \u0111\u1ed5i m\u1ecdi th\u1ee9",
    "k\u1ef7 nguy\u00ean m\u1edbi", "b\u1ee9c tranh to\u00e0n c\u1ea3nh",
    "h\u1ec7 sinh th\u00e1i", "s\u00e2n ch\u01a1i", "cu\u1ed9c \u0111ua v\u0169 trang",
]

ENGLISH_DENSITY_LIMIT = 15.0
MIN_SENTENCE_WORDS = 4
HAS_URL = re.compile(r"https?://|www\.")

# SEO limits. The page title tag appends " | Edge Notes" (13 chars), and Google
# cuts titles near 60 chars and descriptions near 160, so keep both short.
TITLE_WARN, TITLE_MAX = 60, 70
DESC_MIN, DESC_MAX = 110, 160
MAX_INTERNAL_LINKS = 5
DUPLICATE_WINDOW_DAYS = 10
ARTICLE_LINK = re.compile(r"\]\((?:https://edgenotes\.net)?/articles/([a-z0-9]+(?:-[a-z0-9]+)*)/?(?:#[^)\s]*)?\)")
NAMED_TERM = re.compile(r"(?<![\w])([A-Z][\w.+-]*(?:[ ](?:[A-Z][\w.+-]*|\d+(?:[.,]\d+)*))*)")
COMMON_TERMS = {
    "The", "This", "What", "How", "Why", "Một", "Các", "Những", "Trong", "Với", "Của",
    "Tại", "Sau", "Trước", "Khi", "Vì", "Và", "Theo", "Ngày", "Tháng", "Năm",
    # Outlets named in descriptions say where the news came from, not what it is about.
    "CNBC", "Reuters", "Bloomberg", "Financial Times", "TechCrunch", "The Information",
    "The Block", "CoinDesk", "Decrypt", "The Verge", "Wall Street Journal", "WSJ", "Axios",
    # Vietnamese words without diacritics that open sentences.
    "Doanh", "Theo", "Trong", "Sau", "Khi", "Cho", "Con", "Hai", "Ba", "Ban", "Nam", "Gia",
    "Chi", "Tin", "Thanh", "Giao", "Mua", "Hoa", "Kinh", "Sang", "Vay", "Tai", "Tim", "Nhanh",
    "Chinh", "Phong", "Quan", "Lam", "Lai", "Hang", "Tang", "Giam", "Dang", "Mang", "Ngan",
    "Tham", "Thi", "Startup",
}


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"')
    return value


def frontmatter_fields(content):
    """Reads the flat frontmatter this blog uses without needing PyYAML."""
    match = re.match(r"\ufeff?---\r?\n(.*?)\r?\n---", content, re.S)
    fields, current, folded = {}, None, False
    for line in match.group(1).splitlines() if match else []:
        top = re.match(r"([A-Za-z]\w*):\s*(.*)$", line)
        if top:
            current, value = top.group(1), top.group(2).strip()
            folded = value in (">", ">-", "|", "|-")
            if folded:
                fields[current] = ""
            elif value.startswith("[") and value.endswith("]"):
                fields[current] = [unquote(v) for v in value[1:-1].split(",") if v.strip()]
            else:
                fields[current] = [] if value == "" else unquote(value)
        elif current and folded and line.strip():
            fields[current] = (fields[current] + " " + line.strip()).strip()
        elif current and isinstance(fields.get(current), list):
            item = re.match(r"\s*-\s+(.*)$", line)
            if item:
                fields[current].append(unquote(item.group(1)))
    return fields


def is_true(value):
    return str(value).strip().lower() == "true"


def article_date(fields):
    value = str(fields.get("scheduledAt") or fields.get("publishedAt") or "")[:10]
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def named_terms(text):
    terms = set()
    for phrase in NAMED_TERM.findall(text):
        # A word ending in punctuation closes the name; "Face. OpenAI" is two names.
        for segment in re.split(r"(?<=[.,:;])\s+", phrase):
            parts = segment.rstrip(".,:;").split()
            while parts and parts[0] in COMMON_TERMS:
                parts.pop(0)
            for size in range(1, len(parts) + 1):
                term = " ".join(parts[:size])
                # A lone capitalized Vietnamese word is usually a sentence start ("Tổng", "Báo").
                if size == 1 and not term.isascii():
                    continue
                if len(term) > 1 and term not in COMMON_TERMS:
                    terms.add(term)
    return terms


def maximal_terms(terms):
    """Drops terms contained in a longer shared term, so "Hugging Face" is not also scored as "Hugging"."""
    return {t for t in terms if not any(t != other and other.startswith(t + " ") for other in terms)}


def load_site_articles(path):
    """Returns (slug -> fields, disabled slugs) for the blog that contains path."""
    directory = os.path.dirname(os.path.realpath(path))
    if not directory.replace("\\", "/").endswith("src/content/writing"):
        return None, set()
    disabled_file = os.path.join(directory, "..", "disabled-articles.json")
    try:
        disabled = set(json.load(open(disabled_file, encoding="utf-8")))
    except (OSError, ValueError):
        disabled = set()
    articles = {}
    for name in os.listdir(directory):
        if not name.endswith((".md", ".mdx")):
            continue
        content = unicodedata.normalize("NFC", open(os.path.join(directory, name), encoding="utf-8").read())
        articles[name.rsplit(".", 1)[0]] = frontmatter_fields(content)
    return articles, disabled


def first_paragraph(lines):
    for line in lines:
        text = line.strip()
        if text and not text.startswith(("#", "<", "!", "|", ">", "-", "*")):
            return text
    return ""


def seo_checks(path, content, lines, body_words):
    errors, warns, info = [], [], []
    fields = frontmatter_fields(content)
    slug = os.path.basename(path).rsplit(".", 1)[0]
    title = str(fields.get("title") or "")
    description = str(fields.get("description") or "")

    if not title:
        errors.append("frontmatter has no title")
    elif len(title) > TITLE_MAX:
        errors.append(f"title is {len(title)} chars (max {TITLE_MAX}, aim <= {TITLE_WARN}) -> {title}")
    elif len(title) > TITLE_WARN:
        warns.append(f"title is {len(title)} chars; Google may cut it after about {TITLE_WARN}")
    if not description:
        errors.append("frontmatter has no description")
    elif len(description) > DESC_MAX:
        errors.append(f"description is {len(description)} chars (max {DESC_MAX})")
    elif len(description) < DESC_MIN:
        warns.append(f"description is {len(description)} chars; aim for {DESC_MIN}-{DESC_MAX - 5}")

    in_code = False
    h2 = 0
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        if re.match(r"#\s", line):
            errors.append(f"line {i}: H1 in body; the layout already renders the title as H1, use ## -> {line.strip()[:60]}")
        if re.match(r"##\s", line):
            h2 += 1
    if body_words >= 400 and h2 < 2:
        warns.append(f"only {h2} H2 heading(s) in {body_words} words; the table of contents needs 3 headings")

    sources = fields.get("sources")
    if not sources:
        (errors if fields.get("kind", "news") == "news" else warns).append("sources is empty")

    if description and difflib.SequenceMatcher(None, description.lower(), first_paragraph(lines).lower()).ratio() >= 0.6:
        warns.append("first paragraph repeats the description, which the page already shows as the lead")

    articles, disabled = load_site_articles(path)
    if articles is None:
        warns.append("file is not under src/content/writing; internal link and duplicate checks skipped")
        return errors, warns, info

    targets = list(dict.fromkeys(ARTICLE_LINK.findall("\n".join(lines))))
    if not targets:
        errors.append("no internal links; add 2-3 links to related published articles (see related: below)")
    elif len(targets) == 1:
        warns.append("only 1 internal link; aim for 2-3")
    elif len(targets) > MAX_INTERNAL_LINKS:
        warns.append(f"{len(targets)} internal links; more than {MAX_INTERNAL_LINKS} dilutes them")
    source_draft = is_true(fields.get("draft"))
    source_time = str(fields.get("scheduledAt") or "")
    for target in targets:
        target_fields = articles.get(target)
        if target == slug:
            errors.append(f"links to itself: /articles/{target}/")
        elif target_fields is None:
            errors.append(f"internal link target does not exist: /articles/{target}/")
        elif target in disabled:
            errors.append(f"internal link target is disabled: /articles/{target}/")
        elif is_true(target_fields.get("draft")):
            target_time = str(target_fields.get("scheduledAt") or "")
            if source_time and target_time and target_time <= source_time:
                continue
            message = f"internal link target is a draft that may publish after this article: /articles/{target}/"
            (warns if source_draft and not source_time else errors).append(message)

    # Terms used by many titles (Anthropic, OpenAI, Bitcoin) say little about the story.
    term_sets = {other: named_terms(f"{f.get('title', '')}. {f.get('description', '')}") for other, f in articles.items()}
    frequency = {}
    for terms in term_sets.values():
        for term in terms:
            frequency[term] = frequency.get(term, 0) + 1
    limit = max(3, len(articles) // 20)
    own_terms = {t for t in named_terms(f"{title}. {description}") if frequency.get(t, 0) <= limit}
    # Suggestions also use names from the body: a story often mentions earlier news only there.
    prose = re.sub(r"\]\([^)\s]*\)", "]", "\n".join(lines))
    # A single capitalized word mentioned once is often a sentence start, not a name.
    body_terms = {
        t for t in named_terms(prose)
        if frequency.get(t, 0) <= limit and (" " in t or len(re.findall(rf"(?<!\w){re.escape(t)}(?!\w)", prose)) >= 2)
    }
    own_date = article_date(fields)
    scored = []
    for other, other_fields in articles.items():
        if other == slug or other in disabled or is_true(other_fields.get("draft")):
            continue
        shared = maximal_terms(own_terms & term_sets[other])
        related = maximal_terms((own_terms | body_terms) & term_sets[other])
        if not related:
            continue
        other_date = article_date(other_fields)
        days = abs((own_date - other_date).days) if own_date and other_date else None
        similarity = difflib.SequenceMatcher(None, title.lower(), str(other_fields.get("title", "")).lower()).ratio()
        score = sum(2 if " " in t else 1 for t in shared)
        # Names shared with the headline matter more than names only the body mentions.
        related_score = 3 * score + sum(2 if " " in t else 1 for t in related - shared)
        scored.append((related_score, other, sorted(related), days, other_fields, similarity, score, sorted(shared)))
    scored.sort(key=lambda item: (-item[0], item[3] if item[3] is not None else 9999))
    for _, other, _, days, other_fields, similarity, score, shared in scored:
        if days is not None and days <= DUPLICATE_WINDOW_DAYS and (similarity >= 0.5 or (score >= 3 and similarity >= 0.3)):
            warns.append(
                f"possible duplicate story: {other} ({days} days apart, shares {', '.join(shared)}); "
                "if it is the same news, update that article or write a follow-up that links to it"
            )
    for _, other, shared, days, other_fields, *_ in scored[:5]:
        linked = " (linked)" if other in targets else ""
        info.append(f"/articles/{other}/{linked} - {other_fields.get('title', '')} [{', '.join(shared)}]")
    return errors, warns, info


def is_html(line):
    return line.lstrip().startswith("<")


def split_frontmatter(content):
    parts = content.split("---", 2)
    body = parts[2] if len(parts) >= 3 else content
    return body.lstrip("\n")


def prose_text(lines):
    # Link targets are not prose; an internal link slug would count as English words.
    return " ".join(
        re.sub(r"\]\([^)\s]*\)", "]", line) for line in lines
        if line.strip() and not is_html(line) and not line.strip().startswith("#")
    )


def check(path, min_words, seo=True):
    raw = open(path, encoding="utf-8").read()
    content = unicodedata.normalize("NFC", raw)
    body = split_frontmatter(content)
    lines = body.splitlines()
    errors, warns = [], []

    for label, pattern in [
        ("em-dash (U+2014)", EM_DASH),
        ("en-dash (U+2013)", EN_DASH),
        ("curly double quote", CURLY_DOUBLE),
        ("curly single quote", CURLY_SINGLE),
    ]:
        for i, line in enumerate(lines, 1):
            if not is_html(line) and pattern in line:
                errors.append(f"line {i}: {label} -> {line.strip()[:80]}")

    for i, line in enumerate(lines, 1):
        if is_html(line) or HAS_URL.search(line):
            continue
        # Table rows pad cells with spaces and images carry asset paths; neither is prose.
        if line.lstrip().startswith(("|", "![")):
            continue
        if re.search(r"  ", line.lstrip()) and not line.lstrip().startswith("- "):
            errors.append(f"line {i}: double space -> {line.strip()[:80]}")
        if MISSING_SPACE.search(line):
            errors.append(f"line {i}: missing space after punctuation -> {line.strip()[:80]}")
        if CJK.search(line):
            errors.append(f"line {i}: CJK character -> {line.strip()[:80]}")
        if ZERO_WIDTH.search(line):
            errors.append(f"line {i}: zero-width character -> {line.strip()[:80]}")

    oxford_lines = [
        (i, line.strip()[:90]) for i, line in enumerate(lines, 1)
        if not is_html(line) and OXFORD.search(line)
    ]
    if oxford_lines:
        detail = "; ".join(f"L{i}: {t}" for i, t in oxford_lines)
        warns.append(
            f"{len(oxford_lines)} line(s) with a comma before 'v\u00e0'/'and'. "
            f"Compound sentences are fine in Vietnamese; fix only real serial lists. {detail}"
        )

    prose = prose_text(lines)
    words = re.findall(r"[A-Za-z]+", prose)
    candidates = [
        w for w in words
        if len(w) > 3 and w.lower() not in ALLOWED_EN and not w[0].isupper() and not w.isupper()
    ]
    total = max(len(re.findall(r"\S+", prose)), 1)
    density = 100.0 * len(candidates) / total
    if density > ENGLISH_DENSITY_LIMIT:
        errors.append(
            f"English density {density:.0f}% ({len(candidates)}/{total} words) -> "
            f"{', '.join(candidates[:10])}"
        )

    for i, sentence in enumerate(SHORT_SENTENCE_SPLIT.split(body), 1):
        sentence = sentence.strip()
        count = len(sentence.split())
        if 0 < count < MIN_SENTENCE_WORDS and not SENTENCE_SKIP.match(sentence):
            errors.append(f"short sentence ({count} words): ...{sentence[:60]}")

    negation = len(re.findall(
        r"kh\u00f4ng ch\u1ec9.*?m\u00e0 c\u00f2n|not only.*?but also", body, re.IGNORECASE | re.DOTALL
    ))
    if negation > 1:
        errors.append(f"parallel negation used {negation} times (max 1)")

    lowered = body.lower()
    for cliche in AI_CLICHES:
        count = lowered.count(cliche)
        if count > 1:
            errors.append(f"AI cliche '{cliche}' used {count} times (max 1)")

    body_words = len(body.split())
    if body_words < min_words:
        errors.append(f"body is {body_words} words, below the {min_words} minimum")

    info = []
    if seo:
        seo_errors, seo_warns, info = seo_checks(path, content, lines, body_words)
        errors += seo_errors
        warns += seo_warns

    return errors, warns, info, body_words, density


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--min-words", type=int, default=350)
    parser.add_argument("--no-seo", action="store_true", help="skip SEO checks (for backup copies outside the blog)")
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        errors, warns, info, words, density = check(path, args.min_words, seo=not args.no_seo)
        name = path.rsplit("/", 1)[-1]
        status = "PASS" if not errors else "FAIL"
        print(f"{name}: {status} - {words} body words, English density {density:.1f}%")
        for warn in warns:
            print(f"  warn: {warn}")
        for error in errors:
            print(f"  error: {error}")
        for line in info:
            print(f"  related: {line}")
        if errors:
            failed = True

    print("OVERALL:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
