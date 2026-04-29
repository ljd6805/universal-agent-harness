#!/usr/bin/env python3
"""Format the file changed by an agent tool call when a formatter exists."""

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
    tool_response = payload.get("tool_response", {})
    value = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_response.get("filePath")
        or tool_response.get("file_path")
    )
    if not value:
        return None
    return Path(value).expanduser().resolve()


def run(command: list[str], cwd: Path) -> None:
    try:
        subprocess.run(command, cwd=cwd, capture_output=True, check=False)
    except FileNotFoundError:
        return


def main() -> int:
    path = changed_file()
    if not path or not path.exists() or not path.is_file():
        return 0

    project = Path.cwd().resolve()
    try:
        path.relative_to(project)
    except ValueError:
        return 0

    ext = path.suffix.lower()
    if ext in {".js", ".ts", ".jsx", ".tsx", ".json", ".css", ".html", ".md"}:
        run(["npx", "--yes", "prettier", "--write", str(path)], project)
    elif ext == ".py":
        run([sys.executable, "-m", "black", str(path)], project)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
