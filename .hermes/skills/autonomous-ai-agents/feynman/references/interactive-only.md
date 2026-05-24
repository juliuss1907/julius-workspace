/**
 * Feynman CLI v0.2.58 Interactive-Only Constraint
 * 
 * DISCOVERY: Feynman CLI v0.2.58 ONLY works in real interactive terminal sessions.
 * All attempts at non-interactive execution fail:
 * 
 * ❌ nohup → stalls 14+ min → SIGKILL (exit -9)
 * ❌ expect.spawn() → captures banner only, plan content empty
 * ❌ tmux session → plan prompt appears but content missing 
 * ❌ python pty.fork() → timeout 5 min, captured 318KB of retry loops
 * ❌ echo "yes" | feynman → produces ZERO output (no PTY)
 * 
 * Root cause: Feynman calls tcsetattr() and requires full TTY controls.
 * Non-interactive modes cause ioctl failures → Feynman stalls forever.
 * 
 * ✅ ONLY SOLUTION: Run manually from terminal.
 * Cron/background automation is IMPOSSIBLE with current Feynman version.
 * 
 * Workflow for Julius:
 * 1. cd ~/julius-workspace/personal/researchs
 * 2. feynman chat '/deepresearch TOPIC, trình bày bằng tiếng Việt'
 * 3. Wait for "Proceed with this deep research plan?"
 * 4. Reply "yes"
 * 5. Wait 5-15 minutes for completion
 * 6. Check outputs in /tmp/outputs/ (Feynman ignores workdir!)
 * 
 * Session: 2026-05-22, tested all methods, confirmed failure.
 */