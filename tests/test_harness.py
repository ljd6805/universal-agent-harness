from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX_GUIDE = ".agent-harness/rules/CODEX.md"


class CodexHarnessStructureTest(unittest.TestCase):
    def test_codex_entrypoint_references_codex_guide(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(CODEX_GUIDE, text)
        self.assertIn("Codex", text)

    def test_codex_only_files_are_present(self) -> None:
        self.assertTrue((ROOT / CODEX_GUIDE).is_file())
        self.assertTrue((ROOT / ".agent-harness/adapters/codex/README.md").is_file())

    def test_non_codex_entrypoints_are_removed(self) -> None:
        for path in (
            "CLAUDE.md",
            "GEMINI.md",
            "opencode.json",
            ".claude/settings.json",
            ".agent-harness/adapters/claude/settings.json",
            ".agent-harness/adapters/gemini/README.md",
        ):
            self.assertFalse((ROOT / path).exists(), path)


class ActiveRulesDocTest(unittest.TestCase):
    def test_active_rules_declares_codex_only_scope(self) -> None:
        text = (ROOT / ".agent-harness/rules/ACTIVE_RULES.ko.md").read_text(
            encoding="utf-8"
        )
        match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
        self.assertIsNotNone(match)
        spec = match.group(1)
        self.assertIn("tool_scope: codex-only", spec)
        self.assertIn('entrypoint: "AGENTS.md"', spec)
        self.assertIn(f'guide: "{CODEX_GUIDE}"', spec)
        self.assertIn("native_auto_hook: false", spec)


class ProjectTemplateTest(unittest.TestCase):
    def test_project_config_template_is_valid(self) -> None:
        config = json.loads(
            (ROOT / "templates/project/harness.config.json").read_text(
                encoding="utf-8"
            )
        )
        for key in ("project", "commands", "paths", "policy"):
            self.assertIn(key, config)
        for key in ("build", "test", "lint", "typecheck"):
            self.assertIn(key, config["commands"])
        for key in ("source", "tests", "protected"):
            self.assertIn(key, config["paths"])

    def test_project_guide_template_mentions_codex(self) -> None:
        text = (ROOT / "templates/project/PROJECT_GUIDE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(CODEX_GUIDE, text)
        self.assertIn("## 완료 보고 규칙", text)


class HookSmokeTest(unittest.TestCase):
    def test_tdd_guard_warns_when_test_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            source = project / "widget.py"
            source.write_text("def widget():\n    return 1\n")
            payload = {"tool_input": {"file_path": str(source)}}
            result = subprocess.run(
                [sys.executable, str(ROOT / ".agent-harness/hooks/tdd_guard.py")],
                cwd=project,
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=True,
            )
        self.assertIn("[TDD warning]", result.stdout)

    def test_run_tests_uses_configured_test_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            harness_dir = project / ".agent-harness"
            harness_dir.mkdir()
            script = project / "custom_test.py"
            script.write_text("print('custom test ran')\n")
            config = {
                "commands": {"test": f"{sys.executable} custom_test.py"},
                "policy": {"test_failure": "warning"},
            }
            (harness_dir / "harness.config.json").write_text(json.dumps(config))
            payload = {"tool_input": {"file_path": str(project / "dummy.py")}}
            result = subprocess.run(
                [sys.executable, str(ROOT / ".agent-harness/hooks/run_tests.py")],
                cwd=project,
                input=json.dumps(payload),
                text=True,
                capture_output=True,
            )
        self.assertEqual(0, result.returncode)
        self.assertIn("custom test ran", result.stdout)


if __name__ == "__main__":
    unittest.main()
