# 범용 에이전트 하네스 상세 가이드

이 문서는 현재 하네스의 목적, 구조, 설정 범위, 특징, 동작 방식, 한계, 강화 방향을 이해하기 위한 상세 가이드입니다.

README가 빠른 입구라면, 이 문서는 왜 이런 구조를 선택했는지와 실제 프로젝트에 어떻게 적용하는지를 조금 더 자세히 설명합니다.

## 1. 하네스란 무엇인가

여기서 말하는 하네스는 Codex, Claude, Gemini, OpenCode 같은 AI 코딩 에이전트가 프로젝트 안에서 일할 때 따르는 공통 운영 레이어입니다.

애플리케이션 코드가 아니라, 에이전트가 작업하는 방식을 정리하는 기반입니다.

하네스가 담당하는 일은 크게 네 가지입니다.

1. 에이전트에게 동일한 작업 규칙을 알려준다.
2. 파일 수정 후 포맷, 테스트, TDD 확인 같은 반복 검사를 자동화한다.
3. 도구별 설정을 한곳에서 관리한다.
4. 프로젝트별 지침과 실행 설정을 공통 규칙과 분리해 관리한다.

즉, 이 저장소는 "코드를 만드는 프로젝트"라기보다 "코드를 만드는 에이전트를 관리하는 프로젝트"입니다.

## 2. 현재 하네스의 핵심 철학

현재 구성의 핵심은 다음 두 문장으로 요약할 수 있습니다.

```text
공통 규칙은 하나로 유지하고, 도구별 차이는 adapter로 분리한다.
Base harness와 project harness를 분리한다.
```

Codex, Claude, Gemini, OpenCode가 모두 같은 규칙을 참고하게 하려면 각 도구별 파일에 같은 내용을 길게 복사해두면 안 됩니다. 복사된 규칙은 시간이 지나면 조금씩 달라집니다.

그래서 공통 규칙의 실제 원본은 하나로 둡니다.

```text
.agent-harness/rules/AGENT_GUIDE.md
```

각 도구별 진입점은 이 공통 가이드를 자기 도구가 지원하는 방식으로 참조합니다.

- `CLAUDE.md`: `@.agent-harness/rules/AGENT_GUIDE.md`
- `GEMINI.md`: `@.agent-harness/rules/AGENT_GUIDE.md`
- `AGENTS.md`: 공통 가이드를 읽고 따르라는 안내 주석
- `opencode.json`: `instructions` 필드로 공통 가이드 지정

또한 이 저장소 자체는 개별 프로젝트 전용 설정 묶음이 아니라, 여러 프로젝트에 적용하기 위한 team base harness입니다.

각 실제 프로젝트는 이 base harness를 적용한 뒤, 프로젝트별 지침과 실행 설정을 추가합니다.

## 3. Base Harness와 Project Harness

이 하네스는 두 층으로 이해하는 것이 가장 쉽습니다.

| 구분 | 위치 | 역할 |
| --- | --- | --- |
| Base Harness | `universal-agent-harness` 저장소 | 팀 공통 규칙, 공통 hook, adapter 기본값, template 제공 |
| Project Harness | 각 프로젝트의 `.agent-harness/` | 프로젝트별 지침, 실행 명령, 보호 경로, 예외 정책 |
| Project Guide | `.agent-harness/rules/PROJECT_GUIDE.md` | 에이전트가 읽는 프로젝트별 자연어 지침 |
| Project Config | `.agent-harness/harness.config.json` | hook이나 agent가 참고할 프로젝트별 실행 설정 |

핵심은 다음과 같습니다.

```text
Base harness는 “어떻게 일해야 하는가”를 정의합니다.
Project harness는 “이 프로젝트에서는 어떻게 검증해야 하는가”를 정의합니다.
```

Base harness에는 모든 프로젝트에 적용 가능한 원칙을 둡니다.

- 수정 전 탐색
- 기존 사용자 변경 보존
- TDD 기본 원칙
- 완료 전 검증
- 공통 hook 구조
- 도구별 adapter 기본 구조

Project harness에는 프로젝트별로 달라지는 내용을 둡니다.

- build/test/lint/typecheck 명령
- source/test directory 구조
- 수정 주의 경로
- legacy 예외
- 테스트 실패를 warning으로 둘지 strict로 둘지 같은 정책

이렇게 나누면 공통 규칙은 유지하면서도, 프로젝트마다 다른 현실을 무리 없이 반영할 수 있습니다.

