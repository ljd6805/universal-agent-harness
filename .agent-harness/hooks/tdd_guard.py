#!/usr/bin/env python3
"""Warn agents when production code has no nearby matching test file."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PRODUCTION_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}
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


def matching_test_exists(project: Path, path: Path) -> bool:
    names = matching_test_names(path)
    for candidate in project.rglob("*"):
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

    if not matching_test_exists(project, path):
        emit_warning(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
