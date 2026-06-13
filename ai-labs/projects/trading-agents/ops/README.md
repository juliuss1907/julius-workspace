# ops/

Operational templates and helper scripts.

## systemd/

Reference `*.service` files for running the trading runtime and supervisor as user-level systemd services.

These are **templates only** — do not symlink them directly into `~/.config/systemd/user/`. Always copy and edit:

```bash
mkdir -p ~/.config/systemd/user
cp ops/systemd/trading-runtime.service.example \
   ~/.config/systemd/user/trading-runtime.service
$EDITOR ~/.config/systemd/user/trading-runtime.service

systemctl --user daemon-reload
systemctl --user enable trading-runtime.service
systemctl --user start trading-runtime.service
```

See `docs/service-setup.md` for the full walkthrough and the comparison between `nohup`, `tmux`, and `systemd`.

## Why no auto-install

The runtime is currently in conservative rollout. Service installation must be intentional:

- It changes process supervision model
- It persists across reboots (which may surprise the operator)
- It can race with `runtime_control` if both are used

`docs/service-setup.md` lists the prerequisites (>= 1 week of stable `nohup` operation) before enabling systemd.

## When you edit templates

If you change ExecStart paths, WorkingDirectory, or resource limits, update **both**:

1. The `.example` file (this repo)
2. The operator's local copy in `~/.config/systemd/user/`

Do not commit the local copy. It is host-specific.
