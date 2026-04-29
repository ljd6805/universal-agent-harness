# 범용 에이전트 하네스 상세 가이드

이 문서는 현재 하네스의 목적, 구조, 설정 범위, 특징, 동작 방식, 한계, 강화 방향을 이해하기 위한 학습용 문서입니다.

## 1. 하네스란 무엇인가

여기서 말하는 하네스는 Codex, Claude, Gemini 같은 AI 코딩 에이전트가 프로젝트 안에서 일할 때 따르는 공통 운영 레이어입니다.

애플리케이션 코드가 아니라, 에이전트가 작업하는 방식을 정리하는 기반입니다.

하네스가 담당하는 일은 크게 네 가지입니다.

1. 에이전트에게 동일한 작업 규칙을 알려준다.
2. 파일 수정 후 포맷, 테스트, TDD 확인 같은 반복 검사를 자동화한다.
3. 도구별 설정을 한곳에서 관리한다.
4. 시간이 지나도 규칙이 흩어지지 않게 구조를 잡아준다.

즉, 이 저장소는 "코드를 만드는 프로젝트"라기보다 "코드를 만드는 에이전트를 관리하는 프로젝트"입니다.

## 2. 현재 하네스의 핵심 철학

현재 구성의 핵심은 다음 문장으로 요약할 수 있습니다.

```text
공통 규칙은 하나로 유지하고, 도구별 차이는 어댑터로 분리한다.
```

Codex, Claude, Gemini가 모두 같은 규칙을 참고하게 하려면 각 도구별 파일에 같은 내용을 복사해두면 안 됩니다. 복사된 규칙은 시간이 지나면 조금씩 달라집니다.

그래서 이 하네스는 루트의 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`를 모두 하나의 공통 파일로 연결합니다.

```text
AGENTS.md  -> .agent-harness/rules/AGENT_GUIDE.md
CLAUDE.md  -> .agent-harness/rules/AGENT_GUIDE.md
GEMINI.md  -> .agent-harness/rules/AGENT_GUIDE.md
```

이 구조에서는 규칙을 바꾸고 싶을 때 `.agent-harness/rules/AGENT_GUIDE.md` 하나만 수정하면 됩니다.

## 3. 전체 디렉터리 구조

현재 구조는 다음과 같습니다.

```text
.
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
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
└── tests/
    └── test_harness.py
