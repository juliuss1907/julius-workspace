# Validation False Positives (2026-09-10)

## Known false positives in content-validation.md script

### Domain names and entity suffixes trigger "missing space" check
The regex `(?<=[a-zà-ỹ])([.,:])(?=[A-Za-zÀ-Ỹà-ỹ])` matches periods preceded by a lowercase letter and followed by any letter. This catches:
- Domain names: `io.net`, `x.com`, `Venice.ai`, `pump.fun`, `ether.fi`, `dydx.exchange`
- Jurisdiction suffixes: `Binance.US`, `FTX.US`

**Example:** `Binance.US` matches `e.U`; `io.net` matches `o.n`.

**Agent action: Do NOT remove the entity or mangle the sentence.**
The script `validate-content.py` explicitly skips lines containing URLs (`HAS_URL = re.compile(r"https?://|www\.")`):
```python
if is_html(line) or HAS_URL.search(line):
    continue
```

Therefore, choose one of two clean solutions:
1. **Format as markdown link with full URL (preferred):** `[Binance.US](https://binance.us)`, `[io.net](https://io.net)`. The presence of `https://` causes `HAS_URL.search(line)` to return True, safely bypassing `MISSING_SPACE` while keeping the exact official name and providing a useful link for readers.
2. **Use brand name without dot:** If a link is unnecessary or repetitive within the paragraph, write the brand name without the dot (e.g. `Binance US`, `Venice AI`).

Never delete an essential project name or drop an investor/partner from a list just to silence the check.

### Frontmatter lines may trigger checks
The script splits on `---` markers but some checks may still match frontmatter content (e.g., `kind: news` has a colon followed by a space). If validation reports errors on frontmatter-adjacent lines, verify the line is actually in the body.

### Date format regex may catch decimals
Pattern `ngày \d/\d` could match fractions (3/4) or ratios (1/2). Agent judges context.

## Fixes applied to script (already in content-validation.md)

1. **NFC normalization** — `unicodedata.normalize('NFC', content)` prevents false English density from Vietnamese combining marks
2. **HTML line skip** — `is_html(line)` returns True for lines starting with `<`
3. **URL line skip** — `HAS_URL.search(line)` skips punctuation spacing checks on lines with links
4. **Oxford comma threshold** — only warn when count > 2
5. **Proper noun skip** — words starting with uppercase are excluded from English density count
6. **Acronym skip** — all-uppercase words excluded
