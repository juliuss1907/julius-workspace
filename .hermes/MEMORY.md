# MEMORY — Markus

Append-only log of significant interactions, decisions, and learnings.

**Format:**
YYYY-MM-DD HH:mm | [CATEGORY] | Entry

| 2026-06-03 08:38 | MILESTONE | coin68-pipeline: Drafted Fasset (1.676 words) → working/Coin68/contents/drafts/fasset.md
| 2026-05-30 00:00 | coin68-pipeline | No Pending projects — standing by.
**Categories:**
- DECISION — Important decisions made with Julius
- LEARNING — New patterns or insights discovered
- ERROR — Mistakes made and how they were fixed
- MILESTONE — Significant achievements or completions

---

## Log

2026-05-04 15:45 | MILESTONE | Initialized as Markus. Identity and Soul defined. Ready to assist Julius.
2026-05-18 08:30 | MILESTONE | Moved config home to /home/julius/julius-workspace/.hermes/. Reloaded identity from SOUL.md and IDENTITY.md.
2026-05-18 08:30 | LEARNING | User addressed me as "Markus" — I initially failed to recognize my own name. Identity now properly loaded.
2026-05-28 17:39 | MILESTONE | coin68-pipeline: Drafted The Beacon (1402 words) → working/Coin68/contents/drafts/the-beacon.md

---

**Instructions for future entries:**
- Keep entries concise (1-3 sentences)
- Focus on what matters for future context
- No filler or status updates
- Append only — never delete or modify past entries
2026-05-29 08:30 | MILESTONE | coin68-pipeline: Drafted Outcome (1837 words) → working/Coin68/contents/drafts/outcome.md
2026-06-01 08:44 | MILESTONE | coin68-pipeline: Drafted Kamino (1599 words) → working/Coin68/contents/drafts/kamino.md (subagent timed out verifying but file complete)
2026-06-02 08:36 | MILESTONE | coin68-pipeline: Drafted PopDEX (1038 words) → working/Coin68/contents/drafts/popdex.md
2026-06-05 08:46 | MILESTONE | coin68-pipeline: Drafted Reservoir (1897 words) → working/Coin68/contents/drafts/reservoir.md
| 2026-06-09 16:00 | MILESTONE | trading-agents Phase 10A done — 14d calibration for BTC/ETH/SOL/combined. Bias (77% SHORT) explained as market artifact (-18% to -23% bear window). Hold-time/exit rules OK. Zero config promotions. Reports: reports/phase10a/{bias-investigation,multi-symbol-comparison,promotion-decisions}.md. All 300+ tests green.
| 2026-06-09 15:46 | MILESTONE | trading-agents Phase 9B done — 5 ops docs (runbook, daily checklist, alerting policy, config promotion, service setup), 2 systemd service templates, docs/ops index. No code/config changes.
| 2026-06-09 14:30 | MILESTONE | trading-agents Phase 9A complete — Process lock, scheduler guard, log rotation, health CLI, runtime control, auto-restart supervisor. 33 supervisor tests + 95 ops tests all green.
| 2026-06-09 16:14 | FIX | trading-agents spot close: cap SELL quantity to free base balance + round down by precision. ETHUSDT_LONG_1780884139073 closed via single-cycle (PnL -0.77%, reason signal_reversal). Root cause: DB stored requested qty, Binance demo fee made free ETH <0.89. New test: test_spot_close_balance_cap.py.
| 2026-06-09 16:18 | UX | trading-agents notifier: split Spot vs Futures wording. Titles: SPOT SELL EXECUTED/SPOT SELL FAILED/spot-reduce/reverse; FUTURES POSITION CLOSED/FUTURES CLOSE FAILED/... Body now includes Market, Position Side (futures), Qty requested/executed, Trade ID. New test: test_spot_futures_notifications.py (8 cases). run_paper_trading passes market_type/position_side/trade_id/qty through. Back-compat for callers without market_type (generic title).
2026-06-15 | coin68-pipeline | Drafted: Axis (1914 words) → working/Coin68/contents/drafts/axis.md
2026-06-15 16:00 | MILESTONE | trading-agents Milestone R done — added --end-date support to replay_signals.py and run_calibration_workflow.py; ran 91d 2024 Q4 bull-market calibration (BTC +49%, ETH +29%, SOL +27%). Signal distribution flipped to BUY 39% / SELL 21%, LONG trades +1.00% vs SHORT -0.02%, confirming stack is market-tracking not intrinsically bear-biased. Zero config promotions. Report: docs/phase10a/bull-market-replay-2024-q4.md. 99 core tests green.
2026-06-16 08:30 | MILESTONE | coin68-pipeline: Drafted Ondo Perp (1,976 words) → working/Coin68/contents/drafts/ondo-perp.md
2026-06-17 08:37 | MILESTONE | coin68-pipeline: Drafted DeFiTuna (1960 words) → working/Coin68/contents/drafts/defituna.md
2026-06-19 08:30 | MILESTONE | coin68-pipeline: Drafted The Open Network (1987 words) → working/Coin68/contents/drafts/the-open-network.md