## 4. 전체 디렉터리 구조

현재 base harness 저장소 구조는 다음과 같습니다.

```text
.
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── opencode.json
├── .claude/
│   └── settings.json
├── .agent-harness/
│   ├── rules/
│   │   └── AGENT_GUIDE.md
│   ├── hooks/
│   │   ├── format_changed_file.py
│   │   ├── run_tests.py
│   │   └── tdd_guard.py
│   └── adapters/
│       ├── claude/
│       │   └── settings.json
│       ├── codex/
│       │   └── README.md
│       └── gemini/
│           └── README.md
├── templates/
│   └── project/
│       ├── PROJECT_GUIDE.md
│       └── harness.config.json
└── tests/
    └── test_harness.py
```

각 영역의 역할은 다음과 같습니다.

| 영역 | 역할 |
| --- | --- |
| 루트 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `opencode.json` | 각 에이전트가 처음 읽는 진입점 |
| `.agent-harness/rules/` | 모든 에이전트가 공유하는 실제 규칙 |
| `.agent-harness/hooks/` | 포맷, 테스트, TDD 검사 같은 자동화 스크립트 |
| `.agent-harness/adapters/` | Codex, Claude, Gemini별 설정 |
| `.claude/` | Claude Code가 실제로 찾는 설정 위치 |
| `templates/project/` | 프로젝트별 지침과 실행 설정 template |
| `tests/` | 하네스 자체가 깨지지 않았는지 확인하는 테스트 |

## 5. 왜 symlink 대신 native import를 쓰는가

이 하네스는 처음에는 진입점 파일을 symlink로 구성했습니다. symlink는 "이 파일의 실제 내용은 다른 파일에 있다"는 연결이라 같은 규칙을 여러 번 복사하지 않아도 되고 어떤 파일이 진짜 원본인지 명확하다는 장점이 있습니다.

하지만 symlink는 Windows를 비롯한 일부 환경과 일부 git 설정(`core.symlinks=false`)에서 제대로 동작하지 않습니다. 이런 환경에서 저장소를 clone하면 symlink가 실제 링크가 아니라 "링크 대상 경로가 적힌 일반 텍스트 파일"로 checkout되어, 에이전트 도구가 진입점 파일을 읽어도 규칙 내용이 아니라 경로 문자열만 보게 됩니다.

그래서 지금은 각 에이전트 도구가 지원하는 native 방식 또는 그에 준하는 방식을 사용합니다.

```text
CLAUDE.md             : "@.agent-harness/rules/AGENT_GUIDE.md" (Claude Code native import)
GEMINI.md             : "@.agent-harness/rules/AGENT_GUIDE.md" (Gemini CLI native import)
AGENTS.md             : 공통 가이드를 읽고 따르라는 안내 주석
opencode.json         : "instructions" 필드로 .agent-harness/rules/AGENT_GUIDE.md 지정
.claude/settings.json : .agent-harness/adapters/claude/settings.json 내용을 그대로 복사
```

이 방식의 장점은 다음과 같습니다.

- 운영체제나 git 설정과 무관하게 항상 같은 내용을 읽습니다.
- 각 도구가 지원하는 방식을 그대로 사용하므로 별도의 변환 과정이 필요 없습니다.
- 공통 가이드의 실제 원본은 여전히 `.agent-harness/rules/AGENT_GUIDE.md` 하나뿐입니다.

대신 `CLAUDE.md`, `GEMINI.md`, `.claude/settings.json`처럼 내용을 직접 적거나 복사해 둔 파일은, 원본인 `.agent-harness/` 아래 파일이 바뀌면 함께 갱신해야 합니다.

현재 `tests/test_harness.py`는 각 진입점이 공통 가이드를 올바르게 가리키는지, `.claude/settings.json`이 공유 adapter 설정과 일치하는지 검사합니다.

## 6. 공통 규칙 파일: `.agent-harness/rules/AGENT_GUIDE.md`

이 파일은 하네스의 가장 중요한 정책 파일입니다.

현재 포함된 규칙은 다음과 같습니다.

### 6.1 수정 전 탐색

에이전트는 파일을 수정하기 전에 관련 파일을 먼저 읽고, git 상태를 확인하고, 기존 사용자 변경을 보존해야 합니다.

이 규칙이 필요한 이유는 간단합니다. AI 에이전트가 맥락 없이 바로 수정하면 기존 작업을 덮어쓰거나, 프로젝트 스타일과 맞지 않는 코드를 만들 가능성이 커집니다.

