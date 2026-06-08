# 범용 에이전트 하네스

이 저장소는 Codex, Claude, Gemini, OpenCode 같은 AI 코딩 에이전트를 공통 규칙으로 관리하기 위한 팀 공통 base harness입니다.

애플리케이션 코드가 아니라, 에이전트가 프로젝트 안에서 어떻게 탐색하고, 수정하고, 검증하고, 보고해야 하는지를 정리하는 운영 기반입니다.

## 이 저장소의 목적

이 하네스의 목표는 에이전트 작업을 다음 상태로 만드는 것입니다.

- 여러 도구에서 일관되게 동작한다.
- 현재 설정과 규칙을 쉽게 확인할 수 있다.
- 시간이 지나며 안전하게 강화할 수 있다.
- 다른 저장소에 복사하거나 이식하기 쉽다.
- 프로젝트별 규칙과 실행 설정을 base harness와 분리해 관리할 수 있다.
- 하네스 자체도 테스트로 검증할 수 있다.

## Base Harness와 Project Harness

이 저장소는 개별 프로젝트 전용 harness가 아니라, 여러 프로젝트에 공통 적용하기 위한 base harness입니다.

Base harness는 모든 프로젝트가 공유할 원칙과 기본 장비를 제공합니다.

- 공통 agent 작업 규칙
- 공통 hook 스크립트
- Codex, Claude, Gemini, OpenCode 같은 도구별 adapter 기본 구조
- 프로젝트에 적용하기 위한 template

각 실제 프로젝트는 이 base harness를 복사하거나 적용한 뒤, 프로젝트별 지침과 실행 설정을 추가합니다. 이 적용본을 project harness라고 부릅니다.

| 구분 | 위치 | 역할 |
| --- | --- | --- |
| Base Harness | `universal-agent-harness` 저장소 | 팀 공통 규칙, 공통 hook, adapter 기본값 |
| Project Harness | 각 프로젝트의 `.agent-harness/` | 프로젝트별 규칙, 실행 명령, 보호 경로, 예외 정책 |
| Project Guide | `.agent-harness/rules/PROJECT_GUIDE.md` | agent가 읽는 프로젝트별 자연어 지침 |
| Project Config | `.agent-harness/harness.config.json` | hook이나 agent가 참고할 프로젝트별 실행 설정 |

핵심은 간단합니다.

```text
Base harness는 “어떻게 일해야 하는가”를 정의합니다.
Project harness는 “이 프로젝트에서는 어떻게 검증해야 하는가”를 정의합니다.
```

## 먼저 읽을 문서

목적에 따라 읽어야 할 문서가 다릅니다.

- **지금 이 하네스에 어떤 permission, hook, 작업 규칙이 켜져 있는지 빠르게 확인하고 싶다면** → [현재 적용된 규칙](.agent-harness/rules/ACTIVE_RULES.ko.md)
- **왜 이런 구조와 규칙을 선택했는지, 한계와 강화 방향이 궁금하다면** → [범용 에이전트 하네스 상세 가이드](docs/HARNESS_GUIDE.ko.md)

"현재 적용된 규칙" 문서는 실제 설정 파일(`.claude/settings.json`, `AGENT_GUIDE.md` 등)의 거울이며, `tests/test_harness.py`로 동기화가 검증됩니다. 설정을 바꿀 때는 이 문서도 함께 갱신해야 합니다.

상세 가이드에서는 다음 내용을 설명합니다.

- 하네스가 무엇인지
- 왜 현재 구조를 선택했는지
- 각 파일과 디렉터리가 어떤 역할을 하는지
- Codex, Claude, Gemini, OpenCode에 각각 어떤 범위까지 적용되는지
- 공통 hook이 어떻게 동작하는지
- 현재 공통 hook, 도구별 적용 범위, 한계가 무엇인지
- 앞으로 어떤 순서로 강화하면 좋은지

## 저장소 구조

