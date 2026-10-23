# Workflow — Coin68 Writer

Step-by-step process for writing Coin68 articles.

---

## Phase 1: Research

### Step 1.1: Read task requirements

From task file, extract:
- Project name
- Article type (news/review/deep-dive)
- Deadline
- Context files referenced

### Step 1.2: Read domain context

```bash
cd ~/julius-workspace/working/Coin68

# Read brand context
cat context/coin68.md

# Read category index
cat contents/published/published.md
```

Identify which category this project belongs to (perpdex, defi, layer1, layer2, etc.)

### Step 1.3: Gather sources

**Primary sources (required):**
- Project website
- Project documentation
- Official Twitter/social media

**Secondary sources (if available):**
- Whitepaper
- GitHub repository
- Team LinkedIn profiles
- Investor announcements
- News articles about the project

**Internal sources:**
- `knowledge-base/wiki/concepts/` (search for related concepts)
- `working/Coin68/contents/published/` (read 2-3 similar articles for voice)

### Step 1.4: Verify facts

For each key claim, note:
- Source URL
- Date accessed
- Confidence level (confirmed / claimed by project / unverified)

**Red flags requiring escalation:**
- Team members with no online presence
- Investors not confirmed on their official sites
- Tokenomics numbers that don't add up
- Contradictory information across sources

---

## Phase 2: Outline

### Step 2.1: Choose template

Based on article type:
- **Review** → Use Review template (see templates.md)
- **News** → (template TBD)
- **Deep-dive** → (template TBD)

### Step 2.2: Map content to sections

For Review template:

```
H1: [Project] là gì? Tìm hiểu về [description]
  H2: [Project] là gì?
       2-3 sentences definition
  H2: Điểm nổi bật của [Project]
       H3: [Feature 1]
       H3: [Feature 2]
       H3: [Feature 3-6]
  H2: [Sản phẩm/Cơ chế chính] (optional)
       H3: [Component 1]
       H3: [Component 2]
  H2: Đội ngũ phát triển
  H2: Nhà đầu tư [và đối tác]
  H2: Tokenomics (if applicable)
  H2: Tổng kết
```

### Step 2.3: Identify gaps

If any required section lacks content:
- Can it be found from additional research?
- Can it be omitted (optional sections only)?
- Does it require escalation?

---

## Phase 3: Draft

### Step 3.1: Write frontmatter

```yaml
---
type: article
category: review
project: [Project Name]
main_tag: crypto
sub_tags: [perpdex, defi]
status: draft
created: YYYY-MM-DD
---
```

### Step 3.2: Write H1 title

Format: `[Project] là gì? Tìm hiểu về [short description]`

Examples:
- `Phoenix là gì? Tìm hiểu về fully on-chain perp DEX trên Solana`
- `PrismaX là gì? Tìm hiểu về hạ tầng dịch vụ cho robotics`
- `Pixie Chess là gì? Tìm hiểu về game cờ vua Web3 trên blockchain Base`

### Step 3.3: Write "là gì?" section

2-3 sentences:
1. What the project is (category + blockchain)
2. Core value proposition
3. Key differentiator (optional)

Example:
```markdown
## Phoenix là gì?

Phoenix là perp DEX được xây dựng hoàn toàn trên blockchain Solana bởi Ellipsis Labs. Với kiến trúc fully on-chain và sử dụng matching engine kép kết hợp sổ lệnh FIFO truyền thống với Spline liquidity độc quyền, Phoenix mang đến trải nghiệm giao dịch perpetual futures với tốc độ và hiệu quả vốn cao.
```

### Step 3.4: Write "Điểm nổi bật" section

List 3-6 key features as H3 subsections.

**Feature selection criteria:**
- Technical innovations (architecture, consensus, novel mechanisms)
- User benefits (lower fees, faster transactions, better UX)
- Ecosystem advantages (partnerships, integrations, network effects)

**Feature writing pattern:**
```markdown
### [Feature name in Vietnamese]

[1-2 paragraphs explaining the feature]
[Include technical details if relevant]
[Explain user benefit]
```

### Step 3.5: Write optional sections

**"Sản phẩm chính" or "Cơ chế hoạt động":**
- Use when project has multiple products/components
- Each component gets H3 subsection
- Explain how components work together

**"Vòng lặp kinh tế" or "Các cách tham gia":**
- Use for projects with complex tokenomics or user flows
- Explain the flywheel or participation mechanisms

### Step 3.6: Write "Đội ngũ phát triển"

Format:
```markdown
## Đội ngũ phát triển

[Project] được phát triển bởi [Company/Team Name], do [Founder Name] sáng lập.

[Optional: 1-2 sentences about founder background]

[Optional: Notable team members with relevant experience]
```

If team is anonymous or minimal info available:
```markdown
## Đội ngũ phát triển

Đội ngũ phát triển [Project] hoạt động dưới dạng pseudonymous, tập trung vào việc xây dựng sản phẩm và cộng đồng thay vì branding cá nhân.
```