### 6.2 프로젝트별 지침 확인

프로젝트에 다음 파일이 있으면 공통 지침과 함께 읽고 따릅니다.

```text
.agent-harness/rules/PROJECT_GUIDE.md
.agent-harness/harness.config.json
```

`PROJECT_GUIDE.md`는 프로젝트별 자연어 지침입니다. 프로젝트 개요, 검증 방식, 수정 주의 경로, 보고 규칙처럼 작업 맥락에 필요한 내용을 확인합니다.

`harness.config.json`은 프로젝트별 실행 설정입니다. build, test, lint, typecheck 명령과 source/test/protected path, policy 값을 확인합니다.

### 6.3 TDD 기본 원칙

프로덕션 코드는 기본적으로 실패하는 테스트를 먼저 작성한 뒤 구현하도록 합니다.

```text
write failing test -> confirm failure -> minimal implementation -> confirm pass -> refactor
```

단, 예외도 명시되어 있습니다.

- 문서만 수정하는 경우
- 하네스 설정만 수정하는 경우
- 사용자가 명시한 실험적 스캐폴딩
- 사용자가 승인한 예외

현재 하네스 작업 자체는 문서와 설정 중심이므로 TDD 예외에 해당할 수 있습니다. 그래도 하네스 자체 테스트는 추가되어 있습니다.

### 6.4 병렬화 판단

에이전트가 작업을 시작할 때 병렬로 나눌 수 있는지 판단하게 합니다.

병렬화가 적합한 경우:

- 서로 다른 파일이나 모듈을 독립적으로 수정할 수 있을 때
- 실패 원인이 서로 다를 때
- 조사, 구현, 검증이 상태를 공유하지 않을 때

단일 작업이 적합한 경우:

- 실패 원인이 연결되어 있을 때
- 전체 시스템을 같이 봐야 할 때
- 같은 파일을 여러 작업이 동시에 수정해야 할 때

### 6.5 완료 전 검증

에이전트는 완료 보고 전에 테스트나 검증을 수행해야 합니다.

프로젝트별 `harness.config.json`이 있으면 그 안의 검증 명령을 우선 참고합니다.

검증을 할 수 없다면 "못 했다"는 사실과 이유를 말해야 합니다.

이 규칙은 매우 중요합니다. 하네스의 목적은 에이전트가 그럴듯한 말만 하고 끝내는 것이 아니라, 확인 가능한 작업 습관을 갖도록 만드는 것입니다.

### 6.6 하네스 유지 원칙

공통 규칙, 공통 자동화, 도구별 설정, 프로젝트별 설정을 각각 정해진 위치에 둡니다.

```text
.agent-harness/rules/AGENT_GUIDE.md      공통 규칙
.agent-harness/rules/PROJECT_GUIDE.md    프로젝트별 자연어 지침
.agent-harness/harness.config.json       프로젝트별 실행 설정
.agent-harness/hooks/                    공통 자동화
.agent-harness/adapters/                 도구별 설정
```

## 7. Project Harness Template

프로젝트별 지침과 실행 설정을 쉽게 시작할 수 있도록 template을 제공합니다.

```text
templates/project/
├── PROJECT_GUIDE.md
└── harness.config.json
```

적용할 때는 다음 위치로 복사합니다.

```text
templates/project/PROJECT_GUIDE.md
-> .agent-harness/rules/PROJECT_GUIDE.md

templates/project/harness.config.json
-> .agent-harness/harness.config.json
```

### 7.1 PROJECT_GUIDE.md

`PROJECT_GUIDE.md`는 에이전트가 읽는 프로젝트별 자연어 지침입니다.

주요 내용은 다음과 같습니다.

- 프로젝트 개요
- 작업 전 확인
- 프로젝트별 검증 명령
- 수정 주의 경로
- 프로젝트별 예외
- 완료 보고 규칙

이 파일은 사람이 읽고 쉽게 고칠 수 있어야 합니다. 너무 많은 규칙을 넣기보다, 프로젝트에서 실제로 중요한 차이만 적는 것이 좋습니다.

### 7.2 harness.config.json

`harness.config.json`은 프로젝트별 실행 설정입니다.

기본 section은 다음과 같습니다.

```text
project   프로젝트 이름과 유형
commands  build/test/lint/typecheck 명령
paths     source/test/protected 경로
policy    tdd_guard/test_failure 같은 정책
```

이 파일은 나중에 hook이나 agent가 기계적으로 읽을 수 있는 설정입니다.

