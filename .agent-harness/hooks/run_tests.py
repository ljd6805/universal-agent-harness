#!/usr/bin/env python3
"""Run the project's available test command after a file change."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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


def has_python_tests(project: Path) -> bool:
    ignored = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    for path in project.rglob("*.py"):
        if any(part in ignored for part in path.parts):
            continue
        name = path.name
        if name.startswith("test_") or name.endswith("_test.py"):
            return True
    return False


def run(command: list[str], cwd: Path) -> None:
    try:
        subprocess.run(command, cwd=cwd, check=False)
    except FileNotFoundError:
        return


def main() -> int:
    path = changed_file()
    project = Path.cwd().resolve()
    if path:
        try:
            path.relative_to(project)
        except ValueError:
            return 0

    if (project / "package.json").is_file():
        run(["npm", "test", "--if-present"], project)
    elif has_python_tests(project):
        run([sys.executable, "-m", "pytest"], project)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
