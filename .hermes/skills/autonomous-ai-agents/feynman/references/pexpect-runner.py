#!/usr/bin/env python3
"""
Pexpect-based Feynman runner with PTY support.

Use this when:
- process(action="submit") to PTY fails
- Need auto-confirm for unattended runs
- Cron jobs that require interactive input

Exit codes:
- 0: Success
- 1: Timeout waiting for plan
- 2: Timeout waiting for research
- 3: Process killed/OOM
"""
import pexpect
import sys
import os
import time
import signal

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def run_feynman(topic, workdir='/tmp', confirm=True):
    os.chdir(workdir)
    
    log("Spawning Feynman...")
    child = pexpect.spawn(
        f"feynman chat '/deepresearch {topic}'",
        encoding='utf-8',
        timeout=900,
        dimensions=(40, 120)
    )
    
    # Stage 1: Wait for plan prompt
    log("Waiting for plan prompt (max 180s)...")
    try:
        idx = child.expect(["Proceed with this deep research plan", pexpect.TIMEOUT], timeout=180)
        if idx == 0:
            log("Plan prompt detected!")
        else:
            log("TIMEOUT waiting for plan prompt")
            child.close()
            sys.exit(1)
    except Exception as e:
        log(f"Error: {e}")
        child.close()
        sys.exit(1)
    
    # Stage 2: Confirm
    if confirm:
        log("Sending yes...")
        child.sendline("yes")
    else:
        log("Auto-confirm disabled, waiting...")
    
    # Stage 3: Wait research complete
    log("Waiting for research to complete (max 14 min)...")
    try:
        child.expect(pexpect.EOF, timeout=840)
        log("RESEARCH COMPLETE!")
    except pexpect.TIMEOUT:
        log("TIMEOUT - research did not finish in 14 min")
        child.close()
        sys.exit(2)
    
    # Check exit status
    child.close()
    log(f"Exit: {child.exitstatus}")
    
    if child.signalstatus == signal.SIGKILL:
        log("WARNING: Process killed by SIGKILL (OOM?)")
        sys.exit(3)
    
    sys.exit(child.exitstatus)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} '<topic>' [confirm=true/false]", file=sys.stderr)
        sys.exit(1)
    
    topic = sys.argv[1]
    confirm = sys.argv[2].lower() != 'false' if len(sys.argv) > 2 else True
    
    run_feynman(topic, confirm=confirm)