## 8. 현재 공통 hook

> 지금 켜져 있는 hook의 전체 목록과 on/off 상태는 [`ACTIVE_RULES.ko.md`](../.agent-harness/rules/ACTIVE_RULES.ko.md)를 참고하세요.
> 아래 절에서는 각 hook이 *어떻게* 동작하는지를 설명합니다.

### 8.1 format_changed_file.py

Claude Code의 파일 수정 hook에서 호출됩니다.

역할은 변경된 파일의 확장자를 보고 가능한 formatter를 실행하는 것입니다.

- JavaScript, TypeScript, JSON, CSS, HTML, Markdown: `npx --yes prettier --write <file>`
- Python: `python -m black <file>`

formatter가 없으면 조용히 넘어갑니다.

### 8.2 run_tests.py

파일 수정 이후 감지 가능한 테스트 명령을 실행합니다.

현재는 단순 감지 방식입니다.

- `package.json`이 있으면 `npm test --if-present`
- Python 테스트 파일이 있으면 `python -m pytest`

프로젝트별 test/build/lint/typecheck 명령은 앞으로 `.agent-harness/harness.config.json`을 통해 더 명확하게 다룰 수 있습니다.

### 8.3 tdd_guard.py

프로덕션 파일을 수정했는데 대응되는 테스트 파일이 없으면 경고를 출력합니다.

현재는 파일 이름 기반의 단순 매칭을 사용합니다.

- Python: `test_<name>.py`, `<name>_test.py`
- TypeScript/JavaScript: `<name>.test.ts`, `<name>.spec.ts`, `<name>.test.js`, `<name>.spec.js`

이 guard는 아직 강한 차단이 아니라 warning 중심입니다.

## 9. 도구별 적용 범위

> 각 규칙이 어떤 도구에 강제되고 어떤 도구에는 권고 수준인지는 [`ACTIVE_RULES.ko.md`](../.agent-harness/rules/ACTIVE_RULES.ko.md)의 스냅샷을 함께 참고하세요.

현재 도구별 적용 범위는 다음과 같습니다.

| 도구 | 현재 적용 |
| --- | --- |
| Codex | `AGENTS.md` 안내 주석을 통해 공통 가이드 확인을 유도 |
| Claude Code | `CLAUDE.md` native import와 `.claude/settings.json` hook 설정 사용 |
| Gemini CLI | `GEMINI.md` native import로 공통 가이드 참조 |
| OpenCode | `opencode.json`의 `instructions`로 공통 가이드 지정 |

가장 강하게 자동화가 연결된 도구는 현재 Claude Code입니다. Codex, Gemini, OpenCode는 각 도구의 안정적인 hook/설정 방식이 확인되면 adapter를 더 강화할 수 있습니다.

## 10. 하네스 자체 테스트

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

하네스는 앞으로 계속 강화될 예정이므로, 구조가 깨지는지 확인할 수 있어야 합니다. 이 저장소가 테스트를 갖는 이유가 바로 여기에 있습니다.

## 11. 현재 한계

현재 하네스는 출발점입니다. 아직 완성형은 아닙니다.

중요한 한계는 다음과 같습니다.

1. Codex, Gemini, OpenCode는 아직 Claude Code처럼 자동 hook이 강하게 연결되어 있지 않습니다.
2. Claude hook도 실패를 강하게 차단하지 않습니다.
3. 테스트 감지는 아직 단순합니다.
4. 포맷 실패나 테스트 실패 로그가 별도로 저장되지 않습니다.
5. 언어별 프로젝트 관례가 충분히 반영되어 있지 않습니다.
6. 보안 정책이 아직 구체적이지 않습니다.
7. "테스트 파일 존재"만 확인하지, 테스트 품질은 확인하지 않습니다.
8. project harness template은 시작점이며, 프로젝트별로 반드시 조정해야 합니다.

이 한계를 알고 있어야 다음 강화 방향을 올바르게 잡을 수 있습니다.

## 12. 추천 강화 순서

하네스를 키울 때는 한 번에 많은 기능을 넣기보다, 검증 가능한 단위로 강화하는 것이 좋습니다.

추천 순서는 다음과 같습니다.

### 12.1 문서와 테스트를 먼저 안정화

- README와 상세 가이드를 최신 상태로 유지
- 구조 테스트 강화
- adapter JSON schema 테스트 추가
- project template 테스트 유지

### 12.2 훅 관측성 추가

