#!/usr/bin/env python3
"""Run the project's available test command after a file change."""

from __future__ import annotations

import json
import shlex
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


def load_config(project: Path) -> dict:
    config_path = project / ".agent-harness" / "harness.config.json"
    if config_path.is_file():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def has_python_tests(project: Path) -> bool:
    ignored = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    for path in project.rglob("*.py"):
        if any(part in ignored for part in path.parts):
            continue
        name = path.name
        if name.startswith("test_") or name.endswith("_test.py"):
            return True
    return False


def run(command: list[str], cwd: Path, missing_ok: bool = True) -> int:
    try:
        result = subprocess.run(command, cwd=cwd, check=False)
        return result.returncode
    except FileNotFoundError:
        # missing_ok=False: 명시적 config command — 실행 파일 없음을 실패로 처리
        return 0 if missing_ok else 127


def main() -> int:
    path = changed_file()
    project = Path.cwd().resolve()
    if path:
        try:
            path.relative_to(project)
        except ValueError:
            return 0

    config = load_config(project)
    policy = config.get("policy", {})
    is_strict = policy.get("test_failure", "warning") == "strict"

    # config에 test 명령이 있으면 그것만 실행
    config_test_cmd = config.get("commands", {}).get("test", "").strip()
    if config_test_cmd:
        rc = run(shlex.split(config_test_cmd), project, missing_ok=False)
        if rc != 0 and is_strict:
            return 2
        return 0

    # 언어별 테스트 러너를 모두 감지하여 순서대로 실행
    failed = False

    if (project / "package.json").is_file():
        rc = run(["npm", "test", "--if-present"], project)
        if rc != 0:
            failed = True

    if has_python_tests(project):
        rc = run([sys.executable, "-m", "pytest"], project)
        if rc != 0:
            failed = True

    if failed and is_strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
