# Batch 5G — Local Dev Test Environment Setup

## Summary

Batch 5G executed `Option A — Minimal local venv` for the source-of-truth repo.

- Source repo: `/home/julius/julius-workspace/ai-labs/projects/the-trading-guy`
- Venv path: `/home/julius/julius-workspace/ai-labs/projects/the-trading-guy/.venv`
- Expected source commit: `b83fb38292a24f260f7372ab557326b2ba50093d`
- Status: `completed`

## Preflight

Source repo status before setup:

```text
returncode=0
stdout:
## main...origin/main
stderr:
<empty>
```

HEAD / origin / remote:

```text
HEAD:        b83fb38292a24f260f7372ab557326b2ba50093d
origin/main: b83fb38292a24f260f7372ab557326b2ba50093d
remote main: b83fb38292a24f260f7372ab557326b2ba50093d
```

Python:

```text
returncode=0
stdout:
Python 3.14.3
stderr:
<empty>
```

`requirements-dev.txt`:

```text
pytest
pytest-asyncio
```

`.venv/` ignore check:

```text
returncode=0
stdout:
.gitignore:16:.venv	.venv/
stderr:
<empty>
```

Pre-existing `.venv`:

```json
{
  "exists": false,
  "is_dir": false
}
```

## Execution

No pip upgrade was run. Dependencies were installed only into `.venv` using:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
```

Install result:

```text
returncode=0
stdout:
Collecting pytest (from -r requirements-dev.txt (line 1))
  Downloading pytest-9.1.1-py3-none-any.whl.metadata (7.6 kB)
Collecting pytest-asyncio (from -r requirements-dev.txt (line 2))
  Using cached pytest_asyncio-1.4.0-py3-none-any.whl.metadata (4.1 kB)
Collecting iniconfig>=1.0.1 (from pytest->-r requirements-dev.txt (line 1))
  Using cached iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
Collecting packaging>=22 (from pytest->-r requirements-dev.txt (line 1))
  Using cached packaging-26.2-py3-none-any.whl.metadata (3.5 kB)
Collecting pluggy<2,>=1.5 (from pytest->-r requirements-dev.txt (line 1))
  Using cached pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
Collecting pygments>=2.7.2 (from pytest->-r requirements-dev.txt (line 1))
  Using cached pygments-2.20.0-py3-none-any.whl.metadata (2.5 kB)
Downloading pytest-9.1.1-py3-none-any.whl (386 kB)
Using cached pluggy-1.6.0-py3-none-any.whl (20 kB)
Using cached pytest_asyncio-1.4.0-py3-none-any.whl (16 kB)
Using cached iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Using cached packaging-26.2-py3-none-any.whl (100 kB)
Using cached pygments-2.20.0-py3-none-any.whl (1.2 MB)
Installing collected packages: pygments, pluggy, packaging, iniconfig, pytest, pytest-asyncio

Successfully installed iniconfig-2.3.0 packaging-26.2 pluggy-1.6.0 pygments-2.20.0 pytest-9.1.1 pytest-asyncio-1.4.0
stderr:
[notice] A new release of pip is available: 25.1.1 -> 26.1.2
[notice] To update, run: /home/julius/julius-workspace/ai-labs/projects/the-trading-guy/.venv/bin/python -m pip install --upgrade pip
```

Installed relevant dev packages:

```text
returncode=0
stdout:
iniconfig==2.3.0
packaging==26.2
pluggy==1.6.0
pytest==9.1.1
pytest-asyncio==1.4.0
stderr:
<empty>
```

## Safe Test Result

Command:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
```

Result:

```text
returncode=0
stdout:
....                                                                     [100%]
4 passed in 0.03s
stderr:
<empty>
```

## Post-Setup Repository Cleanliness

Source repo status after setup:

```text
returncode=0
stdout:
## main...origin/main
stderr:
<empty>
```

Tracked local/dev/generated file check:

```text
returncode=0
stdout:
<empty>
stderr:
<empty>

returncode=0
stdout:
<empty>
stderr:
<empty>
```

Ignored local artifact sample:

```text
returncode=0
stdout:
!! .venv/
stderr:
<empty>
```

## Stop Reasons

```json
[]
```

## Safety Boundary Confirmation

- No live trading executed.
- No order placement executed.
- No simulate-live execution.
- No StrategySignal-to-order bridge added or touched.
- No runtime/default config mutated.
- No `.env` files read, printed, or committed.
- No global package install.
- No `sudo` usage.
- No `pip install --user`.
- No pip upgrade.
- No full test suite execution.
- No replay/monitoring jobs executed.
- No raw replay logs staged or committed.
- No scheduler/cron/systemd enablement.
- No push executed.

## Recommended Local Command Going Forward

```bash
cd /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
.venv/bin/python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
```