- `.agent-harness/logs/`에 hook 실행 결과 저장
- 어떤 파일에 어떤 hook이 실행됐는지 기록
- 포맷, 테스트, TDD guard 결과를 요약

### 12.3 테스트 러너 확장

언어별 감지를 추가합니다.

| 파일 | 예상 명령 |
| --- | --- |
| `pyproject.toml` | `python3 -m pytest` 또는 프로젝트 설정 기반 |
| `package.json` | `npm test --if-present` |
| `pnpm-lock.yaml` | `pnpm test` |
| `yarn.lock` | `yarn test` |
| `go.mod` | `go test ./...` |
| `Cargo.toml` | `cargo test` |

### 12.4 lint와 typecheck 추가

테스트만으로는 충분하지 않습니다.

추가 후보:

- Python: `ruff check`, `mypy`, `pyright`
- TypeScript: `tsc --noEmit`, `eslint`
- Go: `go vet`
- Rust: `cargo clippy`

### 12.5 TDD guard 고도화

현재는 파일 이름만 봅니다.

다음 단계에서는 다음을 고려할 수 있습니다.

- `src/`와 `tests/` 매핑
- import 기반 매칭
- 테스트 없는 프로덕션 변경 차단 모드
- 예외 파일 목록
- 문서/설정 변경 자동 예외

### 12.6 보안 정책 추가

에이전트 하네스에서 보안은 중요합니다.

추가 후보:

- secret 탐지
- 민감 설정 파일 출력 제한
- destructive command 감지
- 외부 네트워크 접근 정책
- dependency install 승인 정책

### 12.7 도구별 adapter 강화

도구별로 안정적인 설정 방법이 확인되면 adapter에 추가합니다.

- Codex adapter: Codex 프로젝트 설정, 권한, 검증 명령 문서화
- Claude adapter: hook, 권한, 종료/세션 hook 강화
- Gemini adapter: Gemini CLI나 IDE 연동 설정 추가
- OpenCode adapter: `opencode.json` 기반 설정과 hook 연동 방식 정리

## 13. 하네스를 수정할 때의 원칙

앞으로 이 저장소를 강화할 때는 다음 원칙을 지키는 것이 좋습니다.

1. 공통 규칙은 `.agent-harness/rules/AGENT_GUIDE.md`에 둡니다.
2. 프로젝트별 자연어 지침은 `.agent-harness/rules/PROJECT_GUIDE.md`에 둡니다.
3. 프로젝트별 실행 설정은 `.agent-harness/harness.config.json`에 둡니다.
4. 도구별 설정은 `.agent-harness/adapters/<tool>/`에 둡니다.
5. 실행 가능한 자동화는 `.agent-harness/hooks/`에 둡니다.
6. 새 자동화나 template을 추가하면 `tests/`에 하네스 테스트를 추가합니다.
7. README는 입구 역할로 유지하고, 긴 설명은 `docs/`에 둡니다.
8. 자동화가 실제로 강제하는 것과 문서로만 안내하는 것을 구분해서 기록합니다.
9. 위험한 권한이나 destructive command는 기본 허용하지 않습니다.

## 14. 빠른 확인 명령

하네스 상태를 확인할 때 자주 쓸 명령입니다.

```bash
find . -maxdepth 4 -type f -o -type l
```

```bash
python3 -m json.tool .agent-harness/adapters/claude/settings.json
```

```bash
python3 -m json.tool templates/project/harness.config.json
```

```bash
python3 -m py_compile .agent-harness/hooks/*.py tests/test_harness.py
```

```bash
python3 -m unittest discover -s tests
```

```bash
git status -sb
```

## 15. 가장 먼저 고민해볼 질문

이 하네스를 더 강화하기 전에 다음 질문에 답해보면 방향을 잡기 좋습니다.

1. 나는 어떤 언어와 프레임워크 프로젝트에 이 하네스를 가장 자주 적용할 것인가?
2. 에이전트가 실수했을 때 가장 위험한 행동은 무엇인가?
3. 테스트 실패를 경고로 둘 것인가, 작업 차단 조건으로 삼을 것인가?
4. Codex, Claude, Gemini, OpenCode 중 어떤 도구를 가장 강하게 자동화할 것인가?
5. 프로젝트별 설정과 base harness 설정을 어떻게 나눌 것인가?
6. 빠른 작업 속도와 강한 검증 중 어디에 더 무게를 둘 것인가?

이 질문에 대한 답이 정해지면 다음 강화 작업의 우선순위도 자연스럽게 정해집니다.