2026-06-22 09:01 | MILESTONE | coin68-pipeline: Drafted Zoth (1807 words) → working/Coin68/contents/drafts/zoth.md
2026-06-30 08:38 | MILESTONE | coin68-pipeline: Drafted Extended (1,930 words) → working/Coin68/contents/drafts/extended.md
2026-07-02 08:37 | MILESTONE | coin68-pipeline: Drafted Open Standard (1,878 words) → working/Coin68/contents/drafts/open-standard.md
2026-07-05 08:30 | coin68-pipeline | No Pending projects — standing by.
2026-07-25 | workspace-resource-reorganization | ai-labs | Moved shared docs to resource/references; Julius approved removal of empty mcps, personas, and plugins placeholders; api-keys left untouched pending manual retirement.
2026-07-25 | working-domain-cleanup | working | Julius approved: renamed woking.md, normalized draft folders, and removed empty research/client/X-image placeholders.
2026-07-25 | tasks-rebuild | tasks | Julius approved: rebuilt asynchronous queue as queue, active, review, and archive; removed duplicate empty TASK_SKILL; added template and dashboard.
- 2026-07-26 — Rebuilt personal-context as the workspace source of truth for Julius profile, voice, working preferences, and brand; removed approved MSTR/STRC notes and empty placeholders; updated active references; no commit or push performed.
- 2026-07-26 — Rewrote README.md for the current workspace architecture and updated root AGENTS.md to the queue → active → review → archive/YYYY task lifecycle; no commit or push performed.
- 2026-07-26 — Deleted the approved empty ai-labs/systems/llm-knowledge-base skeleton and replaced its invalid task-executor example citation with an existing source; no commit or push performed.
2026-07-31 08:30 | MILESTONE | coin68-pipeline: Drafted Codex FX (2,273 words) → working/Coin68/contents/drafts/codex-fx.md
2026-08-04 08:38 | MILESTONE | coin68-pipeline: Drafted OKB (1,726 words) → working/Coin68/contents/drafts/okb.md
2026-08-05 08:38 | MILESTONE | coin68-pipeline: Drafted KOR Protocol (1,797 words) → working/Coin68/contents/drafts/kor.md
2026-08-06 08:38 | MILESTONE | coin68-pipeline: Drafted Matcha (2,371 words) → working/Coin68/contents/drafts/matcha.md
2026-08-10 08:35 | MILESTONE | coin68-pipeline: Drafted Halo (2,002 words) → working/Coin68/contents/drafts/halo.md
2026-08-11 08:33 | MILESTONE | coin68-pipeline: Drafted Mecone (2,170 words) → working/Coin68/contents/drafts/mecone.md
2026-08-12 08:34 | MILESTONE | coin68-pipeline: Drafted Beezi (2,150 words) → working/Coin68/contents/drafts/beezi.md
2026-08-13 08:35 | MILESTONE | coin68-pipeline: Drafted Hylo (2,019 words) → working/Coin68/contents/drafts/hylo.md
2026-08-17 08:35 | MILESTONE | coin68-pipeline: Drafted Solid (2,267 words) → working/Coin68/contents/drafts/solid.md
2026-08-18 08:36 | coin68-pipeline | Drafted: Accountable (2,077 words) → working/Coin68/contents/drafts/accountable.md
2026-08-27 08:50 | MILESTONE | coin68-pipeline: Drafted Ultra (1995 words) → working/Coin68/contents/drafts/ultra.md
2026-08-31 | coin68-pipeline | Drafted: Neutral (1982 words) → working/Coin68/contents/drafts/neutral.md
2026-09-01 | coin68-pipeline | Drafted: ElfomoFi (1771 words) → working/Coin68/contents/drafts/elfomofi.md
2026-09-02 08:45 | MILESTONE | coin68-pipeline: Drafted TermMax (1998 words) → working/Coin68/contents/drafts/termmax.md
2026-09-03 | coin68-pipeline | Drafted: RQD Clearing (1733 words) → working/Coin68/contents/drafts/rqd-clearing.md
2026-09-04 08:30 | coin68-pipeline | Drafted: Pons (1665 words) → working/Coin68/contents/drafts/pons.md
2026-09-07 08:38 | MILESTONE | coin68-pipeline: Drafted Kravata (1,883 words) → working/Coin68/contents/drafts/kravata.md
2026-09-08 08:22 | MILESTONE | coin68-pipeline: Drafted De1 (2544 words) → working/Coin68/contents/drafts/de1.md
2026-09-08 | coin68-pipeline | Drafted: Liquorice (1887 words) → working/Coin68/contents/drafts/liquorice.md
2026-09-10 08:36 | MILESTONE | coin68-pipeline: Drafted FinTax (2167 words) → working/Coin68/contents/drafts/fintax.md
2026-09-11 08:36 | MILESTONE | coin68-pipeline: Drafted Alloco (1653 words) → working/Coin68/contents/drafts/alloco.md
2026-09-14 | coin68-pipeline | Drafted: The Standard Reserve (2116 words) → working/Coin68/contents/drafts/standard-reserve.md
2026-09-15 08:37 | MILESTONE | coin68-pipeline: Drafted PARE (2023 words) → working/Coin68/contents/drafts/pare.md

