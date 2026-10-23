# News brief → blog: item selection edge cases (observed 2026-09-01)

Session-specific rules for turning a numbered news brief into scheduled blog posts.
Complements `brief-to-blog-and-destination-mapping.md` (destination disambiguation +
sequential numbering base rule).

## 1. `N: <url>` overrides the brief's item N

When Julius writes something like:

```
Viết news:
- 1: kèm bitmine mua eth: https://decrypt.co/376932/... (tiêu đề là Báo cáo kho bạc 31/08/2026: ....)
4, 5, 10 và 12
```

- The `1:` slot is OVERRIDDEN by his supplied story/URL. It is NOT brief item #1
  (which in that session was "Strategy mua lại 4.603 BTC").
- Use HIS URL as the primary source.
- Honor any custom title format he gives (treasury-report style: `Báo cáo kho bạc
  31/08/2026: ...`).
- Map only the PLAIN numbers (4, 5, 10, 12) to brief-sequential order.
- Final post list was: BitMine (user URL), Pentagon ChatGPT/Grok (#4), Apple
  MacBook evidence (#5), Polymarket 1B round (#10), Sony/Anthropic Z-Library (#12).

## 2. Same-story follow-up needs its own slug

Brief item #12 (Sony cites "Zlibrary my beloved" staff chats) was a NEW DEVELOPMENT
of a lawsuit the blog had already covered 08-30 (`sony-warner-anthropic-lawsuit.md`).

- Check `src/content/writing/` for an existing slug covering the same story BEFORE
  writing a brief item that looks similar.
- A new filing / new evidence / amended complaint is a distinct post: new slug
  (`sony-anthropic-zlibrary-chat-evidence.md`), framed as the new development.
- Do not re-publish the original event and do not merge it into the old post.

## 3. Dead primary source → find alternate, don't skip

Two brief URLs failed extraction this session:
- TechCrunch Apple article → 404
- Ars Technica (Z-Library) → anti-bot scrape failure

Worked recovery:
1. web_search the headline (not the URL).
2. Pick an alternate outlet covering the same event: 9to5Mac (Apple), Variety +
   AI Chat Daily (Sony/Anthropic) all worked.
3. Read the alternate with web_extract BEFORE writing.
4. Put the actually-read alternate URL in `sources:`.
5. Note in the report that the brief's primary URL was blocked.

## 4. Scheduling reminder (already in SKILL.md, applied cleanly)

- All 5 posts: `draft: true` + `scheduledAt` in UTC ISO-8601 with milliseconds.
- First post = write-time + 30 min buffer, then exactly 2h apart.
- Report the ICT times to Julius; backup copies to `working/Blog/Content/`.

## 5. Merging multiple treasury news into 'Báo cáo kho bạc DD/MM:...'

When Julius requests:
> "Riêng news X và Y hãy thành 1 bài chung viết kèm thêm news @url:<external-announcement> và đặt tiêu đề là: 'Báo cáo kho bạc DD/MM:....'"

- **Do NOT write separate posts for X and Y:** Collapse them into a single comprehensive article alongside the supplied URL.
- **Title format:** Exact prefix `Báo cáo kho bạc DD/MM: <concise summary>` (e.g. `Báo cáo kho bạc 19/10: Strategy gom STRC, Strive mua BTC và Bitmine áp sát 5% cung ETH`).
- **Sources array:** Aggregate ALL primary sources from the merged brief items plus the external release URL into `sources:`.
- **Structure:** Group by company / treasury entity under clear H2 headings (e.g. Strategy, Strive, Bitmine, Metaplanet). Detail token acquisitions, financing mechanisms (common equity, preferred share buybacks/issuances like STRC/SATS/BMNP, warrants), per-share token dilution impact, and real on-chain yield (such as validator staking revenue).
- **Ending narrative:** Synthesize the overarching capital structure trend (e.g. shift from indiscriminate token purchasing to balance-sheet defense, preferred stock yield management, and self-sustaining on-chain cash flows).

