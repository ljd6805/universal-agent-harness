# 범용 에이전트 하네스

이 저장소는 Codex, Claude, Gemini 같은 AI 코딩 에이전트를 공통 규칙으로 관리하기 위한 범용 하네스입니다.

애플리케이션 코드가 아니라, 에이전트가 프로젝트 안에서 어떻게 탐색하고, 수정하고, 검증하고, 보고해야 하는지를 정리하는 운영 기반입니다.

## 이 저장소의 목적

이 하네스의 목표는 에이전트 작업을 다음 상태로 만드는 것입니다.

- 여러 도구에서 일관되게 동작한다.
- 현재 설정과 규칙을 쉽게 확인할 수 있다.
- 시간이 지나며 안전하게 강화할 수 있다.
- 다른 저장소에 복사하거나 이식하기 쉽다.
- 하네스 자체도 테스트로 검증할 수 있다.

## 먼저 읽을 문서

하네스를 제대로 이해하고 강화 방향을 고민하려면 아래 문서부터 읽는 것을 권장합니다.

- [범용 에이전트 하네스 상세 가이드](docs/HARNESS_GUIDE.ko.md)

상세 가이드에서는 다음 내용을 설명합니다.

- 하네스가 무엇인지
- 왜 현재 구조를 선택했는지
- 각 파일과 디렉터리가 어떤 역할을 하는지
- Codex, Claude, Gemini에 각각 어떤 범위까지 적용되는지
- 훅 스크립트가 어떻게 동작하는지
- 현재 자동으로 강제되는 것과 문서로만 안내되는 것이 무엇인지
- 앞으로 어떤 순서로 강화하면 좋은지

## 저장소 구조

```text
.
├── AGENTS.md -> .agent-harness/rules/AGENT_GUIDE.md
├── CLAUDE.md -> .agent-harness/rules/AGENT_GUIDE.md
├── GEMINI.md -> .agent-harness/rules/AGENT_GUIDE.md
├── .claude/
│   └── settings.json -> ../.agent-harness/adapters/claude/settings.json
└── .agent-harness/
    ├── adapters/
    │   ├── claude/settings.json
    │   ├── codex/README.md
    │   └── gemini/README.md
    ├── hooks/
    │   ├── format_changed_file.py
    │   ├── run_tests.py
    │   └── tdd_guard.py
    └── rules/
        └── AGENT_GUIDE.md
```

## 설계 원칙

루트의 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 각 도구가 읽는 진입점입니다. 이 파일들은 작고 안정적으로 유지하고, 실제 규칙은 `.agent-harness/` 아래에 둡니다.

실제 원본은 다음 위치에 있습니다.

- `.agent-harness/rules/`: 모든 에이전트가 공유하는 작업 규칙
- `.agent-harness/hooks/`: 포맷, 테스트, TDD 확인 같은 공통 자동화 스크립트
- `.agent-harness/adapters/`: 도구별 설정

이 구조를 쓰면 Codex, Claude, Gemini의 지침이 서로 다르게 갈라지는 일을 줄일 수 있습니다.

## 에이전트 진입점

- Codex는 `AGENTS.md`를 읽습니다.
- Claude Code는 `CLAUDE.md`를 읽습니다.
- Gemini 계열 도구는 일반적으로 `GEMINI.md`를 읽습니다.

세 파일은 모두 같은 공통 가이드를 가리킵니다.

```text
.agent-harness/rules/AGENT_GUIDE.md
```

## 현재 자동화

현재 가장 강하게 연결된 도구는 Claude Code입니다. Claude Code는 `.claude/settings.json`을 읽고, 이 파일은 Claude 어댑터 설정을 가리킵니다.

```text
.agent-harness/adapters/claude/settings.json
```

Claude 어댑터는 파일 수정 이후 다음 공통 훅 스크립트를 실행합니다.

1. `format_changed_file.py`: Prettier 또는 Black이 있으면 변경 파일을 포맷합니다.
2. `run_tests.py`: 감지 가능한 테스트 명령을 실행합니다.
3. `tdd_guard.py`: 프로덕션 코드에 대응 테스트가 없으면 경고합니다.

Codex와 Gemini 어댑터는 현재 문서화된 기본 자리만 마련되어 있습니다. 공통 규칙은 이미 `AGENTS.md`와 `GEMINI.md`를 통해 적용되며, 각 도구가 안정적인 프로젝트 훅이나 설정 방식을 제공할 때 `.agent-harness/adapters/` 아래에 추가하면 됩니다.

## 검증 방법

하네스 자체 테스트는 다음 명령으로 실행합니다.

```bash
python3 -m unittest discover -s tests
```

현재 테스트는 다음을 확인합니다.

- 에이전트 진입점 symlink
- Claude 설정 symlink
- Claude 어댑터 JSON 유효성
- TDD 가드 경고 동작
- 대응 테스트가 있을 때 TDD 가드가 경고하지 않는 동작

## 강화 로드맵

이 하네스를 발전시킬 때는 다음 순서를 권장합니다.

1. 언어별 테스트와 린트 어댑터를 추가합니다.
2. Codex와 Gemini의 안정적인 도구별 설정 방식이 확인되면 어댑터에 반영합니다.
3. 훅 스크립트에 대한 하네스 자체 테스트를 늘립니다.
4. 위험 명령과 시크릿 유출을 막는 보안 검사를 추가합니다.
5. Python, Node, Go, Rust, 혼합 저장소용 템플릿을 추가합니다.

## 다른 프로젝트에 적용하기

하네스 디렉터리를 복사하고, 각 에이전트 진입점 링크를 만듭니다.

```bash
cp -r .agent-harness /path/to/project/
ln -s .agent-harness/rules/AGENT_GUIDE.md /path/to/project/AGENTS.md
ln -s .agent-harness/rules/AGENT_GUIDE.md /path/to/project/CLAUDE.md
ln -s .agent-harness/rules/AGENT_GUIDE.md /path/to/project/GEMINI.md
mkdir -p /path/to/project/.claude
ln -s ../.agent-harness/adapters/claude/settings.json /path/to/project/.claude/settings.json
```

symlink를 지원하지 않는 환경에서는 파일을 복사해도 됩니다. 다만 복사본에는 실제 원본이 `.agent-harness/rules/AGENT_GUIDE.md`라는 사실을 명확히 적어두는 것이 좋습니다.
