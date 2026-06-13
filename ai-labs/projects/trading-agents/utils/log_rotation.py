"""
Log Rotation — Phase 9A.2.

Size-based log rotation. Only operates on files explicitly listed
in config (`runtime.log_rotation.files`). Refuses paths outside the
project root for safety.

Public API:
  - rotate_file(path, max_bytes, keep_files, project_root) -> dict
  - rotate_all(config, project_root) -> list[dict]
  - should_rotate(path, max_bytes) -> bool

No compression. No remote upload. No deletion of arbitrary files.
"""
import os
from pathlib import Path
from typing import List, Optional


def should_rotate(path: Path, max_bytes: int) -> bool:
    """Return True if file exists and is larger than max_bytes."""
    if not path.exists():
        return False
    try:
        return path.stat().st_size > max_bytes
    except OSError:
        return False


def _is_safe_path(path: Path, project_root: Path) -> bool:
    """Return True if path is under project_root after resolution."""
    try:
        rp = path.resolve()
        rr = project_root.resolve()
    except OSError:
        return False
    try:
        rp.relative_to(rr)
        return True
    except ValueError:
        return False


def _resolve(path_str: str, project_root: Path) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = project_root / p
    return p


def rotate_file(
    path: Path,
    max_bytes: int = 10 * 1024 * 1024,
    keep_files: int = 5,
    project_root: Optional[Path] = None,
) -> dict:
    """Rotate a single file if it exceeds max_bytes.

    Behavior:
      - File missing → no-op, return skipped=True
      - File <= max_bytes → no-op
      - File > max_bytes → shift .N → .N+1, drop oldest over keep_files
      - Only rotates files under project_root
    """
    result = {
        "path": str(path),
        "rotated": False,
        "skipped": False,
        "reason": None,
        "kept_files": keep_files,
        "size_before": None,
    }

    if project_root is not None and not _is_safe_path(path, project_root):
        result["skipped"] = True
        result["reason"] = "path_outside_project_root"
        return result

    if not path.exists():
        result["skipped"] = True
        result["reason"] = "file_missing"
        return result

    try:
        size = path.stat().st_size
    except OSError as e:
        result["skipped"] = True
        result["reason"] = f"stat_error:{e}"
        return result

    result["size_before"] = size

    if size <= max_bytes:
        result["skipped"] = True
        result["reason"] = "below_threshold"
        return result

    keep = max(1, int(keep_files))

    # Drop the oldest beyond keep
    oldest = path.with_suffix(path.suffix + f".{keep}")
    if oldest.exists():
        try:
            oldest.unlink()
        except OSError:
            pass

    # Shift .N -> .N+1 from keep-1 down to 1
    for n in range(keep - 1, 0, -1):
        src = path.with_suffix(path.suffix + f".{n}")
        dst = path.with_suffix(path.suffix + f".{n+1}")
        if src.exists():
            try:
                os.replace(src, dst)
            except OSError:
                pass

    # current -> .1
    first_backup = path.with_suffix(path.suffix + ".1")
    try:
        os.replace(path, first_backup)
    except OSError as e:
        result["skipped"] = True
        result["reason"] = f"rename_error:{e}"
        return result

    # Recreate empty file
    try:
        path.touch()
    except OSError:
        pass

    result["rotated"] = True
    result["reason"] = "rotated"
    return result


def rotate_all(config: dict, project_root: Path) -> list:
    """Rotate all files listed in runtime.log_rotation.files."""
    if not config:
        return []
    runtime_cfg = config.get("runtime") or {}
    rot_cfg = runtime_cfg.get("log_rotation") or {}
    if not rot_cfg.get("enabled", False):
        return []

    max_bytes = int(rot_cfg.get("max_bytes", 10 * 1024 * 1024))
    keep_files = int(rot_cfg.get("keep_files", 5))
    files = rot_cfg.get("files") or []

    out = []
    for f in files:
        p = _resolve(f, project_root)
        result = rotate_file(
            path=p, max_bytes=max_bytes, keep_files=keep_files,
            project_root=project_root,
        )
        out.append(result)
    return out
