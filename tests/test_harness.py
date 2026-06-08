from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HarnessStructureTest(unittest.TestCase):
    def test_native_import_entry_points_reference_the_shared_guide(self) -> None:
        guide = ".agent-harness/rules/AGENT_GUIDE.md"
        for name in ("CLAUDE.md", "GEMINI.md"):
            path = ROOT / name
            self.assertFalse(path.is_symlink(), name)
            self.assertIn(f"@{guide}", path.read_text(encoding="utf-8"))

    def test_prompt_based_entry_point_references_the_shared_guide(self) -> None:
        guide = ".agent-harness/rules/AGENT_GUIDE.md"
        path = ROOT / "AGENTS.md"
        self.assertFalse(path.is_symlink())
        self.assertIn(guide, path.read_text(encoding="utf-8"))

    def test_opencode_instructions_reference_the_shared_guide(self) -> None:
        config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        self.assertIn(".agent-harness/rules/AGENT_GUIDE.md", config["instructions"])

    def test_claude_settings_matches_shared_adapter(self) -> None:
        path = ROOT / ".claude/settings.json"
        self.assertFalse(path.is_symlink())
        adapter_path = ROOT / ".agent-harness/adapters/claude/settings.json"
        self.assertEqual(
            json.loads(path.read_text(encoding="utf-8")),
            json.loads(adapter_path.read_text(encoding="utf-8")),
        )

    def test_claude_adapter_is_valid_json(self) -> None:
        settings = json.loads(
            (ROOT / ".agent-harness/adapters/claude/settings.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("permissions", settings)
        self.assertIn("hooks", settings)


class TddGuardTest(unittest.TestCase):
    def test_warns_when_production_file_has_no_matching_test(self) -> None:
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

    def test_skips_when_matching_test_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            source = project / "widget.py"
            source.write_text("def widget():\n    return 1\n")
            (project / "test_widget.py").write_text("def test_widget():\n    pass\n")

            payload = {"tool_input": {"file_path": str(source)}}
            result = subprocess.run(
                [sys.executable, str(ROOT / ".agent-harness/hooks/tdd_guard.py")],
                cwd=project,
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertEqual("", result.stdout)


if __name__ == "__main__":
    unittest.main()
