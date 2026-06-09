# Codex 하네스 상세 가이드

이 문서는 `codex-dedicated-harness` branch의 목적, 구조, 적용 방식, 한계, 강화 방향을 설명합니다.

## 1. 왜 Codex 전용 branch인가

기존 `main`은 Codex, Claude, Gemini, OpenCode를 함께 고려하는 범용 base harness입니다. 그 구조는 공통 운영 원칙을 만들기에는 좋지만, 특정 도구 하나를 깊게 다루기 시작하면 책임이 흐려질 수 있습니다.

이 branch는 범용성을 내려놓고 Codex만 봅니다. 욕심을 줄여야 구조가 선명해집니다.

## 2. 핵심 철학

```text
Codex entrypoint는 AGENTS.md 하나로 고정한다.
실제 규칙 원본은 CODEX.md 하나로 유지한다.
자동 연결 여부는 사실대로 적는다.
```

## 3. 전체 구조

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

## 4. 파일별 역할

| 파일/디렉터리 | 역할 |
| --- | --- |
| `AGENTS.md` | Codex가 읽는 루트 entrypoint |
| `.agent-harness/rules/CODEX.md` | Codex 작업 규칙 원본 |
| `.agent-harness/rules/ACTIVE_RULES.ko.md` | 현재 Codex harness 상태 요약 |
| `.agent-harness/adapters/codex/` | Codex 전용 adapter 문서와 향후 설정 위치 |
| `.agent-harness/hooks/` | 포맷, 테스트, TDD 확인 script |
| `templates/project/` | 실제 프로젝트에 복사할 guide/config template |
| `tests/` | 하네스 구조와 hook 동작 검증 |

## 5. 제거한 구조

Codex 전용성을 지키기 위해 다음 구조를 제거합니다.

```text
CLAUDE.md
GEMINI.md
opencode.json
.claude/settings.json
.agent-harness/adapters/claude/
.agent-harness/adapters/gemini/
```

이 파일들이 남아 있으면 branch 이름은 Codex 전용인데 실제 구조는 범용이 됩니다. 이름표만 바꾸는 수준에서 끝내면 안 됩니다.

## 6. Codex 작업 흐름

Codex는 다음 순서로 작업해야 합니다.

1. `AGENTS.md`를 읽습니다.
2. `.agent-harness/rules/CODEX.md`를 읽습니다.
3. 프로젝트에 `.agent-harness/rules/PROJECT_GUIDE.md`가 있으면 함께 읽습니다.
4. 프로젝트에 `.agent-harness/harness.config.json`이 있으면 검증 명령과 보호 경로를 확인합니다.
5. 관련 파일과 테스트를 먼저 탐색합니다.
6. 작은 단위로 수정합니다.
7. 가능한 검증 명령을 실행합니다.
8. 변경 요약, 검증 결과, 남은 위험을 보고합니다.

## 7. Hook script의 위치와 한계

현재 유지하는 script는 다음과 같습니다.

| Script | 역할 |
| --- | --- |
| `format_changed_file.py` | 변경 파일 확장자에 따라 Prettier 또는 Black 실행 |
| `run_tests.py` | project config 또는 감지된 테스트 runner 실행 |
| `tdd_guard.py` | production file에 대응 test file이 있는지 확인 |

중요한 한계가 있습니다.

```text
이 script들은 현재 Codex에 native auto-hook으로 자동 연결되어 있다고 주장하지 않습니다.
```

따라서 현재는 Codex가 작업 완료 전 검증 단계에서 참고하거나, 향후 wrapper/hook 구조가 생겼을 때 연결할 수 있는 재사용 script로 봐야 합니다.

## 8. Project Harness Template

실제 프로젝트에 적용할 때는 `templates/project/`를 사용합니다.

```bash
cp -r .agent-harness /path/to/project/
cp templates/project/PROJECT_GUIDE.md /path/to/project/.agent-harness/rules/PROJECT_GUIDE.md
cp templates/project/harness.config.json /path/to/project/.agent-harness/harness.config.json
cp AGENTS.md /path/to/project/AGENTS.md
```

프로젝트별로 반드시 수정해야 할 파일은 다음입니다.

- `.agent-harness/rules/PROJECT_GUIDE.md`
- `.agent-harness/harness.config.json`

## 9. 하네스 자체 테스트

```bash
python3 -m unittest discover -s tests
```

테스트는 다음을 확인합니다.

- Codex entrypoint가 올바른 guide를 가리키는지
- Codex 외 도구 entrypoint가 제거되었는지
- Codex adapter 문서가 존재하는지
- active rules 문서가 Codex 전용 상태를 반영하는지
- project template이 기본 section을 유지하는지
- hook script가 기본 동작을 유지하는지

## 10. 현재 한계

1. Codex native auto-hook은 아직 연결하지 않았습니다.
2. hook 결과를 파일로 저장하지 않습니다.
3. `run_tests.py`의 test runner 감지는 아직 단순합니다.
4. `tdd_guard.py`는 테스트 파일 존재 여부만 확인하고 테스트 품질은 판단하지 않습니다.
5. 보안 정책은 아직 최소 수준입니다.

## 11. 추천 강화 순서

1. Codex 완료 보고 format을 더 엄격히 정의합니다.
2. `harness.config.json` 기반 검증 runner를 build/lint/typecheck까지 확장합니다.
3. hook 실행 결과를 `.agent-harness/logs/`에 저장합니다.
4. 민감 경로와 secret 출력 방지 guard를 추가합니다.
5. Codex native hook 또는 wrapper 방식이 확정되면 `.agent-harness/adapters/codex/`에 반영합니다.

## 12. 빠른 확인 명령

```bash
find . -maxdepth 4 -type f | sort
```

```bash
python3 -m py_compile .agent-harness/hooks/*.py tests/test_harness.py
```

```bash
python3 -m unittest discover -s tests
```