```

각 영역의 역할은 명확히 분리되어 있습니다.

| 영역 | 역할 |
| --- | --- |
| 루트 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | 각 에이전트가 처음 읽는 진입점 |
| `.agent-harness/rules/` | 모든 에이전트가 공유하는 실제 규칙 |
| `.agent-harness/hooks/` | 포맷, 테스트, TDD 검사 같은 자동화 스크립트 |
| `.agent-harness/adapters/` | Codex, Claude, Gemini별 설정 |
| `.claude/` | Claude Code가 실제로 찾는 설정 위치 |
| `tests/` | 하네스 자체가 깨지지 않았는지 확인하는 테스트 |

## 4. 왜 symlink를 쓰는가

이 하네스는 여러 곳에서 symlink를 사용합니다.

symlink는 "이 파일의 실제 내용은 다른 파일에 있다"는 연결입니다.

현재 중요한 symlink는 네 개입니다.

```text
AGENTS.md           -> .agent-harness/rules/AGENT_GUIDE.md
CLAUDE.md           -> .agent-harness/rules/AGENT_GUIDE.md
GEMINI.md           -> .agent-harness/rules/AGENT_GUIDE.md
.claude/settings.json -> ../.agent-harness/adapters/claude/settings.json
```

이 방식의 장점은 다음과 같습니다.

- 같은 규칙을 세 번 복사하지 않아도 됩니다.
- Codex, Claude, Gemini가 같은 정책을 보게 됩니다.
- 어떤 파일이 진짜 원본인지 명확합니다.
- 나중에 어댑터가 많아져도 공통 코어는 그대로 유지됩니다.

주의할 점도 있습니다.

- 일부 환경은 symlink를 잘 지원하지 않을 수 있습니다.
- 그런 환경에서는 symlink 대신 짧은 안내 파일을 복사해서 둘 수 있습니다.
- GitHub에서는 symlink가 링크 파일로 보이므로, 의도한 구조인지 테스트로 확인하는 것이 좋습니다.

현재 `tests/test_harness.py`는 이 symlink들이 올바른 위치를 가리키는지 검사합니다.

## 5. 공통 규칙 파일: `.agent-harness/rules/AGENT_GUIDE.md`

이 파일은 하네스의 가장 중요한 정책 파일입니다.

현재 포함된 규칙은 다음과 같습니다.

### 5.1 수정 전 탐색

에이전트는 파일을 수정하기 전에 관련 파일을 먼저 읽고, git 상태를 확인하고, 기존 사용자 변경을 보존해야 합니다.

이 규칙이 필요한 이유는 간단합니다.

AI 에이전트가 맥락 없이 바로 수정하면 기존 작업을 덮어쓰거나, 프로젝트 스타일과 맞지 않는 코드를 만들 가능성이 커집니다.

### 5.2 TDD 기본 원칙

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

### 5.3 병렬화 판단

에이전트가 작업을 시작할 때 병렬로 나눌 수 있는지 판단하게 합니다.

병렬화가 적합한 경우:

- 서로 다른 파일이나 모듈을 독립적으로 수정할 수 있을 때
- 실패 원인이 서로 다를 때
- 조사, 구현, 검증이 상태를 공유하지 않을 때

단일 작업이 적합한 경우:

- 실패 원인이 연결되어 있을 때
- 전체 시스템을 같이 봐야 할 때
- 같은 파일을 여러 작업이 동시에 수정해야 할 때

### 5.4 완료 전 검증

에이전트는 완료 보고 전에 테스트나 검증을 수행해야 합니다.

검증을 할 수 없다면 "못 했다"는 사실과 이유를 말해야 합니다.

이 규칙은 매우 중요합니다. 하네스의 목적은 에이전트가 그럴듯한 말만 하고 끝내는 것이 아니라, 확인 가능한 작업 습관을 갖도록 만드는 것입니다.

### 5.5 하네스 유지 원칙

공통 규칙, 공통 자동화, 도구별 설정을 각각 정해진 위치에 두도록 합니다.

```text
.agent-harness/rules/      공통 규칙
.agent-harness/hooks/      공통 자동화
.agent-harness/adapters/   도구별 설정
```

이 원칙을 지키면 하네스가 커져도 구조가 무너지지 않습니다.

## 6. 도구별 설정 범위

현재 세 도구의 설정 범위는 동일하지 않습니다.

이 점을 정확히 이해하는 것이 중요합니다.

## 6.1 Codex

Codex 쪽 현재 설정은 다음 파일을 통해 이뤄집니다.

```text
AGENTS.md -> .agent-harness/rules/AGENT_GUIDE.md
```

즉, 현재 Codex에는 "공통 지침 문서"가 적용됩니다.

현재 Codex 어댑터는 다음 위치에 있습니다.

```text
.agent-harness/adapters/codex/README.md
```

아직 Codex 전용 자동 훅 설정은 없습니다. 이유는 이 저장소가 특정 Codex 실행 환경에 과하게 묶이지 않도록 하기 위해서입니다.

현재 Codex에 적용되는 범위:

- 작업 전 탐색 규칙
- TDD 원칙
- 병렬화 판단
- 완료 전 검증
- 하네스 유지 규칙

현재 Codex에 자동 적용되지 않는 범위:

- 파일 수정 후 자동 포맷
- 파일 수정 후 자동 테스트
- 파일 수정 후 TDD 가드 주입

이 자동화는 현재 Claude Code 어댑터에서만 직접 연결되어 있습니다.

## 6.2 Claude Code

Claude Code는 현재 가장 강하게 설정되어 있습니다.

Claude Code가 읽는 루트 파일:

```text
CLAUDE.md -> .agent-harness/rules/AGENT_GUIDE.md
```

Claude Code가 읽는 설정 파일:

```text
.claude/settings.json -> ../.agent-harness/adapters/claude/settings.json
```

실제 설정 원본:

```text
.agent-harness/adapters/claude/settings.json
```

Claude 어댑터는 두 가지를 설정합니다.

1. 허용 권한
2. PostToolUse / Stop 훅

### Claude 권한 설정

현재 허용된 권한은 다음과 같습니다.

```json
[
  "Bash(git *)",
  "Bash(ls *)",
  "Bash(find *)",
  "Bash(grep *)",
  "Read",
  "Edit",
  "Write"
]
```

의미는 다음과 같습니다.

| 권한 | 의미 |
| --- | --- |
| `Read` | 파일 읽기 허용 |
| `Edit` | 기존 파일 수정 허용 |
| `Write` | 새 파일 작성 허용 |
| `Bash(git *)` | git 명령 허용 |
| `Bash(ls *)` | 파일 목록 확인 허용 |
| `Bash(find *)` | 파일 탐색 허용 |
| `Bash(grep *)` | 텍스트 검색 허용 |

주의할 점:

- 이 권한은 Claude Code 설정입니다.
- Codex나 Gemini의 권한 체계와 동일하지 않습니다.
- 위험한 명령을 폭넓게 허용하지 않도록 현재는 비교적 좁게 시작했습니다.

### Claude PostToolUse 훅

Claude adapter는 `Write`, `Edit`, `MultiEdit` 이후 세 개의 훅을 실행합니다.

```text
1. python3 .agent-harness/hooks/format_changed_file.py
2. python3 .agent-harness/hooks/run_tests.py
3. python3 .agent-harness/hooks/tdd_guard.py
```

즉, Claude가 파일을 쓰거나 수정하면 포맷, 테스트, TDD 확인이 순서대로 실행됩니다.

### Claude Stop 훅

작업 종료 시 다음 메시지를 출력합니다.

```text
범용 에이전트 하네스 종료 훅 완료.
```

이 훅은 현재는 단순한 생존 신호에 가깝습니다. 나중에는 세션 요약, 검증 누락 경고, 작업 로그 저장 같은 기능으로 강화할 수 있습니다.

## 6.3 Gemini

Gemini 쪽 현재 설정은 다음 파일을 통해 이뤄집니다.

```text
GEMINI.md -> .agent-harness/rules/AGENT_GUIDE.md
```

Gemini 어댑터는 다음 위치에 있습니다.

```text
.agent-harness/adapters/gemini/README.md
```

현재 Gemini 전용 자동 훅 설정은 없습니다.

현재 Gemini에 적용되는 범위:

- 공통 지침 문서
- 작업 전 탐색 규칙
- TDD 원칙
- 병렬화 판단
- 완료 전 검증
- 하네스 유지 규칙

현재 Gemini에 자동 적용되지 않는 범위:

- 파일 수정 후 자동 포맷
- 파일 수정 후 자동 테스트
- 파일 수정 후 TDD 가드 주입

## 7. 훅 스크립트 상세

공통 훅 스크립트는 `.agent-harness/hooks/` 아래에 있습니다.

이 스크립트들은 특정 에이전트에 종속되지 않도록 만들어졌습니다. 현재는 Claude 어댑터가 호출하지만, Codex나 Gemini에서 비슷한 훅 구조를 안정적으로 제공하면 같은 스크립트를 재사용할 수 있습니다.

## 7.1 `format_changed_file.py`

역할:

```text
변경된 파일을 감지하고, 가능한 포맷터가 있으면 실행한다.
```

입력:

- stdin으로 들어오는 JSON payload
- `tool_input.file_path`
- `tool_input.path`
- `tool_response.filePath`
- `tool_response.file_path`

동작:

1. 변경된 파일 경로를 찾습니다.
2. 파일이 없거나 프로젝트 밖이면 종료합니다.
3. 확장자를 확인합니다.
4. 지원하는 확장자이면 포맷터를 실행합니다.

현재 지원 확장자:

| 확장자 | 실행 |
| --- | --- |
| `.js`, `.ts`, `.jsx`, `.tsx`, `.json`, `.css`, `.html`, `.md` | `npx --yes prettier --write <file>` |
| `.py` | `python3 -m black <file>` |

특징:

- 포맷터가 설치되어 있지 않으면 조용히 스킵합니다.
- 포맷 실패가 전체 작업을 막지는 않습니다.
- 프로젝트 밖 파일은 수정하지 않습니다.

강화 아이디어:

- `ruff format` 지원
- `gofmt` 지원
- `rustfmt` 지원
- 포맷 실패를 조용히 무시하지 않고 로그에 남기기
- 프로젝트별 포맷터 우선순위 설정

## 7.2 `run_tests.py`

역할:

```text
프로젝트에서 가능한 테스트 명령을 감지해 실행한다.
```

동작:

1. 변경된 파일 경로를 확인합니다.
2. 변경 파일이 프로젝트 밖이면 종료합니다.
3. `package.json`이 있으면 Node 테스트를 실행합니다.
4. Python 테스트 파일이 있으면 pytest를 실행합니다.

현재 테스트 감지:

| 조건 | 실행 |
| --- | --- |
| `package.json` 존재 | `npm test --if-present` |
| `test_*.py` 또는 `*_test.py` 존재 | `python3 -m pytest` |
| 둘 다 없음 | 아무 것도 실행하지 않음 |

주의할 점:

- `package.json`이 있으면 Python 테스트보다 Node 테스트가 우선입니다.
- pytest가 설치되어 있지 않으면 실패할 수 있습니다.
- 현재는 실패 결과를 별도 요약하지 않습니다.
- 대형 프로젝트에서는 매번 전체 테스트를 돌리는 방식이 느릴 수 있습니다.

강화 아이디어:

- 변경 파일에 대응하는 가까운 테스트만 실행
- `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml` 감지
- lint/typecheck 별도 훅 추가
- 실패 로그를 `.agent-harness/logs/`에 저장
- 테스트 시간이 긴 프로젝트에서 fast/full 모드 분리

## 7.3 `tdd_guard.py`

역할:

```text
프로덕션 코드 파일에 대응하는 테스트 파일이 없으면 에이전트에게 경고한다.
```

검사 대상 확장자:

```text
.py, .js, .ts, .jsx, .tsx
```

테스트 파일로 보는 패턴:

```text
test_<name>.<ext>
<name>_test.<ext>
<name>.test.<ext>
<name>.spec.<ext>
```

예를 들어 `calculator.py`를 수정하면 다음 이름을 찾습니다.

```text
test_calculator.py
calculator_test.py
calculator.test.py
calculator.spec.py
```

경고 메시지는 Claude hook의 `additionalContext` 형태로 출력됩니다.

현재 특징:

- 테스트가 없다고 해서 작업을 차단하지는 않습니다.
- 경고를 통해 에이전트가 TDD 원칙을 다시 보게 합니다.
- `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`는 탐색에서 제외합니다.

현재 한계:

- 테스트가 같은 디렉터리에 있는지, 별도 `tests/`에 있는지는 구분하지 않고 이름만 봅니다.
- 실제 테스트 내용이 해당 코드를 검증하는지는 확인하지 않습니다.
- 파일 이름 기반이므로 복잡한 모듈 구조에서는 오탐이나 미탐이 있을 수 있습니다.

강화 아이디어:

- `src/foo/bar.py`와 `tests/foo/test_bar.py` 매핑 지원
- 테스트 내용에서 import 대상 확인
- 경고만 하지 않고 특정 조건에서는 차단
- 사용자 승인 예외 목록 지원
- 언어별 테스트 관례 분리

## 8. 현재 자동화와 비자동화 구분

하네스를 강화하려면 "지침으로만 존재하는 것"과 "자동으로 실행되는 것"을 구분해야 합니다.

현재 자동으로 실행되는 것:

| 항목 | 적용 대상 | 설명 |
| --- | --- | --- |
| Claude `PostToolUse` 포맷 | Claude | 파일 수정 후 포맷 시도 |
| Claude `PostToolUse` 테스트 | Claude | 파일 수정 후 테스트 시도 |
| Claude `PostToolUse` TDD 가드 | Claude | 프로덕션 파일에 테스트가 없으면 경고 |
| Claude `Stop` 훅 | Claude | 작업 종료 메시지 출력 |
| unittest 자체 테스트 | 수동 실행 | 하네스 구조와 TDD 가드 검사 |

현재 지침으로만 존재하는 것:

| 항목 | 적용 대상 | 설명 |
| --- | --- | --- |
| 수정 전 탐색 | Codex, Claude, Gemini | 공통 규칙 파일에 명시 |
| TDD 기본 원칙 | Codex, Claude, Gemini | 공통 규칙 파일에 명시 |
| 병렬화 판단 | Codex, Claude, Gemini | 공통 규칙 파일에 명시 |
| 완료 전 검증 | Codex, Claude, Gemini | 공통 규칙 파일에 명시 |
| Codex 자동 훅 | Codex | 아직 어댑터 자리만 있음 |
| Gemini 자동 훅 | Gemini | 아직 어댑터 자리만 있음 |

이 구분이 중요합니다.

문서 규칙은 에이전트의 행동을 유도합니다. 하지만 자동 훅은 실제로 실행됩니다. 강한 하네스를 만들려면 중요한 규칙을 점차 자동화해야 합니다.

## 9. 하네스 자체 테스트

현재 테스트 파일은 다음 위치에 있습니다.

```text
tests/test_harness.py
```

실행 명령:

```bash
python3 -m unittest discover -s tests
```

현재 테스트하는 것:

1. `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`가 공통 규칙 파일을 가리키는지
2. `.claude/settings.json`이 Claude adapter를 가리키는지
3. Claude adapter가 유효한 JSON인지
4. 테스트 없는 프로덕션 파일에 대해 `tdd_guard.py`가 경고하는지
5. 매칭 테스트가 있으면 `tdd_guard.py`가 조용히 넘어가는지

아직 테스트하지 않는 것:

- `format_changed_file.py`의 실제 포맷 동작
- `run_tests.py`의 테스트 러너 감지 우선순위
- README 문서의 구조 예시가 실제와 일치하는지
- adapter별 설정이 의도한 hook을 모두 참조하는지

강화할 때는 새 훅을 추가할 때마다 최소 하나의 하네스 테스트도 같이 추가하는 것이 좋습니다.

## 10. 현재 저장소의 설정 범위 요약

현재 저장소는 다음 수준까지 설정되어 있습니다.

| 영역 | 현재 상태 |
| --- | --- |
| 범용 규칙 | 있음 |
| Codex 진입점 | 있음, `AGENTS.md` symlink |
| Claude 진입점 | 있음, `CLAUDE.md` symlink |
| Gemini 진입점 | 있음, `GEMINI.md` symlink |
| Claude 훅 | 있음 |
| Codex 훅 | 아직 없음 |
| Gemini 훅 | 아직 없음 |
| 포맷 자동화 | Claude 어댑터를 통해 실행 |
| 테스트 자동화 | Claude 어댑터를 통해 실행 |
| TDD 경고 | Claude 어댑터를 통해 실행 |
| 하네스 자체 테스트 | 있음 |
| 로그 저장 | 아직 없음 |
| 언어별 어댑터 | 아직 기본 수준 |
| 보안 정책 | 아직 기본 수준 |

## 11. 이 하네스의 특징

현재 하네스의 좋은 점은 다음과 같습니다.

### 11.1 공통 규칙 단일화

세 도구가 하나의 규칙 파일을 봅니다. 이 덕분에 규칙이 흩어질 가능성이 줄어듭니다.

### 11.2 어댑터 구조

도구별 차이를 `.agent-harness/adapters/`에 둡니다. 나중에 Codex, Gemini 설정이 추가되어도 공통 규칙과 섞이지 않습니다.

### 11.3 hook 재사용 가능성

훅 스크립트는 `.agent-harness/hooks/`에 있으며 특정 도구 이름에 묶이지 않습니다. 현재는 Claude가 호출하지만, 다른 도구에서도 재사용할 수 있습니다.

### 11.4 테스트 가능한 하네스

하네스 자체를 테스트합니다. 이 점이 중요합니다. 하네스는 앞으로 계속 강화될 예정이므로, 구조가 깨지는지 확인할 수 있어야 합니다.

### 11.5 보수적인 권한

Claude 권한은 기본 탐색과 파일 편집 중심입니다. 아직 위험한 명령을 넓게 열어두지 않았습니다.

## 12. 현재 한계

현재 하네스는 출발점입니다. 아직 강력한 완성형은 아닙니다.

중요한 한계는 다음과 같습니다.

1. Codex와 Gemini는 아직 자동 훅이 없습니다.
2. Claude 훅도 실패를 강하게 차단하지 않습니다.
3. 테스트 감지는 단순합니다.
4. 포맷 실패나 테스트 실패 로그가 별도로 저장되지 않습니다.
5. 언어별 프로젝트 관례가 충분히 반영되어 있지 않습니다.
6. 보안 정책이 아직 구체적이지 않습니다.
7. "테스트 파일 존재"만 확인하지, 테스트 품질은 확인하지 않습니다.

이 한계를 알고 있어야 다음 강화 방향을 올바르게 잡을 수 있습니다.

## 13. 추천 강화 순서

하네스를 키울 때는 한 번에 많은 기능을 넣기보다, 검증 가능한 단위로 강화하는 것이 좋습니다.

추천 순서는 다음과 같습니다.

### 13.1 문서와 테스트를 먼저 안정화

- README와 상세 가이드를 최신 상태로 유지
- 구조 테스트 강화
- adapter JSON schema 테스트 추가

### 13.2 훅 관측성 추가

- `.agent-harness/logs/`에 hook 실행 결과 저장
- 어떤 파일에 어떤 훅이 실행됐는지 기록
- 포맷, 테스트, TDD 가드 결과를 요약

### 13.3 테스트 러너 확장

언어별 감지를 추가합니다.

| 파일 | 예상 명령 |
| --- | --- |
| `pyproject.toml` | `python3 -m pytest` 또는 프로젝트 설정 기반 |
| `package.json` | `npm test --if-present` |
| `pnpm-lock.yaml` | `pnpm test` |
| `yarn.lock` | `yarn test` |
| `go.mod` | `go test ./...` |
| `Cargo.toml` | `cargo test` |

### 13.4 lint와 typecheck 추가

테스트만으로는 충분하지 않습니다.

추가 후보:

- Python: `ruff check`, `mypy`, `pyright`
- TypeScript: `tsc --noEmit`, `eslint`
- Go: `go vet`
- Rust: `cargo clippy`

### 13.5 TDD guard 고도화

현재는 파일 이름만 봅니다.

다음 단계에서는 다음을 고려할 수 있습니다.

- `src/`와 `tests/` 매핑
- import 기반 매칭
- 테스트 없는 프로덕션 변경 차단 모드
- 예외 파일 목록
- 문서/설정 변경 자동 예외

### 13.6 보안 정책 추가

에이전트 하네스에서 보안은 중요합니다.

추가 후보:

- secret 탐지
- `.env` 읽기/출력 제한
- destructive command 감지
- 외부 네트워크 접근 정책
- dependency install 승인 정책

### 13.7 도구별 어댑터 강화

도구별로 안정적인 설정 방법이 확인되면 어댑터에 추가합니다.

- Codex 어댑터: Codex 프로젝트 설정, 권한, 검증 명령 문서화
- Claude 어댑터: 훅, 권한, 종료/세션 훅 강화
- Gemini 어댑터: Gemini CLI나 IDE 연동 설정 추가

## 14. 하네스를 수정할 때의 원칙

앞으로 이 저장소를 강화할 때는 다음 원칙을 지키는 것이 좋습니다.

1. 공통 규칙은 `.agent-harness/rules/AGENT_GUIDE.md`에 둡니다.
2. 도구별 설정은 `.agent-harness/adapters/<tool>/`에 둡니다.
3. 실행 가능한 자동화는 `.agent-harness/hooks/`에 둡니다.
4. 새 자동화를 추가하면 `tests/`에 하네스 테스트를 추가합니다.
5. README는 입구 역할로 유지하고, 긴 설명은 `docs/`에 둡니다.
6. 자동화가 실제로 강제하는 것과 문서로만 안내하는 것을 구분해서 기록합니다.
7. 위험한 권한이나 destructive command는 기본 허용하지 않습니다.

## 15. 빠른 확인 명령

하네스 상태를 확인할 때 자주 쓸 명령입니다.

```bash
find . -maxdepth 4 -type f -o -type l
```

```bash
python3 -m json.tool .agent-harness/adapters/claude/settings.json
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

## 16. 가장 먼저 고민해볼 질문

이 하네스를 더 강화하기 전에 다음 질문에 답해보면 방향을 잡기 좋습니다.

1. 나는 어떤 언어와 프레임워크 프로젝트에 이 하네스를 가장 자주 적용할 것인가?
2. 에이전트가 실수했을 때 가장 위험한 행동은 무엇인가?
3. 테스트 실패를 경고로 둘 것인가, 작업 차단 조건으로 삼을 것인가?
4. Codex, Claude, Gemini 중 어떤 도구를 가장 강하게 자동화할 것인가?
5. 프로젝트별 설정과 전역 하네스 설정을 어떻게 나눌 것인가?
6. 빠른 작업 속도와 강한 검증 중 어디에 더 무게를 둘 것인가?

이 질문에 대한 답이 정해지면 다음 강화 작업의 우선순위도 자연스럽게 정해집니다.
