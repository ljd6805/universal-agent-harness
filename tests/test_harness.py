from __future__ import annotations

import json
import re
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


def _hook_scripts(settings: dict) -> set[str]:
    scripts: set[str] = set()
    for entries in settings.get("hooks", {}).values():
        for entry in entries:
            for hook in entry.get("hooks", []):
                match = re.search(r"(\.agent-harness/hooks/\S+\.py)", hook.get("command", ""))
                if match:
                    scripts.add(match.group(1))
    return scripts


class ActiveRulesDocTest(unittest.TestCase):
    """ACTIVE_RULES.ko.md의 YAML 스펙 블록이 .claude/settings.json과 어긋나지 않는지 확인한다.

    PyYAML 같은 추가 의존성 없이, 스펙 블록 텍스트에서 `rule:`/`script:` 값을
    추출해 실제 설정과 양방향(빠짐 없음 + stale 항목 없음)으로 비교한다.
    """

    @classmethod
    def setUpClass(cls) -> None:
        doc_text = (ROOT / ".agent-harness/rules/ACTIVE_RULES.ko.md").read_text(
            encoding="utf-8"
        )
        match = re.search(r"```yaml\n(.*?)\n```", doc_text, re.DOTALL)
        assert match is not None, "ACTIVE_RULES.ko.md must contain a fenced ```yaml spec block"
        cls.spec_text = match.group(1)
        cls.settings = json.loads(
            (ROOT / ".claude/settings.json").read_text(encoding="utf-8")
        )

    def test_every_permission_rule_in_settings_is_documented(self) -> None:
        for rule in self.settings["permissions"]["allow"]:
            self.assertIn(
                f'"{rule}"',
                self.spec_text,
                f"permission rule {rule!r} is missing from ACTIVE_RULES.ko.md",
            )

    def test_no_documented_permission_rule_is_stale(self) -> None:
        documented = re.findall(r'rule: "([^"]+)"', self.spec_text)
        actual = self.settings["permissions"]["allow"]
        for rule in documented:
            self.assertIn(
                rule,
                actual,
                f"ACTIVE_RULES.ko.md documents permission {rule!r} that is not in .claude/settings.json",
            )

    def test_every_hook_script_in_settings_is_documented(self) -> None:
        for script in _hook_scripts(self.settings):
            self.assertIn(
                script,
                self.spec_text,
                f"hook script {script!r} is missing from ACTIVE_RULES.ko.md",
            )

    def test_no_documented_hook_script_is_stale(self) -> None:
        documented = set(re.findall(r'script: "([^"]+)"', self.spec_text))
        actual = _hook_scripts(self.settings)
        for script in documented:
            self.assertIn(
                script,
                actual,
                f"ACTIVE_RULES.ko.md documents hook script {script!r} that is not wired up in .claude/settings.json",
            )


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