```text
.
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── opencode.json
├── .claude/
│   └── settings.json
├── .agent-harness/
│   ├── adapters/
│   │   ├── claude/settings.json
│   │   ├── codex/README.md
│   │   └── gemini/README.md
│   ├── hooks/
│   │   ├── format_changed_file.py
│   │   ├── run_tests.py
│   │   └── tdd_guard.py
│   └── rules/
│       ├── AGENT_GUIDE.md
│       └── ACTIVE_RULES.ko.md
├── templates/
│   └── project/
│       ├── PROJECT_GUIDE.md
│       └── harness.config.json
└── tests/
    └── test_harness.py
```

## 설계 원칙

루트의 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `opencode.json`은 각 도구가 읽는 진입점입니다. 이 파일들은 작고 안정적으로 유지하고, 실제 공통 규칙은 `.agent-harness/` 아래에 둡니다.

실제 원본은 다음 위치에 있습니다.

- `.agent-harness/rules/`: 모든 에이전트가 공유하는 작업 규칙
- `.agent-harness/hooks/`: 포맷, 테스트, TDD 확인 같은 공통 자동화 스크립트
- `.agent-harness/adapters/`: 도구별 설정
- `templates/project/`: 프로젝트별 지침과 실행 설정을 시작하기 위한 template

이 구조를 쓰면 Codex, Claude, Gemini, OpenCode의 지침이 서로 다르게 갈라지는 일을 줄일 수 있습니다.

## 에이전트 진입점

각 도구는 서로 다른 방식으로 공통 가이드를 참조합니다.

| 도구 | 진입점 | 방식 |
| --- | --- | --- |
| Codex | `AGENTS.md` | 공통 가이드를 읽고 따르라는 안내 주석 |
| Claude Code | `CLAUDE.md` | `@.agent-harness/rules/AGENT_GUIDE.md` native import |
| Gemini CLI | `GEMINI.md` | `@.agent-harness/rules/AGENT_GUIDE.md` native import |
| OpenCode | `opencode.json` | `instructions` 필드로 공통 가이드 지정 |

공통 가이드의 실제 원본은 항상 다음 파일입니다.

```text
.agent-harness/rules/AGENT_GUIDE.md
```

## 현재 자동화

현재 가장 강하게 연결된 도구는 Claude Code입니다. Claude Code는 `.claude/settings.json`을 읽고, 이 파일은 Claude 어댑터 설정과 같은 내용을 가집니다.

```text
.agent-harness/adapters/claude/settings.json
```

Claude 어댑터는 파일 수정 이후 다음 공통 훅 스크립트를 실행합니다.

1. `format_changed_file.py`: Prettier 또는 Black이 있으면 변경 파일을 포맷합니다.
2. `run_tests.py`: 감지 가능한 테스트 명령을 실행합니다.
3. `tdd_guard.py`: 프로덕션 코드에 대응 테스트가 없으면 경고합니다.

Codex와 Gemini 어댑터는 현재 문서화된 기본 자리만 마련되어 있습니다. 공통 규칙은 이미 `AGENTS.md`, `GEMINI.md`, `opencode.json`을 통해 적용되며, 각 도구가 안정적인 프로젝트 훅이나 설정 방식을 제공할 때 `.agent-harness/adapters/` 아래에 추가하면 됩니다.

## Project Harness Template

프로젝트별 지침과 실행 설정을 쉽게 시작할 수 있도록 template을 제공합니다.

```text
templates/project/
├── PROJECT_GUIDE.md
└── harness.config.json
```

각 프로젝트에 적용할 때는 다음 위치로 복사해서 사용합니다.

```text
templates/project/PROJECT_GUIDE.md
-> .agent-harness/rules/PROJECT_GUIDE.md

templates/project/harness.config.json
-> .agent-harness/harness.config.json
```

`PROJECT_GUIDE.md`는 agent가 읽는 프로젝트별 자연어 지침입니다. 프로젝트 개요, 검증 명령, 수정 주의 경로, 완료 보고 규칙처럼 사람이 읽고 조정할 내용을 담습니다.

