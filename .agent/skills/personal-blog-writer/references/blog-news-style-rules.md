# Blog news style rules (Julius, confirmed 2026-08-23)

Hard style constraints Julius gave when ordering Coin68-style news drafts from a
news brief ("Không dùng em-dash, không so what"):

1. **No em-dash anywhere** in the article body. Use commas, colons, parentheses,
   or split sentences instead. Verify after writing: count U+2014 / U+2013 in the
   file must be 0 before presenting the draft.
2. **No "So what:" closing section** in Blog/Content drafts. End with a plain
   closing paragraph (context, caveat, or outlook) and/or a `Nguồn:` link list.
   This overrides older guidance that mapped brief "Tai sao dang chu y" bullets
   into a "So what:" ending.

## Research depth rule

When writing drafts from a news brief, do NOT rely on the brief item alone if its
source was only an excerpt or a secondary outlet. Fetch the original source URL
(web_extract) before drafting. Session example: brief items for the Sandbox bridge
exploit and X stablecoin plans had thin excerpt-based summaries; fetching BeInCrypto
and the CoinDesk original yielded concrete mechanics (LayerZero delegate via
`approveAndCall`, ~400 txs, Upbit/Bithumb freeze timing) and context (Revenue
Sharing phase-out, Benji Taylor hire) that made the drafts substantive.

- **Noisy or foreign-language primary pages** (observed 2026-08-29, CoinShares
  market update): when the "primary" source a secondary outlet links to is
  dominated by cookie-consent markup and/or served in a non-English language
  (Swedish), web_extract's returned page may be 90% banner noise. The real
  content is in the cache file web_extract saves to disk — grep it directly with
  `search_files(pattern='inflow|70%|miner', path='<cache file>')` to jump past
  the banner to the actual report lines. Numbers from the foreign-language
  original are still usable as primary data (translate in the draft, keep the
  attribution).

## Attribution discipline for company-claimed results

When a story's headline claim comes from the company itself (e.g. Inherent claiming
its Faraday agent beat Anthropic/OpenAI models), keep the attribution explicit in
the body ("theo đánh giá của chính công ty") AND add a closing note that no
independent verification exists. Same for unconfirmed plans (X stablecoin talks:
"mới là kế hoạch đang thảo luận, chưa công bố chính thức").
