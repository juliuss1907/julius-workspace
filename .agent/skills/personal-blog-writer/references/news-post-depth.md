# News Post Depth (Julius correction — 2026-08-28)

## The correction

Julius rejected the first batch of news posts written from a daily brief with:
> "Sao mấy bài này ngắn quá vậy? Viết chi tiết lên chứ" — "Why are these posts so short? Write them in detail."

The first versions were ~250-300 word Coin68-voice summaries. Julius wanted **600-900 words per post** with **real source research** (he explicitly chose "~600-900 từ mỗi bài, có research thêm nguồn gốc để có chi tiết thật").

## What "detailed" means in practice (5 posts reworked 2026-08-28)

For each of stories 2/3/5/7/10 (Anthropic MHS, rogue-AI letter, StarkWare QSB, Lightning AI bug, HashKey capital-markets), the accepted version added:

- **Mechanism / how it works**: MHS driver primitives (read/write), HORS one-time signatures, DER-encoded ECDSA trick (1/2^46), vesting-account exploit sequence.
- **Named examples with numbers**: QuEra 99.3%, CMU 3x, Lightning capacity 5,891→3,998 BTC (−32.1%), 148M KII, transaction size/fee figures.
- **Context and implications**: why it matters, ecosystem framing, "so what" woven into the closing paragraph (NOT a separate line).
- **Explicit claim-vs-fact discipline**: for StarkWare QSB, clearly labeled that the quantum-resistance claim comes from StarkWare + the method's author, not independently verified on-chain.

## Process notes

- When Julius says "viết chi tiết lên" / asks to expand already-written short posts, **research the primary sources** (web_extract the source URLs from the brief; CoinDesk may hit antibot → fall back to the cryptonomist cache / another outlet) and rewrite each file.
- Keep `scheduledAt`/`publishedAt`/`category` unchanged; bump `readingMinutes` 2→4.
- If the first post is scheduled soon, push the detailed rewrite BEFORE the first scheduled time so the Cloudflare Worker publishes the detailed version directly (no need to let the short version go out first).
- Update the `working/Blog/Content/news/` backup copies + index to match the detailed bodies.
- `readingMinutes` for these posts: **4**, not 2.
