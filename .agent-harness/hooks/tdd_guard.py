#!/usr/bin/env python3
"""Warn agents when production code has no nearby matching test file."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PRODUCTION_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".c", ".cpp", ".h"}
IGNORED_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def changed_file() -> Path | None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return None

    tool_input = payload.get("tool_input", {})
    value = tool_input.get("file_path") or tool_input.get("path")
    if not value:
        return None
    return Path(value).expanduser().resolve()


def load_config(project: Path) -> dict:
    config_path = project / ".agent-harness" / "harness.config.json"
    if config_path.is_file():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def is_test_file(path: Path) -> bool:
    name = path.name.lower()
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or ".test." in name
        or ".spec." in name
    )


def matching_test_names(path: Path) -> set[str]:
    stem = path.stem
    ext = path.suffix
    return {
        f"test_{stem}{ext}",
        f"{stem}_test{ext}",
        f"{stem}.test{ext}",
        f"{stem}.spec{ext}",
    }


def search_roots(project: Path, config: dict) -> list[Path]:
    """Return directories to search for test files.

    If paths.tests is configured (B), restrict search to those directories only.
    Otherwise fall back to the entire project (A).
    """
    test_paths = config.get("paths", {}).get("tests", [])
    if not test_paths:
        return [project]
    # paths.tests가 지정된 경우 존재하는 디렉터리만 반환 (없으면 빈 리스트 → 테스트 미발견)
    return [(project / p).resolve() for p in test_paths if (project / p).is_dir()]


def matching_test_exists(project: Path, path: Path, config: dict) -> bool:
    names = matching_test_names(path)
    for root in search_roots(project, config):
        for candidate in root.rglob("*"):
            if not candidate.is_file():
                continue
            if any(part in IGNORED_PARTS for part in candidate.parts):
                continue
            if candidate.name in names:
                return True
    return False


def emit_warning(path: Path) -> None:
    message = (
        f'[TDD warning] "{path.name}" has no matching test file. '
        "Write or update a failing test before production implementation, "
        "unless this change is an approved exception."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": message,
                }
            }
        )
    )


def main() -> int:
    path = changed_file()
    if not path:
        return 0

    project = Path.cwd().resolve()
    try:
        path.relative_to(project)
    except ValueError:
        return 0

    if path.suffix.lower() not in PRODUCTION_EXTENSIONS or is_test_file(path):
        return 0

    config = load_config(project)
    policy = config.get("policy", {})
    is_strict = policy.get("tdd_guard", "warning") == "strict"

    if not matching_test_exists(project, path, config):
        emit_warning(path)
        if is_strict:
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
