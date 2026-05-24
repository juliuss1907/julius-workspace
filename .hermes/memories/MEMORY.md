X posts: CT voice with degen slang, crypto tie-in, chill/sarcastic, 2-5 emojis. Use x-post-writer skill.
§
Vai trò Markus: đọc skill Julius đã build (ai-labs/resource/skills/), tư vấn thiết kế, test skill. KHÔNG tự tạo/edit skill Julius khi chưa được yêu cầu. Chỉ thêm reference files vào hermes-agent hoặc system skills.
§
Output format preference: Julius prefers flat output structure - single .md report file, no nested directories. Confirmed across multiple sessions for X research reports and other deliverables.
§
Coin68 article preferences: Team section = founders only (2 max, not all members). Funding section = full details: rounds, dates, amounts, lead investors, purpose, hyperlinks to related Coin68 articles. Variational article revised per these rules — focus on Lucas Schuermann + Edward Yu (Columbia → Qu Capital → DCG/Genesis → Variational), 3 funding rounds detailed ($10.3M Seed Oct 2024, $1.5M Strategic Jun 2025, $50M Series A May 2026).
§
MemPalace is Hermes new memory system at ~/.hermes/mempalace/ (replaces limited built-in memory). MCP server configured (needs Hermes restart). Cron auto-mine Sun 9 AM (job d16769a2bea4). Julius's machine is off at night — always schedule cron jobs during waking hours (9 AM+).
§
Feynman CLI v0.2.58: run from workdir=~/julius-workspace/personal/researchs/ so outputs stay in workspace. Auth via opencode-go (14 models, default deepseek-v4-flash).
§
Feynman workflow: Khi Feynman tạo research plan, PHẢI đọc plan từ log/file và gửi tóm tắt cho Julius TRƯỚC. Chỉ gửi "yes" cho Feynman sau khi Julius confirm. Nếu Julius từ chối, gửi "no" hoặc kill process. KHÔNG tự động confirm plan.
§
Khi chạy Feynman cho Julius, luôn yêu cầu output bằng tiếng Việt (thêm instruction vào prompt). Trừ khi Julius chỉ định ngôn ngữ khác.
§
News brief skill: Python 3.14 breaks playwright due to greenlet incompatibility. Use requests + BeautifulSoup fallback for scraping websites when playwright install fails with _PyCFrame errors. This is not transient — it's a Python version compatibility issue that persists until playwright updates their greenlet dependency for Python 3.14+