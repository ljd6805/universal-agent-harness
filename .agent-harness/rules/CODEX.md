# Codex 작업 지침

이 파일은 이 branch에서 Codex가 따라야 하는 작업 규칙의 원본입니다.

## 목적

이 하네스는 여러 agent를 동시에 지원하려는 범용 구조가 아니라, Codex 작업을 더 안전하고 검증 가능하게 만들기 위한 전용 운영 레이어입니다.

Codex의 루트 진입점은 `AGENTS.md`이고, `AGENTS.md`는 이 파일을 읽으라고 안내합니다.

```text
AGENTS.md -> .agent-harness/rules/CODEX.md
```

## 핵심 작업 흐름

### 1. 수정 전 먼저 탐색한다

- 관련 README, docs, test 파일을 먼저 읽습니다.
- git을 사용할 수 있으면 `git status -sb`로 현재 상태를 확인합니다.
- 기존 사용자 변경이 있는지 확인합니다.
- 현재 작업과 무관한 사용자 변경은 보존합니다.
- branch가 의도한 작업 branch인지 확인합니다.

### 2. 프로젝트별 지침을 확인한다

프로젝트에 다음 파일이 있으면 이 Codex guide와 함께 읽고 따릅니다.

- `.agent-harness/rules/PROJECT_GUIDE.md`
- `.agent-harness/harness.config.json`

프로젝트별 지침이 더 구체적이면 프로젝트별 지침을 우선합니다. 단, 이 파일의 안전 원칙은 유지합니다.

### 3. 기본값은 TDD다

프로덕션 코드는 실패하는 테스트를 먼저 작성한 뒤 구현하는 것을 기본값으로 삼습니다.

```text
실패하는 테스트 작성 -> 실패 확인 -> 최소 구현 -> 통과 확인 -> 리팩터
```

허용되는 예외는 다음과 같습니다.

- 문서만 수정하는 경우
- 하네스 설정만 수정하는 경우
- 사용자가 명시적으로 요청한 탐색적 스캐폴딩
- 사용자가 승인한 예외

### 4. Codex 작업 범위를 작게 유지한다

Codex 작업은 작고 검증 가능한 단위로 유지합니다. 강하게 결합된 변경은 한 번에 밀어붙이지 말고 단계로 나눕니다.

### 5. 완료 전 검증한다

완료를 보고하기 전에 다음을 수행합니다.

- 가능한 가장 관련 있는 테스트나 검사를 실행합니다.
- 프로젝트별 `harness.config.json`이 있으면 그 안의 검증 명령을 우선 참고합니다.
- 검증을 실행할 수 없다면 이유와 다음에 실행해야 할 명령을 명시합니다.

### 6. 보고는 증거 중심으로 한다

Codex 작업 완료 보고에는 최소한 다음을 포함합니다.

- 변경 요약
- 실행한 검증 명령
- 검증 결과
- 실행하지 못한 검증과 이유
- 남은 위험 또는 후속 작업

### 7. Codex 전용 구조를 유지한다

이 branch에서는 Codex 전용 구조를 유지합니다.

- Codex 진입점은 `AGENTS.md`입니다.
- Codex 규칙 원본은 `.agent-harness/rules/CODEX.md`입니다.
- Codex adapter 문서는 `.agent-harness/adapters/codex/`에 둡니다.
- 공통 hook script는 `.agent-harness/hooks/`에 둡니다.
- 프로젝트별 자연어 지침은 `.agent-harness/rules/PROJECT_GUIDE.md`에 둡니다.
- 프로젝트별 실행 설정은 `.agent-harness/harness.config.json`에 둡니다.

Claude, Gemini, OpenCode 전용 entrypoint나 adapter를 이 branch에 다시 추가하지 않습니다.

## 현재 적용된 규칙 확인

현재 Codex harness에 어떤 규칙이 문서화되어 있는지는 [`ACTIVE_RULES.ko.md`](ACTIVE_RULES.ko.md)에서 확인합니다.
