# CJK Leak Patterns -- Session 2026-09-20

Additional Chinese character leak observed during Jev article writing.
Merge into `references/cjk-and-build-pitfalls.md` table when next foreground
edit is possible.

## New pattern (add to leak table)

| Chinese (leaked) | Vietnamese (intended) | Context |
|---|---|---|
| 听起来 | nghe có vẻ | "chỉ cố gắng听起来 hợp lý với người đánh giá" |

## Detection

The content-validation script's CJK check (item #7) caught this on line 13 of the body.
Characters: 听 (U+542C), 起 (U+8D77), 来 (U+6765) — all in the CJK Unified Ideographs block.

## Context

The Chinese phrase 听起来 (tīng qǐlái, "sounds like") leaked into Vietnamese prose where
"nghe có vẻ" was intended. This is a semantic leak — the model knew the meaning but
output the Chinese form instead of Vietnamese.
