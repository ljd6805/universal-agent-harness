# 현재 적용된 규칙 (Active Rules)

이 문서는 이 base harness에 **지금 실제로 켜져 있는** permission, hook, 작업 규칙을 한눈에 확인하기 위한 레퍼런스입니다.

`HARNESS_GUIDE.ko.md`가 "왜 이렇게 설계했는가"를 설명하는 문서라면, 이 문서는 "지금 무엇이 켜져 있는가"만 빠르게 보여주는 것이 목적입니다.

> 이 문서의 YAML 블록은 `.claude/settings.json` / `.agent-harness/adapters/*/settings.json` 및 `AGENT_GUIDE.md`의 실제 내용과 `tests/test_harness.py`로 동기화 검증됩니다.
> **harness 설정을 바꿀 때는 이 문서의 YAML 블록도 함께 수정하세요.** 어긋나면 테스트가 실패합니다.

## 스펙 (기계가 읽는 부분)

```yaml
version: 1

permissions:
  allow:
    - rule: "Bash(git *)"
      description: "git 명령 실행 허용 — 저장소 상태 확인, 커밋 이력 조회 등"
    - rule: "Bash(ls *)"
      description: "디렉터리 목록 조회 허용"
    - rule: "Bash(find *)"
      description: "파일 탐색 허용"
    - rule: "Bash(grep *)"
      description: "텍스트 검색 허용"
    - rule: "Read"
      description: "파일 읽기 허용"
    - rule: "Edit"
      description: "기존 파일 수정 허용"
    - rule: "Write"
      description: "새 파일 생성/덮어쓰기 허용"

hooks:
  PostToolUse:
    - matcher: "Write|Edit|MultiEdit"
      script: ".agent-harness/hooks/format_changed_file.py"
      purpose: "변경된 파일을 자동으로 포맷팅한다"
    - matcher: "Write|Edit|MultiEdit"
      script: ".agent-harness/hooks/run_tests.py"
      purpose: "변경 사항과 관련된 테스트를 자동으로 실행한다"
    - matcher: "Write|Edit|MultiEdit"
      script: ".agent-harness/hooks/tdd_guard.py"
      purpose: "프로덕션 코드 변경에 대응하는 테스트가 있는지 확인하고 없으면 경고한다"
  Stop:
    - matcher: null
      script: null
      purpose: "세션 종료 시 하네스 종료 메시지를 출력한다 (자동화 스크립트 없음, 고정 echo)"

workflow_rules:
  - id: explore-before-edit
    summary: "수정 전에 관련 파일을 읽고 git 상태와 기존 사용자 변경을 확인한다"
    enforced_by: "자연어 지침 (자동 검증 없음)"
    source: ".agent-harness/rules/AGENT_GUIDE.md#1-수정-전-먼저-탐색한다"
  - id: check-project-guide
    summary: "PROJECT_GUIDE.md / harness.config.json이 있으면 공통 지침과 함께 따른다"
    enforced_by: "자연어 지침 (자동 검증 없음)"
    source: ".agent-harness/rules/AGENT_GUIDE.md#2-프로젝트별-지침을-확인한다"
  - id: tdd-default
    summary: "프로덕션 코드는 실패하는 테스트 작성 -> 구현을 기본값으로 한다 (문서/하네스 설정/명시적 스캐폴딩은 예외)"
    enforced_by: "tdd_guard.py 훅 (경고만 출력, 차단 아님)"
    source: ".agent-harness/rules/AGENT_GUIDE.md#3-기본값은-tdd다"
  - id: parallelization-judgement
    summary: "독립적인 파일/모듈/원인일 때만 병렬화하고, 강하게 결합된 작업은 단일 흐름으로 진행한다"
    enforced_by: "자연어 지침 (자동 검증 없음)"
    source: ".agent-harness/rules/AGENT_GUIDE.md#4-병렬화-가능성을-판단한다"
  - id: verify-before-done
    summary: "완료 보고 전 관련 테스트/검사를 실행하고, 불가능하면 이유와 다음 실행 명령을 명시한다"
    enforced_by: "run_tests.py 훅 + 자연어 지침"
    source: ".agent-harness/rules/AGENT_GUIDE.md#5-완료-전-검증한다"
```

## 설명 (사람이 읽는 부분)

### Permissions

이 harness는 기본적으로 **읽기/탐색 + 코드 수정**을 허용하는 비교적 개방적인 권한 셋을 가지고 있습니다. `git`, `ls`, `find`, `grep`은 임의 인자로 실행을 허용하지만, 그 외의 임의 셸 명령(`Bash(*)`)은 허용 목록에 없으므로 도구가 별도로 묻습니다.

> 주의: 현재 `deny` 목록은 비어 있습니다. 민감 경로(`.env`, 시크릿 등)에 대한 명시적 차단이 필요하다면 `permissions.deny`를 추가하고 이 문서에도 반영해야 합니다.

### Hooks

`Write|Edit|MultiEdit` 직후에 포맷팅 → 테스트 실행 → TDD 점검이 순서대로 실행됩니다. 세 훅 모두 **차단(block)이 아니라 안내/경고** 목적입니다 — 즉, 세션을 멈추지 않고 메시지만 보여줍니다. `Stop` 훅은 별도 스크립트 없이 고정 메시지를 출력하는 가장 단순한 형태입니다.

### Workflow rules

`AGENT_GUIDE.md`에 정의된 6개 핵심 규칙 중, 자동화로 일부 보강되는 것은 `tdd-default`(→ `tdd_guard.py`)와 `verify-before-done`(→ `run_tests.py`)이며, 나머지는 현재 **자연어 지침에만 의존**합니다. 이 표의 `enforced_by` 값은 "이 규칙이 실제로 강제되는지, 아니면 안내 수준인지"를 빠르게 파악하는 용도입니다.

## 갱신 절차

1. `.claude/settings.json` (또는 `.agent-harness/adapters/*/settings.json`, `AGENT_GUIDE.md`)을 변경한다.
2. 위 YAML 블록의 해당 항목을 함께 수정한다 (추가/삭제/설명 변경).
3. `python3 -m unittest tests/test_harness.py`를 실행해 동기화 테스트를 통과시킨다.

반대로, "harness를 어떻게 바꾸고 싶은가"를 먼저 정할 때도 이 문서의 YAML 블록을 먼저 합의된 형태로 수정한 뒤, 그 내용을 스펙 삼아 실제 설정 파일을 수정하는 순서를 권장합니다.
