# Codex 전용 에이전트 하네스

이 branch는 `universal-agent-harness`의 `main`에서 분기한 **Codex 전용 결과물 branch**입니다.

기존 main branch가 Codex, Claude, Gemini, OpenCode를 함께 고려하는 범용 base harness라면, 이 branch는 Codex가 프로젝트 안에서 어떻게 탐색하고, 수정하고, 검증하고, 보고해야 하는지만 다룹니다.

## 이 branch의 목적

Codex 전용 harness의 목표는 다음과 같습니다.

- Codex가 읽는 진입점을 `AGENTS.md` 하나로 고정한다.
- Codex 작업 규칙의 원본을 `.agent-harness/rules/CODEX_GUIDE.md`로 분리한다.
- Claude, Gemini, OpenCode 전용 entrypoint와 adapter를 제거해 구조를 단순화한다.
- 프로젝트별 검증 명령과 보호 경로는 `.agent-harness/harness.config.json`으로 관리한다.
- Codex가 완료 보고 전에 실행해야 할 검증 흐름을 문서와 테스트로 확인 가능하게 만든다.

## Codex Harness와 Project Harness

이 branch는 Codex를 위한 base harness입니다. 실제 프로젝트에 적용할 때는 이 구조를 복사한 뒤 프로젝트별 guide와 config를 채웁니다.

| 구분 | 위치 | 역할 |
| --- | --- | --- |
| Codex Base Harness | 이 branch | Codex 공통 작업 규칙, hook script, adapter 문서, template |
| Project Harness | 각 프로젝트의 `.agent-harness/` | 프로젝트별 지침, 실행 명령, 보호 경로, 예외 정책 |
| Codex Entry Point | `AGENTS.md` | Codex가 가장 먼저 읽는 루트 지침 |
| Codex Guide | `.agent-harness/rules/CODEX_GUIDE.md` | Codex가 따라야 하는 작업 규칙 원문 |
| Project Guide | `.agent-harness/rules/PROJECT_GUIDE.md` | 프로젝트별 자연어 지침 |
| Project Config | `.agent-harness/harness.config.json` | build/test/lint/typecheck, path, policy 설정 |

핵심은 간단합니다.

```text
AGENTS.md는 Codex용 얇은 입구입니다.
CODEX_GUIDE.md는 Codex 작업 규칙의 실제 원본입니다.
PROJECT_GUIDE.md와 harness.config.json은 프로젝트별 현실을 담습니다.
```

## 먼저 읽을 문서

- **Codex가 실제로 따라야 할 규칙** → [.agent-harness/rules/CODEX_GUIDE.md](.agent-harness/rules/CODEX_GUIDE.md)
- **현재 켜져 있거나 문서화된 규칙 요약** → [.agent-harness/rules/ACTIVE_RULES.ko.md](.agent-harness/rules/ACTIVE_RULES.ko.md)
- **왜 Codex 전용 구조로 분기했는지** → [Codex 하네스 상세 가이드](docs/CODEX_HARNESS_GUIDE.ko.md)

## 저장소 구조

```text
.
├── AGENTS.md
├── README.md
├── .agent-harness/
│   ├── adapters/
│   │   └── codex/
│   │       └── README.md
│   ├── hooks/
│   │   ├── format_changed_file.py
│   │   ├── run_tests.py
│   │   └── tdd_guard.py
│   └── rules/
│       ├── ACTIVE_RULES.ko.md
│       └── CODEX_GUIDE.md
├── docs/
│   └── CODEX_HARNESS_GUIDE.ko.md
├── templates/
│   └── project/
│       ├── PROJECT_GUIDE.md
│       └── harness.config.json
└── tests/
    └── test_harness.py
```

## Codex 전용으로 제거한 것

이 branch에서는 Codex 외 도구의 entrypoint와 adapter를 제거합니다.

| 제거 대상 | 이유 |
| --- | --- |
| `CLAUDE.md` | Claude Code native import용 entrypoint이므로 제외 |
| `GEMINI.md` | Gemini CLI용 entrypoint이므로 제외 |
| `opencode.json` | OpenCode runtime config이므로 제외 |
| `.claude/settings.json` | Claude Code hook 설정이므로 제외 |
| `.agent-harness/adapters/claude/` | Claude adapter이므로 제외 |
| `.agent-harness/adapters/gemini/` | Gemini adapter이므로 제외 |

무리하게 다 품으려고 하면 구조가 다시 흐려집니다. 이 branch의 답은 단순합니다. **Codex만 본다.**

## 현재 자동화 범위

Codex는 `AGENTS.md`를 읽는 entrypoint를 갖지만, 이 branch는 Codex에 대해 Claude Code의 `.claude/settings.json` 같은 native hook 설정이 있다고 주장하지 않습니다.

대신 다음 script를 Codex가 검증 단계에서 사용할 수 있는 공통 도구로 유지합니다.

1. `.agent-harness/hooks/format_changed_file.py`
2. `.agent-harness/hooks/run_tests.py`
3. `.agent-harness/hooks/tdd_guard.py`

즉 현재 상태는 다음과 같습니다.

```text
Codex instruction: AGENTS.md -> CODEX_GUIDE.md
Verification scripts: .agent-harness/hooks/*.py
Native auto-hook: not claimed
```

이 구분이 중요합니다. 없는 자동화를 있다고 적으면 그건 문서가 아니라 뻥카입니다.

## Project Harness Template

프로젝트별 지침과 실행 설정 template은 다음 위치에 있습니다.

```text
templates/project/
├── PROJECT_GUIDE.md
└── harness.config.json
```

프로젝트에 적용할 때는 다음처럼 복사합니다.

```bash
cp -r .agent-harness /path/to/project/
cp templates/project/PROJECT_GUIDE.md /path/to/project/.agent-harness/rules/PROJECT_GUIDE.md
cp templates/project/harness.config.json /path/to/project/.agent-harness/harness.config.json
cp AGENTS.md /path/to/project/AGENTS.md
```

그 다음 프로젝트 상황에 맞게 아래 파일을 수정합니다.

- `.agent-harness/rules/PROJECT_GUIDE.md`
- `.agent-harness/harness.config.json`

## 검증 방법

하네스 자체 테스트는 다음 명령으로 실행합니다.

```bash
python3 -m unittest discover -s tests
```

현재 테스트는 다음을 확인합니다.

- `AGENTS.md`가 Codex guide를 참조하는지
- Claude/Gemini/OpenCode entrypoint가 제거되었는지
- Codex adapter 문서가 존재하는지
- `ACTIVE_RULES.ko.md`가 Codex 전용 상태를 설명하는지
- project harness template 파일이 존재하고 기본 section을 포함하는지
- TDD guard와 test runner hook이 기본 동작을 유지하는지

## 강화 로드맵

1. Codex 작업 결과 요약 format을 더 엄격히 정의합니다.
2. `harness.config.json` 기반으로 build/lint/typecheck runner를 확장합니다.
3. hook 실행 결과를 `.agent-harness/logs/`에 저장하는 관측성을 추가합니다.
4. 민감 경로와 destructive command에 대한 guard를 추가합니다.
5. Codex가 안정적인 project-level hook 방식을 제공하면 adapter에 반영합니다.