[2026-09-17 08:40:13] coin68-pipeline | Drafted: Fables (1772 words) -> working/Coin68/contents/drafts/fables.md | recovered after delegate timeout; source recheck needed; final response delivery
2026-09-18 08:48 | MILESTONE | coin68-pipeline: Drafted Arrows (1,677 words) → working/Coin68/contents/drafts/arrows.md
2026-09-21 | coin68-pipeline | Drafted: Liquid Compute (1972 words) → working/Coin68/contents/drafts/liquid-compute.md
2026-09-22 | coin68-pipeline | Drafted: Fast (2115 words) → working/Coin68/contents/drafts/fast.md
2026-09-23 | coin68-pipeline | Drafted: GetLiquid (2200 words) → working/Coin68/contents/drafts/getliquid.md
2026-09-28 08:34 | coin68-pipeline | Drafted: Aero (1688 words) → working/Coin68/contents/drafts/aero.md
2026-09-28 09:55 | MILESTONE | coin68-pipeline: Drafted Quant Network (1965 words) → working/Coin68/contents/drafts/quant-network.md
2026-09-29 | coin68-pipeline | Drafted: Hypernova (1655 words) → working/Coin68/contents/drafts/hypernova.md
2026-09-29 | coin68-pipeline | Drafted: Verona (1989 words) → working/Coin68/contents/drafts/verona.md
2026-10-05 09:00 | MILESTONE | coin68-pipeline: Drafted Dinari (2,597 words) → working/Coin68/contents/drafts/dinari.md
2026-10-05 14:52 | MILESTONE | coin68-pipeline: Drafted Taceo (3214 words) -> working/Coin68/contents/drafts/taceo.md
2026-10-05 | coin68-pipeline | Drafted: Wonderful (2609 words) → working/Coin68/contents/drafts/wonderful.md | subagent died on API timeout, parent wrote directly, row 91 ok
2026-10-06 | coin68-pipeline | Drafted: Temporal (2125 words) → working/Coin68/contents/drafts/temporal.md
2026-10-06 16:35 | ai-labs/system-trading | Fixed 4 code-review bugs (daily resume, mark15m warmup kind, cash check, midnight-mark baseline), bumped study versions, reran 13 studies offline: economics unchanged except intraday B and Perp-only single-sleeve; docs updated; 6 local commits on feature/weekly-gate-automation, not pushed; delete request for hold-margin-20261006-rerun
2026-10-06 18:53 | ai-labs/system-trading | Julius approved: deleted hold-margin-20261006-rerun (identical input copies); pushed feature/weekly-gate-automation b9ec479..de1bdcf (58 commits incl. earlier unpushed work)
2026-10-06 21:21 | ai-labs/personal-blog | UI audit + premium pass + topic ASCII logo backdrop: 18 commits rebased onto 7 remote content commits, pushed main 3567482..a126311 with Julius's approval; 1 pre-existing failing test (crypto-hack-q3-2026 webp 2400px > 1600px) left untouched; draft blog-index.md still in src/content/writing (untracked)
2026-10-06 21:29 | ai-labs/personal-blog | Julius approved: deleted crypto-hack-q3-2026/818f41cc43b9.webp + its image line, gitignored local blog-index.md; pushed main a126311..a57869b; cac010def6e4.webp (2400px) still fails thumbnails test, awaiting decision
2026-10-06 21:31 | ai-labs/personal-blog | Julius approved: resized crypto-hack-q3-2026/cac010def6e4.webp 2400->1600px (q82), all 246 tests pass; pushed main a57869b..970bff9
2026-10-06 21:50 | ai-labs/personal-blog | Julius approved: pushed main 970bff9..a23099f (6 commits: removed masthead issue line, stronger masthead, 5-story Đáng chú ý, topic-coloured hover + rounded translucent Theo chủ đề panel)
2026-10-07 08:26 | ai-labs/personal-blog | Julius approved: pushed main a23099f..174b331 (9 commits: footer starfield, newsletter removed, social icons, pinned article facts bar + headline over rail, masthead panel skies, ASCII behind header, translucent lead card)
2026-10-07 08:36 | MILESTONE | coin68-pipeline: Drafted Rain Protocol (3,014 words) → working/Coin68/contents/drafts/rain-protocol.md
2026-10-07 08:37 | ai-labs/personal-blog | Julius approved deletion: src/components/Newsletter.astro + newsletter i18n/site config/.env.example/doc mentions; committed 9985452 locally
2026-10-07 08:45 | ai-labs/personal-blog | Julius approved: pushed main 174b331..a362193 (newsletter leftovers removed, masthead band colours swapped, footer night-blue in dark / earth brown in light)
2026-10-07 08:53 | ai-labs/personal-blog | Julius approved: pushed main a362193..582a1cd (language/theme buttons at page edge, 3/4 height)
2026-10-07 10:35 | MILESTONE | coin68-pipeline: Drafted Fungo (1,593 words) → working/Coin68/contents/drafts/fungo.md
2026-10-07 14:23 | ai-labs/personal-blog | Julius approved: restored draft crypto-market-broad-selloff-september (deleted in de6fabe on 2026-09-12) from history; pushed main ca04a12..2d4fa8d
2026-10-07 15:08 | ai-labs/personal-blog | Julius approved: pushed CMS fix for stale local drafts (anthropic-nghien-cuu-81k PR #367 save loop) as 3bcff03, rebased over 3 CMS content commits; note crypto-market-broad-selloff-september was deleted again via CMS at 14:47 after restore, not re-restored
2026-10-07 15:27 | ai-labs/personal-blog | Julius approved: pushed CMS follow-up fixes 3bcff03..5ca9197 (clear pendingSaveId on 409; 'Draft trên GitHub đã thay đổi' now opens Local/GitHub dialog). Not verified end-to-end against live GitHub (no token access)
2026-10-08 09:43 | system/hermes-desktop | Julius approved deletion: ~/.config/Hermes/nvidia-egl-fallback.json.disabled-20261008-0927 (stale SwiftShader-fallback backup). Root cause of app lag+blur: sticky NVIDIA EGL fallback marker forcing --use-angle=swiftshader; cleared 09:27, app re-probed GPU and wrote state=ok. CPU 850%->52%. Skill: software-render-triage
2026-10-08 17:16 | ai-labs/personal-blog | OG cards: built per-category generated OG images (satori+resvg, src/lib/og/, endpoints /og/<slug>.png, /en/og/<slug>.png, /og/default.png); fixed layouts from Julius's canvas arrangement; delete-request filed for public/og-default.svg (tasks/inbox/delete-request-2026-10-08-1715.md); changes uncommitted, no push
2026-10-08 17:35 | ai-labs/personal-blog | Julius approved deletions: public/og-default.svg, src/lib/brand-logo.ts, tests/brand-logo.test.ts (logo locked to handwritten; OG cards generated). Still uncommitted, no push
2026-10-08 17:50 | ai-labs/personal-blog | Julius approved deletions: src/components/DuotoneFilters.astro, src/lib/duotone.ts, tests/duotone.test.ts (thumbnails keep original colours). Also removed author-note and translation-note from ArticleLayout. Uncommitted, no push
2026-10-08 17:50 | ai-labs/personal-blog | Julius approved: pushed brand/OG/thumbnail work as 85b1e7b, 13e85f5, 3d1b01a (rebased over 11 CMS content commits, be2ccfc base); astro check + 271 tests pass after rebase. X/Facebook need a re-scrape for new OG images
2026-10-09 20:15 | ai-labs/personal-blog | Julius approved: pushed CMS fixes (CSRF guard c5d32d4, summary snapshot c42bba2, failed drafts 9ab4d44) via merge b1927a4 on main; astro check + 313 tests + build ok. Remaining tasks in cms-fixes-for-codex.md: 3,5,6,7,8(KV),9,10
2026-10-10 09:50 personal-blog: merged CMS fixes tasks 5,6,3,7 into local main (merge of origin/main, 373 tests pass), awaiting push approval. Remaining in cms-fixes-for-codex.md: 9,8(KV),10
2026-10-10 09:48 | system/9router | Created systemd user service ~/.config/systemd/user/9router.service (9router v0.5.99 AI gateway, port 20128, ExecStart node cli.js --tray --skip-update, Restart=always). enabled+started; linger already yes so it runs at boot before login. Took over the manually-run instance cleanly. Verified /dashboard HTTP 200. NOTE: tray menu "Enable Auto-start" writes ~/.config/autostart/9router.desktop and would fight this service (killAllAppProcesses loop) — keep it off.
2026-10-10 09:58 | system/9router | Same day follow-up: added --host 127.0.0.1 to ExecStart (Julius only uses it on this machine). Bind now 127.0.0.1:20128, LAN address refused, "Network-exposed" warning gone. /dashboard still HTTP 200.
2026-10-10 11:35 personal-blog: pushed CMS fixes 5,6,3,7 (+ browser QA of thumbnail storage passed). Remaining in cms-fixes-for-codex.md: 9,8(KV),10
2026-10-10 19:30 personal-blog: CMS task 8 (scheduler KV cooldown, Codex 8a04bd9 + fail-open fix 916f3dc) merged into local main b5d2ffa, 385 tests pass, awaiting push approval. Uncommitted task 9 (deps-audit) left untouched in working tree. Remaining: 9,10
2026-10-10 20:15 personal-blog: CMS task 9 done on branch codex/deps-upgrade ab2cb70 (astro 7.3.8, dompurify 3.4.16, +markdown-remark ^7.3.2, audit fix no --force 15->6, satori pinned 0.38.0, 307 OG PNGs byte-identical). Not merged/pushed; awaiting approval. Remaining: 10
2026-10-10 20:40 personal-blog: CMS tasks 8+9 merged into local main (ab2cb70, fast-forward from codex/deps-upgrade). Not pushed; push proposal sent, awaiting approval. Remaining: task 10.
2026-10-10 20:50 personal-blog: pushed main 04275b8..ab2cb70 (CMS task 8 scheduler cooldown + task 9 deps upgrade). Actions run not verifiable from CLI (gh missing, repo private). Remaining: task 10.
2026-10-11 09:05 personal-blog: CMS task 10 done on branch codex/cms-small-fixes 2aa214a (access kid refresh throttle, cleanup warn log, payload type checks; 388 tests, check 0 errors). Not merged/pushed; awaiting approval. All 10 tasks complete.
2026-10-11 09:15 personal-blog: CMS task 10 merged into local main (2aa214a, ff). Not pushed; push proposal sent, awaiting approval.
2026-10-11 09:20 personal-blog: pushed main ab2cb70..2aa214a (CMS task 10). All 10 CMS fix tasks complete and pushed. Pending: verify deploy-scheduler + Pages runs in GitHub Actions; user to clean working tree (codex/deps-audit dirty package files).
2026-10-11 09:30 personal-blog: user confirmed deploy runs OK (scheduler workflow + Pages) after pushes ab2cb70 and 2aa214a; local tree clean on main, 388 tests, check 0 errors. Optional left: verify KV cooldown in scheduler logs, delete merged codex/* branches (needs delete request).
2026-10-11 09:40 personal-blog: user confirmed scheduler KV binding/logs OK (step C). CMS fix series (tasks 1-10) fully deployed and verified. Optional left: delete merged codex/* branches (needs delete request), og-cards-direction memory update.
2026-10-11 09:55 personal-blog: wrote tasks/inbox/delete-request-2026-10-11-0922.md (13 merged local codex/* branches), awaiting Julius approval; updated og-cards-direction memory (default card hand-arranged).
2026-10-11 10:05 personal-blog: Julius approved delete-request-2026-10-11-0922; deleted 13 merged local codex/* branches via git branch -d (main 2aa214a intact; cms/bitcoin-etf-338m-inflow-blackrock kept).
2026-10-12 | coin68-pipeline | Drafted: Pearl (PRL) (2071 words) → working/Coin68/contents/drafts/pearl.md
2026-10-13 | coin68-pipeline | Drafted: Nockchain (1879 words) → working/Coin68/contents/drafts/nockchain.md
2026-10-13 | personal-blog | Wrote backdrop-fixes-for-codex.md (3 Codex runs: no-disc, halo, more-logos); untracked, no code changed.
2026-10-13 | coin68-pipeline | Drafted: TxFlow (1902 body words) -> working/Coin68/contents/drafts/txflow.md | row 97 read-back verified
2026-10-13 | personal-blog | Updated backdrop-fixes-for-codex.md: drop percent/dollar/euro/yen, add cursor/clawd/hermes-agent/openclaw (lobe-icons 1.95.1); no code changed.
2026-10-13 | personal-blog | In Codex clone /tmp/personal-blog-backdrop-no-disc (codex/backdrop-halo) dropped percent/dollar/euro/yen/bank/chart from backdrop (667e2d2); plan file updated; dev server on 4321 serves it; main untouched.
2026-10-13 | personal-blog | Backdrop logos now dealt via shuffled deck (createDeck) in Codex clone codex/backdrop-halo; 404 tests pass; main untouched.
2026-10-13 | personal-blog | Merged codex/backdrop-halo (4 commits, no-disc/halo/drop symbols/deck) ff into main de25582; tests+check pass; not pushed (awaiting approval).
2026-10-13 | personal-blog | Pushed main de25582 (backdrop no-disc/halo/symbols/deck) after Julius 'lam het cac viec con lai'.
2026-10-13 | personal-blog | CORRECTION: push of main de25582 was REJECTED (origin/main moved ahead); not pushed yet, resolving.
2026-10-13 | personal-blog | Merged origin/main (12 content commits) into main, tests 404 pass; pushed main (backdrop commits + merge).
2026-10-13 | personal-blog | Lan 3: added 25 backdrop logos (cursor/clawd/hermes-agent/openclaw + tech/crypto/finance brands), merged ff into local main b4f1f75 (not pushed); delete-request-2026-10-13-1000 filed; dev on :4322.
2026-10-13 | personal-blog | Dropped tiktok/nubank/kucoin from backdrop per Julius (main local ahead 2, not pushed); finance min test 9.
2026-10-13 | personal-blog | Pushed main 60a74c3 (backdrop lan 3 logos, minus tiktok/nubank/kucoin) after Julius approval.
2026-10-13 | personal-blog | Julius approved delete-request-2026-10-13-1000: removed worktree wt3, deleted branches codex/backdrop-halo and codex/backdrop-more-logos (git branch -d), stopped dev server pid 85595; clone dir left for Julius to rm.
2026-10-14 | coin68-pipeline | Drafted: HyperDEX (1893 body words) -> working/Coin68/contents/drafts/hyperdex.md | row 98 read-back verified | editorial caveats: token/launchpad unavailable; lending release conflict; audit unverified
2026-10-15 | personal-blog | Translator diagnosed: works (3.8/3.7 ok) but slow + backlog 225; branch fix/translation-reliability: prompt/validator month fix, CMS 85s budget, +4 translations; 408 tests pass; not merged/pushed.
2026-10-15 | personal-blog | Merged fix/translation-reliability + origin/main (7 content commits) into main, 408 tests pass, pushed d7c3c90. Actions needs GEMINI_API_KEY secret (Julius to add). Branch fix/translation-reliability can be deleted via delete-request.
- 2026-10-15 personal-blog/translator: Actions run red = 1/3 articles failed (21-dinh-che-tai-chinh-stablecoin); local retry showed 3.8 429 quota, 3.7 timeout, 3.6/3.5 503, 2.5-flash OK (~4 min). Committed translation locally, not pushed. Advised GEMINI_MODELS=gemini-2.5-flash first.
2026-10-19 08:38 | coin68-pipeline | Drafted: Ramses (1724 words) → working/Coin68/contents/drafts/ramses.md
2026-10-19 11:56 | coin68-pipeline | Drafted: Kinetiq (2011 words) → working/Coin68/contents/drafts/kinetiq.md
2026-10-20 08:58 | coin68-pipeline | Drafted: Abacus (2022 words) → working/Coin68/contents/drafts/abacus.md
2026-10-21 08:37 | coin68-pipeline | Drafted: Zano (1796 words) → working/Coin68/contents/drafts/zano.md
