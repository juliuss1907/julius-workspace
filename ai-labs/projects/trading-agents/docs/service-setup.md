# Service Setup Guide

> **Scope:** Three ways to keep the trading runtime alive across sessions, from least to most permanent.
> **Default for Phase 9B:** Method A (`nohup` + `runtime_control`) — see `runtime-runbook.md` for the standard flow.
> **Last updated:** 2026-06-09

This guide does **not** install anything automatically. It provides reference templates and command sequences you can copy.

---

## Method A: `nohup` + `runtime_control.py` (default, recommended)

**Best for:** local dev, ad-hoc runs, no systemd access.

**Pros:** zero install, easy to inspect, integrated with `runtime_control` and process lock.
**Cons:** dies on system reboot, no auto-restart on crash (use supervisor for that).

```bash
cd /home/julius/julius-workspace/ai-labs/projects/trading-agents

# Start
./venv/bin/python scripts/runtime_control.py start

# Check
./venv/bin/python scripts/runtime_control.py status

# Stop
./venv/bin/python scripts/runtime_control.py stop

# Force stop (last resort)
./venv/bin/python scripts/runtime_control.py stop --force
```

If you want to run the supervisor alongside (auto-restart on crash):

```bash
# Edit config/default_params.yaml: runtime.supervisor.enabled: true
# Start supervisor in foreground (separate terminal or tmux)
./venv/bin/python scripts/runtime_supervisor.py --loop
```

**This is the recommended path until you have run the system for at least 2 weeks without supervisor intervention.**

---

## Method B: `tmux` session

**Best for:** SSH sessions, multi-pane ops view.

**Pros:** keeps runtime alive across SSH disconnects, easy to detach/reattach, visible logs.
**Cons:** still dies on system reboot, requires `tmux` install (usually present on Linux).

```bash
# Start a named session
tmux new -s trading -d './venv/bin/python scripts/runtime_supervisor.py --loop'

# Attach
tmux attach -t trading

# Detach: Ctrl-b then d

# List sessions
tmux ls

# Kill session
tmux kill-session -t trading
```

Or, for the runtime itself (not supervisor):

```bash
tmux new -s runtime -d './venv/bin/python scripts/runtime_control.py start'
# To actually start the runtime inside the session, attach and run:
./venv/bin/python scripts/runtime_control.py start
```

**Note:** `runtime_control start` already daemonizes the runtime, so wrapping it in `tmux` is mostly for log visibility. The recommended pattern is:

```bash
# Pane 1: runtime
tmux new -s runtime -d './venv/bin/python scripts/runtime_control.py start'
sleep 2
./venv/bin/python scripts/runtime_control.py status

# Pane 2: tail logs (attach and split)
tmux attach -t runtime
# Ctrl-b %  (split vertical)
# Ctrl-b arrow (move to other pane)
# tail -f logs/paper_trading.log
```

---

## Method C: `systemd` user service

**Best for:** VPS, always-on box, auto-start on boot.

**Pros:** survives reboot, auto-restart on crash, integrated with `journalctl`.
**Cons:** requires `systemd` (Linux only), more setup, harder to debug.

**Do not enable this until Methods A and B have been used for at least 1 week without issues.**

### Step 1: install template

Copy `ops/systemd/trading-runtime.service.example` to `~/.config/systemd/user/trading-runtime.service`:

```bash
mkdir -p ~/.config/systemd/user
cp ops/systemd/trading-runtime.service.example \
   ~/.config/systemd/user/trading-runtime.service

# Edit paths inside to match your install
$EDITOR ~/.config/systemd/user/trading-runtime.service
```

### Step 2: enable lingering (so user services run without login)

```bash
sudo loginctl enable-linger $USER
```

### Step 3: reload and start

```bash
systemctl --user daemon-reload
systemctl --user enable trading-runtime.service
systemctl --user start trading-runtime.service

# Check status
systemctl --user status trading-runtime.service
journalctl --user -u trading-runtime.service -n 50

# Stop
systemctl --user stop trading-runtime.service
```

### Step 4 (optional): supervisor service

Same flow with `ops/systemd/runtime-supervisor.service.example`.

**Important:** only enable the supervisor service if `runtime.supervisor.enabled: true` and `mode: auto_restart` in config. Otherwise the supervisor service is a no-op.

### Service lifecycle

| Action | Command |
|---|---|
| Start | `systemctl --user start trading-runtime.service` |
| Stop | `systemctl --user stop trading-runtime.service` |
| Restart | `systemctl --user restart trading-runtime.service` |
| Status | `systemctl --user status trading-runtime.service` |
| Logs | `journalctl --user -u trading-runtime.service -f` |
| Disable on boot | `systemctl --user disable trading-runtime.service` |

### Interaction with process lock

The systemd unit **does not** bypass the process lock. If you `systemctl start` while a runtime is already running, the new process will exit because the lock is held. This is by design.

To replace a running runtime:

```bash
systemctl --user stop trading-runtime.service
# Wait for clean shutdown
systemctl --user start trading-runtime.service
```

Or use `runtime_control restart` instead of systemd commands — both are valid.

---

## Comparison matrix

| Aspect | Method A (nohup + runtime_control) | Method B (tmux) | Method C (systemd) |
|---|---|---|---|
| Survives SSH disconnect | No | Yes | Yes |
| Survives reboot | No | No | Yes |
| Auto-restart on crash | Via supervisor only | No | Yes (Restart=always) |
| Log access | `tail -f logs/*.log` | Same + tmux pane | `journalctl -f` |
| Setup time | 0 min | 1 min | 15 min |
| Required for Phase 9B? | Yes (default) | No | No |
| Recommended next step | — | Optional, for ops view | After 1+ week of A |

---

## Anti-patterns

- **Running runtime directly with `python` (no `runtime_control`)** — bypasses lock, health, log rotation.
- **Wrapping `runtime_control` in `nohup` AND systemd** — double supervision, races.
- **Editing service files in `~/.config/systemd/user/` and pushing to git** — service files are user-specific, not project artifacts. The `ops/systemd/*.example` files are templates only.
- **Enabling supervisor + systemd Restart=always** — both will try to restart, leading to flapping. Pick one.
- **Setting `Restart=always` without supervisor** — fine, but you lose `blocked_by_budget` semantics. Either trust systemd's restart loop, or use supervisor's budget.

---

## When to upgrade to Method C

Upgrade to `systemd` only when:
1. Method A has been stable for `>= 7` days
2. You want auto-start on boot
3. The host is a VPS or always-on box (not a laptop)

If the host is your main machine and you regularly suspend/hibernate, Method A is sufficient.

---

## See also

- `runtime-runbook.md` — operational flows
- `daily-ops-checklist.md` — pre-flight and end-of-session checks
- `alerting-policy.md` — when to react
- `config-promotion-checklist.md` — config change gate
- `ops/systemd/trading-runtime.service.example` — service template
- `ops/systemd/runtime-supervisor.service.example` — supervisor service template
