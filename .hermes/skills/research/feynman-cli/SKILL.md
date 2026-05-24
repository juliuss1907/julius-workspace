---
name: feynman-cli
description: Run Feynman deep research CLI with correct two-stage workflow, interactive terminal requirements, and Vietnamese output handling.
tags: [feynman, deep-research, cli, workflow, cron]
---

# Feynman CLI Research Workflow

## When to Use

Use this skill when Julius requests deep research via Feynman CLI (`/deepresearch` or other workflows). This covers interactive sessions, background execution, and cron automation.

## Core Workflow (Two-Stage)

### Stage 1: Capture Plan

1. **Spawn Feynman in interactive mode** (NEVER use `nohup`, `&`, or cron directly)
   ```
   cd ~/julius-workspace/personal/researchs
   feynman chat '/deepresearch <topic>, trình bày bằng tiếng Việt'
   ```

2. **Wait for plan prompt**  
   Feynman will print: `"Proceed with this deep research plan?"`  
   Timeout: **300 seconds** (plan generation can take 2-5 minutes)

3. **Capture and summarize plan**  
   Show Julius a **brief summary** (not full plan) in Vietnamese. Use `anh-tôi` xưng hô.

4. **Await explicit approval**  
   Julius must reply `"yes"` before proceeding.

### Stage 2: Execute Research

5. **Send confirmation**  
   ```
   echo "yes" | feynman chat '/deepresearch <topic>, trình bày bằng tiếng Việt'
   ```
   Or use pexpect: `child.sendline("yes")`

6. **Wait research completion**  
   Duration: **5-15 minutes** typical  
   Outputs: `outputs/.drafts/<slug>-cited.md`, `outputs/<slug>.md`

7. **Deliver results**  
   - Read `outputs/<slug>.md` (final Vietnamese output)
   - Summarize key findings if needed
   - Send to Julius via telegram

## Critical Requirements

### Interactive Terminal Mandatory ❗

Feynman **requires** a real TTY. Non-interactive execution fails with ioctl errors:
```
bash: tcsetattr: ioctl không thích hợp với thiết bị
```

**DO NOT USE:**
- ❌ `nohup feynman ... &`  
- ❌ Cron jobs without TTY allocation
- ❌ `bash -c 'feynman ...'` (non-interactive)
- ❌ `expect` scripts without verifying `expect` binary exists

**Solution for Cron (requires expect):**
```bash
# 1. Verify expect is installed (Nobara/Fedora may lack it)
which expect || sudo dnf install -y expect

# 2. Use expect with pseudo-tty
expect -c 'spawn feynman chat "/deepresearch ..."; interact'
```

**Fallback when expect/tmux unavailable:**
Stop and request Julius run manual. Do not attempt expect scripts that will stall for 20+ minutes.

### Resource Monitoring

Log memory before/after spawn to detect OOM:
```python
import os, time
os.system(f"echo '[{time.strftime('%H:%M:%S')}] Memory: $(free -h)' >> /tmp/feynman_debug.log")
```

Typical memory usage:
- Before spawn: ~20 MB
- After spawn: ~140 MB (model loading)
- Peak during research: ~500-800 MB

### Timeout Values

| Stage | Timeout | Reason |
|-------|---------|--------|
| Plan generation | 300s | Model loading + agent coordination |
| Research execution | 900s | Multi-phase research pipeline |

## Vietnamese Output Handling

**Always include in prompt:**
```
'/deepresearch <topic>, trình bày bằng tiếng Việt'
```

**Xưng hô trong tóm tắt:**  
- Use **"anh-tôi"** (bình đẳng, never "anh-em")
- Example: *"Anh muốn tôi chạy lại không?"* ✓
- Wrong: *"Anh muốn em chạy lại không?"* ✗

## Cron Automation (Advanced)

If Julius requires cron-based research:

1. **Install expect**: `sudo dnf install -y expect`
2. **Use wrapper script** with pexpect
3. **Monitor for stalls**: Feynman can stall >20 min in non-TTY
4. **Log everything**: `/tmp/feynman_debug.log`

**known issues:**
- First spawn may fail due to model download → retry with backoff
- Cron service may have MemoryMax limits → check `systemctl show cron | grep Memory`

## Verification

After research completes, verify:
- ✅ `outputs/<slug>.md` exists (final output)
- ✅ File size > 1KB (non-empty)
- ✅ Content is Vietnamese (check for diacritics)
- ✅ Citations present (inline links to sources)

If verification fails, mark as `Verification: BLOCKED` in provenance.

## Pitfalls

1. **Auto-confirming plan** → Violation, always show plan first
2. **Wrong xưng hô** → Julius corrects, update skill immediately
3. **Cron without TTY** → SIGKILL or ioctl errors
4. **Short timeout** → Plan generation fails, use 300s minimum
5. **Missing language flag** → Output English instead of Vietnamese

## Example Session

See `references/feynman-vietnamese-workflow.md` for full transcript and debugging log.
