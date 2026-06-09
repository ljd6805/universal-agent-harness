# Codex 전용 에이전트 하네스

이 branch는 `universal-agent-harness`의 `main`에서 분기한 **Codex 전용 결과물 branch**입니다.

기존 main branch는 Codex, Claude, Gemini, OpenCode를 함께 고려하는 범용 base harness입니다. 이 branch는 Codex만 대상으로 하며, Codex가 프로젝트 안에서 어떻게 탐색하고, 수정하고, 검증하고, 보고해야 하는지에 집중합니다.

## 핵심 구조

```text
AGENTS.md -> .agent-harness/rules/CODEX.md
```

| 구분 | 위치 | 역할 |
| --- | --- | --- |
| Codex Entry Point | `AGENTS.md` | Codex가 가장 먼저 읽는 루트 지침 |
| Codex Guide | `.agent-harness/rules/CODEX.md` | Codex 작업 규칙 원본 |
| Active Rules | `.agent-harness/rules/ACTIVE_RULES.ko.md` | 현재 적용 상태 요약 |
| Codex Adapter | `.agent-harness/adapters/codex/` | Codex 관련 adapter 문서 |
| Hooks | `.agent-harness/hooks/` | 검증에 사용할 재사용 script |
| Project Template | `templates/project/` | 실제 프로젝트에 복사할 guide/config template |

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
│       └── CODEX.md
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

이 branch에서는 다음 도구별 entrypoint와 adapter를 제거합니다.

- `CLAUDE.md`
- `GEMINI.md`
- `opencode.json`
- `.claude/settings.json`
- `.agent-harness/adapters/claude/`
- `.agent-harness/adapters/gemini/`

## 현재 자동화 범위

Codex는 `AGENTS.md`를 읽는 entrypoint를 갖습니다. 다만 이 branch는 Codex에 native auto-hook이 연결되어 있다고 주장하지 않습니다.

다음 script는 검증 단계에서 재사용할 수 있도록 유지합니다.

- `.agent-harness/hooks/format_changed_file.py`
- `.agent-harness/hooks/run_tests.py`
- `.agent-harness/hooks/tdd_guard.py`

## Project Harness Template

```bash
cp -r .agent-harness /path/to/project/
cp templates/project/PROJECT_GUIDE.md /path/to/project/.agent-harness/rules/PROJECT_GUIDE.md
cp templates/project/harness.config.json /path/to/project/.agent-harness/harness.config.json
cp AGENTS.md /path/to/project/AGENTS.md
```

## 검증 방법

```bash
python3 -m unittest discover -s tests
```
