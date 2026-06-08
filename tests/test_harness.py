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


class ProjectTemplateTest(unittest.TestCase):
    def test_project_template_files_exist(self) -> None:
        self.assertTrue((ROOT / "templates/project/PROJECT_GUIDE.md").is_file())
        self.assertTrue((ROOT / "templates/project/harness.config.json").is_file())

    def test_project_config_template_is_valid_json(self) -> None:
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

        self.assertIn("tdd_guard", config["policy"])
        self.assertIn("test_failure", config["policy"])

    def test_project_guide_template_has_required_sections(self) -> None:
        text = (ROOT / "templates/project/PROJECT_GUIDE.md").read_text(
            encoding="utf-8"
        )
        for heading in (
            "## 프로젝트 개요",
            "## 작업 전 확인",
            "## 프로젝트별 검증 명령",
            "## 수정 주의 경로",
            "## 프로젝트별 예외",
            "## 완료 보고 규칙",
        ):
            self.assertIn(heading, text)


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
