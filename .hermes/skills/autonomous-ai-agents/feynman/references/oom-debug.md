# OOM Kill Debug for Feynman Cron Jobs

**Symptom:** Feynman process spawned via cron gets SIGKILL (exit -9) after ~2 seconds, wrapper script exits 0.

**Root Cause:** Cron jobs run under systemd/cgroups with different memory limits than interactive shells. The Feynman process is killed by OOM killer, not by normal exit.

## Debug Steps

1. **Check if OOM killer triggered:**
```bash
dmesg | grep -i "killed process" | tail -10
journalctl -k | grep -i "killed process" | tail -10
```

2. **Compare memory limits:**
```bash
echo "=== Memory Limit (Manual) ==="
ulimit -v
echo "=== Memory Limit (Cron) ==="
# Add to cron:
* * * * * ulimit -v > /tmp/cron-ulimit.txt
# Then compare:
diff <(ulimit -v) /tmp/cron-ulimit.txt
```

3. **Monitor memory usage during spawn:**
```bash
# In wrapper script, add:
echo "Memory before spawn: $(free -h)" >> /tmp/feynman_debug.log
# Spawn Feynman
echo "Memory after spawn: $(free -h)" >> /tmp/feynman_debug.log
```

4. **Check systemd cron service limits:**
```bash
systemctl show cron | grep Memory
# If MemoryMax is set, increase it:
sudo systemctl edit cron
# Add:
[Service]
MemoryMax=4G
systemctl daemon-reload && systemctl restart cron
```

## Solutions

### Quick Fix: Use ulimit in wrapper
```bash
# In run_feynman_v3.py, before spawn:
import resource
resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))  # 4GB
```

### Proper Fix: Increase cron cgroup limit
Edit systemd cron config:
```bash
sudo systemctl edit cron
[Service]
MemoryAccounting=yes
MemoryMax=4G
MemoryLimit=4G
```

### Workaround: Run via user systemd timer instead of cron
User timers inherit user session limits:
```bash
# ~/.config/systemd/user/feynman.service
[Service]
ExecStart=/usr/bin/python3 /home/julius/run_feynman_v3.py

# ~/.config/systemd/user/feynman.timer
[Timer]
OnCalendar=*-*-* 09:00:00

systemctl --user enable --now feynman.timer
```

## Env Differences

Cron env is minimal. Always source profile in wrapper:
```python
import os
os.environ.update({
    'PATH': '/home/julius/.local/bin:' + os.environ.get('PATH', ''),
    'HOME': '/home/julius',
    'USER': 'julius',
})
```

## Testing

Before deploying to cron, test via systemd-run with same limits:
```bash
systemd-run --user -p MemoryMax=1G -p MemoryLimit=1G feynman chat '/deepresearch test'
```