`harness.config.json`은 프로젝트별 실행 설정입니다. build, test, lint, typecheck 명령과 source/test/protected path, TDD guard 정책 같은 값을 담습니다.

## 다른 프로젝트에 적용하기

이 하네스는 symlink 대신 각 도구의 native import 또는 그에 준하는 방식을 사용합니다. symlink는 Windows 등 일부 환경에서 잘 동작하지 않으므로, 실제 파일에 공통 가이드를 가리키는 내용을 직접 적어 둡니다.

### 1. base harness 복사

```bash
cp -r .agent-harness /path/to/project/
mkdir -p /path/to/project/.claude
```

### 2. project harness template 복사

```bash
cp templates/project/PROJECT_GUIDE.md /path/to/project/.agent-harness/rules/PROJECT_GUIDE.md
cp templates/project/harness.config.json /path/to/project/.agent-harness/harness.config.json
```

### 3. 도구별 진입점 생성

- `CLAUDE.md`, `GEMINI.md`: Claude Code와 Gemini CLI는 `@경로` import 문법을 지원하므로 `@.agent-harness/rules/AGENT_GUIDE.md` 한 줄을 작성합니다.
- `AGENTS.md`: Codex/OpenCode는 일반적으로 native import가 없으므로, 공통 가이드 파일을 읽고 따르라는 안내 주석을 작성합니다.
- `opencode.json`: OpenCode는 `instructions` 필드로 규칙 파일을 직접 지정할 수 있습니다.
- `.claude/settings.json`: `.agent-harness/adapters/claude/settings.json`의 내용을 그대로 복사해 둡니다.

### 4. 프로젝트별 내용 수정

적용한 프로젝트에서는 다음 파일을 프로젝트 상황에 맞게 수정합니다.

- `.agent-harness/rules/PROJECT_GUIDE.md`
- `.agent-harness/harness.config.json`

예를 들어 프로젝트별 build/test/lint 명령, source/test 경로, 수정 금지 경로, legacy 예외 정책은 base harness가 아니라 project harness에서 관리합니다.

## 검증 방법

하네스 자체 테스트는 다음 명령으로 실행합니다.

```bash
python3 -m unittest discover -s tests
```

현재 테스트는 다음을 확인합니다.

- `CLAUDE.md`, `GEMINI.md`가 symlink가 아니며 공통 가이드를 native import로 참조하는지
- `AGENTS.md`가 symlink가 아니며 공통 가이드 경로를 안내하는지
- `opencode.json`의 `instructions`가 공통 가이드를 참조하는지
- `.claude/settings.json`이 symlink가 아니며 공유 Claude adapter 설정과 일치하는지
- Claude adapter JSON이 유효하고 `permissions`, `hooks`를 포함하는지
- project harness template 파일이 존재하는지
- `templates/project/harness.config.json`이 유효한 JSON이고 기본 section을 포함하는지
- `templates/project/PROJECT_GUIDE.md`가 기본 section을 포함하는지
- TDD guard가 테스트 없는 production 파일에 경고하는지
- 대응 테스트가 있을 때 TDD guard가 경고하지 않는지
- `ACTIVE_RULES.ko.md`의 YAML 스펙 블록이 `.claude/settings.json`과 어긋나지 않는지 (permission rule, hook script 경로, `Stop` hook 존재 여부를 양방향으로 비교 — 실제로 켜진 항목이 문서에 빠짐없이 적혀 있는지 + 문서에 적힌 항목 중 더 이상 켜져 있지 않은 stale 항목은 없는지)

## 강화 로드맵

이 하네스를 발전시킬 때는 다음 순서를 권장합니다.

1. 언어별 테스트와 린트 어댑터를 추가합니다.
2. Codex와 Gemini의 안정적인 도구별 설정 방식이 확인되면 어댑터에 반영합니다.
3. 훅 스크립트에 대한 하네스 자체 테스트를 늘립니다.
4. 위험 명령과 시크릿 유출을 막는 보안 검사를 추가합니다.
5. Python, Node, Go, Rust, 혼합 저장소용 project template을 추가합니다.
