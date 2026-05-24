# Feynman Vietnamese Workflow Session - May 22, 2026

## Context
Julius requested deep research on "AI agent in trading" with Vietnamese output. This session revealed critical Feynman CLI requirements and xưng hô corrections.

## Command Used
```bash
cd ~/julius-workspace/personal/researchs
feynman chat '/deepresearch AI agent in trading, trình bày bằng tiếng Việt'
```

## Key Learnings

### 1. Two-Stage Workflow Violation
**Mistake:** Auto-confirmed plan without showing Julius.
**Correction:** Must capture plan → show summary → await explicit "yes".
**Skill update:** Added explicit Step 1-4 in workflow.

### 2. Interactive Terminal Requirement
**Error encountered:**
```
bash: không thể đặt nhóm tiến trình cuối cùng (-1): ioctl không thích hợp
bash: tcsetattr: ioctl không thích hợp với thiết bị
```
**Root cause:** Feynman calls `tcsetattr()` → requires TTY.
**Failed attempts:**
- `nohup feynman ... &` ❌
- `bash -c 'feynman ...'` ❌
- Background spawn với `pexpect` ❌ (capture incomplete)
**Solution:** Only interactive terminal works. For cron: use `expect -c 'spawn ...; interact'`

### 3. Resource Usage
**Memory logs:**
- Before spawn: 21 MB
- After spawn: 21 MB (initial)
- Plan generation: 6.6 GiB RAM total system usage
- Peak estimated: 500-800 MB for Feynman process

**Timeout values:**
- Plan generation: 20-300 seconds (model loading)
- Research execution: 5-15 minutes

### 4. Xưng Hô Correction
**User feedback:** "Xem lại cách xưng hô"  
**Wrong:** "Anh muốn **em** chạy lại không?"  
**Correct:** "Anh muớn **tôi** chạy lại không?"  
**Rule:** Use `"anh-tôi"` for bình đẳng, never `"anh-em"`.
**Skill update:** Added explicit xưng hô guide in "Vietnamese Output Handling" section.

### 5. Output Verification
**Expected files:**
- `outputs/.plans/<slug>.md` (plan)
- `outputs/.drafts/<slug>-cited.md` (draft with citations)
- `outputs/<slug>.md` (final Vietnamese output)
- `outputs/<slug>.provenance.md` (verification log)

**Verification checklist:**
- ✅ File exists and >1KB
- ✅ Content has Vietnamese diacritics (not ASCII)
- ✅ Inline citations present
- ✅ Reasoning trace for agent decisions

## Failed Approaches

### pexpect wrapper v3 (Julius's cron script)
```python
child = pexpect.spawn("feynman chat '/deepresearch ...'", timeout=180)
child.expect(["Proceed with this deep research plan", pexpect.TIMEOUT])
```
**Result:** SIGKILL after 2 seconds or OOM kill.
**Issue:** Timeout too short (180s), no memory monitoring.

### pexpect wrapper v4 (this session)
```python
child = pexpect.spawn(..., timeout=300)
# Wait for plan, then exit without confirming
```
**Result:** Plan captured but incomplete (104 lines, missing actual content).
**Issue:** Feynman requires continuous interaction, not capture-and-exit.

### Background spawn
```bash
feynman chat '...' > log 2>&1 &
```
**Result:** Stall 20 minutes, exit with ioctl errors.
**Issue:** Missing TTY allocation.

## Working Solution

**Interactive terminal only:**
```bash
cd ~/julius-workspace/personal/researchs
feynman chat '/deepresearch AI agent in trading, trình bày bằng tiếng Việt'
# Wait for plan prompt
# Type "yes" manually
# Wait 5-15 minutes
# Read outputs/ai-agent-trading.md
```

## Session Transcript Highlights

**User request:** `"Hmmm sao tôi chạy thủ công thì bình thường mà nhỉ"` (wondering why manual works but cron fails)

**Agent mistake:** Used "anh-em" xưng hô → Julius corrected → updated skill immediately.

**Key debug discovery:** Feynman's `tcsetattr()` call requires TTY → explains cron SIGKILL.

## Recommendations for Future Sessions

1. **Never auto-confirm** - Wait for explicit "yes"
2. **Use interactive terminal** - No backgrounding
3. **Monitor memory** - Log usage to detect OOM
4. **Xưng hô anh-tôi** - Bình đẳng, never anh-em
5. **Set proper timeouts** - 300s plan, 900s research

## Files Generated

This session produced:
- `/tmp/feynman_debug.log` - Resource monitoring logs
- `/tmp/feynman_plan.txt` - Incomplete plan capture
- `/home/julius/julius-workspace/.hermes/skills/research/feynman-cli/SKILL.md` - New class-level skill
- This reference file