### Step 3.7: Write "Nhà đầu tư"

Format:
```markdown
## Nhà đầu tư [và đối tác]

[Project] đã huy động được [amount] trong vòng [round name] do [lead investor] dẫn đầu, với sự tham gia của [other investors].

[Optional: Notable partnerships or integrations]
```

If no funding info:
```markdown
## Nhà đầu tư

Thông tin về nhà đầu tư của [Project] chưa được công bố công khai.
```

### Step 3.8: Write "Tokenomics" (if applicable)

Only include if project has a token. Format:
```markdown
## Tokenomics

**Token:** [Symbol]
**Tổng cung:** [Total supply]
**Phân bổ:**
- [Category 1]: [percentage]
- [Category 2]: [percentage]
- [Category 3]: [percentage]

[Optional: Vesting schedule, utility, governance]
```

### Step 3.9: Write "Tổng kết"

2-3 sentences wrapping up:
1. Restate core value proposition
2. Current status or next milestone
3. Neutral closing (no investment advice)

Example:
```markdown
## Tổng kết

Phoenix là một perp DEX fully on-chain trên Solana với kiến trúc matching engine độc đáo, hướng tới mục tiêu mang đến trải nghiệm giao dịch perpetual futures nhanh chóng và hiệu quả vốn cao. Dự án hiện đang trong giai đoạn testnet và dự kiến ra mắt mainnet trong Q2/2026.
```

---

## Phase 4: Verification

### Step 4.1: Fact-check

Go through article line by line:
- [ ] Every number has a source
- [ ] Every claim about team/investors is verified
- [ ] Technical terms are used correctly
- [ ] No speculation presented as fact

### Step 4.2: Terminology check

- [ ] English terms kept where appropriate (perp DEX, not "sàn giao dịch vĩnh viễn")
- [ ] Vietnamese terms used correctly (huy động vốn, not "raise capital")
- [ ] No awkward translations

### Step 4.3: Neutrality check

Remove or rephrase:
- [ ] Hype language ("revolutionary", "game-changing")
- [ ] Investment advice ("should buy", "good opportunity")
- [ ] Unverified superlatives ("best", "fastest", "most secure")

### Step 4.4: Structure check

- [ ] All required sections present
- [ ] Heading hierarchy correct (H1 → H2 → H3, no skips)
- [ ] Logical flow (intro → features → team → conclusion)
- [ ] Length appropriate (1000-2000 words for Review)

---

## Phase 5: Proofread

### Step 5.1: Grammar and spelling

- [ ] Vietnamese grammar errors
- [ ] Typos
- [ ] Punctuation
- [ ] Consistent terminology

### Step 5.2: Formatting

- [ ] Frontmatter complete
- [ ] Bold used correctly (project name first mention, key numbers)
- [ ] Bullet points formatted consistently
- [ ] No markdown images
- [ ] No emoji
- [ ] Code blocks only for code (not for emphasis)

### Step 5.3: Final read

Read the entire article as if you are a Coin68 reader:
- Does it answer "What is [Project]?"
- Is it informative without being promotional?
- Would you understand the project after reading?

---

## Phase 6: Delivery

### Step 6.1: Save to correct location

```bash
cd ~/julius-workspace/working/Coin68/contents/drafts
# File: <project-slug>.md
```

### Step 6.2: Update task file

In task file Section 5: Notes, add:
```markdown
**Output location:** working/Coin68/contents/drafts/<project-slug>.md
**Word count:** [actual count]
**Sources used:** [list key sources]
**Verification notes:** [any claims that could not be verified]
```

### Step 6.3: Notify Julius

```
[TASK COMPLETE]
Task: Write Coin68 article about [Project]
Output: working/Coin68/contents/drafts/<project-slug>.md
Word count: [X] words
Ready for review.
```

---

## Error Handling

### If source material is insufficient

Escalate with specific gaps:
```
Cannot complete article for [Project] due to missing information:
- Team: No founder info on website or LinkedIn
- Investors: Claimed [X] raised but no announcement found
- Tokenomics: Whitepaper mentions token but no distribution details

Options:
A. Proceed with available info, note gaps in article
B. Wait for Julius to provide additional sources
C. Skip sections that lack info (if optional)
```

### If project category is unclear

Check `working/Coin68/contents/published/published.md` for existing categories. If no match, escalate:
```
[Project] does not fit existing Coin68 categories.
Suggested new category: [your suggestion]
Or closest match: [existing category]
```

### If deadline is impossible

Escalate immediately with realistic timeline and options:
```
Task deadline: [date]
Estimated time needed: [X hours] for research + [Y hours] for writing
Reason: [explain complexity]

Options:
A. Extend deadline to [new date]
B. Reduce scope (shorter article, fewer sources)
C. Prioritize over other tasks
```

---

**Last updated:** 2026-05-04
