# 현재 적용된 규칙 (Codex Active Rules)

이 문서는 Codex 전용 harness에 현재 문서화되어 있는 entrypoint, workflow rule, 검증 script를 한눈에 확인하기 위한 레퍼런스입니다.

> 이 branch는 Codex 전용입니다. Claude, Gemini, OpenCode entrypoint와 adapter는 의도적으로 제거합니다.
>
> 현재 Codex에 대해 native auto-hook 설정이 연결되어 있다고 주장하지 않습니다. hook script는 검증 단계에서 재사용 가능한 script로 유지합니다.

## 스펙 (기계가 읽는 부분)

```yaml
version: 1
tool_scope: codex-only

codex:
  entrypoint: "AGENTS.md"
  guide: ".agent-harness/rules/CODEX.md"
  native_auto_hook: false

removed_entrypoints:
  - "CLAUDE.md"
  - "GEMINI.md"
  - "opencode.json"
  - ".claude/settings.json"

adapters:
  keep:
    - ".agent-harness/adapters/codex/README.md"
  removed:
    - ".agent-harness/adapters/claude/settings.json"
    - ".agent-harness/adapters/gemini/README.md"

verification_scripts:
  - script: ".agent-harness/hooks/format_changed_file.py"
    purpose: "변경된 파일을 formatter가 있을 때 포맷한다"
  - script: ".agent-harness/hooks/run_tests.py"
    purpose: "프로젝트 설정 또는 감지된 테스트를 실행한다"
  - script: ".agent-harness/hooks/tdd_guard.py"
    purpose: "프로덕션 코드 변경에 대응하는 테스트가 있는지 확인한다"

workflow_rules:
  - id: explore-before-edit
    summary: "수정 전에 관련 파일과 git 상태를 확인하고 기존 사용자 변경을 보존한다"
    source: ".agent-harness/rules/CODEX.md#1-수정-전-먼저-탐색한다"
  - id: check-project-guide
    summary: "PROJECT_GUIDE.md / harness.config.json이 있으면 Codex guide와 함께 따른다"
    source: ".agent-harness/rules/CODEX.md#2-프로젝트별-지침을-확인한다"
  - id: tdd-default
    summary: "프로덕션 코드는 실패하는 테스트 작성 후 구현을 기본값으로 한다"
    source: ".agent-harness/rules/CODEX.md#3-기본값은-tdd다"
  - id: small-scope
    summary: "Codex 작업은 작고 검증 가능한 단위로 유지한다"
    source: ".agent-harness/rules/CODEX.md#4-codex-작업-범위를-작게-유지한다"
  - id: verify-before-done
    summary: "완료 보고 전 관련 테스트나 검증을 실행한다"
    source: ".agent-harness/rules/CODEX.md#5-완료-전-검증한다"
  - id: evidence-based-report
    summary: "변경 요약, 검증 명령, 결과, 남은 위험을 증거 중심으로 보고한다"
    source: ".agent-harness/rules/CODEX.md#6-보고는-증거-중심으로-한다"
  - id: codex-only-structure
    summary: "Codex 외 도구 전용 entrypoint와 adapter를 다시 추가하지 않는다"
    source: ".agent-harness/rules/CODEX.md#7-codex-전용-구조를-유지한다"
```

## 설명

### Entry point

Codex가 읽는 루트 파일은 `AGENTS.md` 하나입니다. `AGENTS.md`는 실제 규칙 원본인 `.agent-harness/rules/CODEX.md`를 읽도록 안내합니다.

### Removed tool-specific files

이 branch는 Codex 전용 결과물이므로 다음 파일은 없어야 합니다.

- `CLAUDE.md`
- `GEMINI.md`
- `opencode.json`
- `.claude/settings.json`
- `.agent-harness/adapters/claude/settings.json`
- `.agent-harness/adapters/gemini/README.md`

### Verification scripts

`.agent-harness/hooks/` 아래 script는 Codex가 검증 단계에서 사용할 수 있는 재사용 가능한 도구입니다. 다만 현재 이 script들이 Codex에 native auto-hook으로 자동 연결되어 있다고 주장하지 않습니다.

### 갱신 절차

1. `CODEX.md`, `AGENTS.md`, adapter, hook script 중 필요한 파일을 수정합니다.
2. 이 문서의 YAML spec을 함께 수정합니다.
3. `python3 -m unittest discover -s tests`를 실행합니다.
