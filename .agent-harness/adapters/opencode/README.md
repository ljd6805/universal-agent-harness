# OpenCode 어댑터

OpenCode는 루트의 `opencode.json` 파일을 프로젝트 지침 진입점으로 사용합니다.

이 하네스에서 `opencode.json`은 다음 공통 규칙 파일을 가리킵니다.

```text
.agent-harness/rules/AGENT_GUIDE.md
```

## 어댑터 구조

| 파일            | 설명                                                               |
| --------------- | ------------------------------------------------------------------ |
| `opencode.json` | 정규(canonical) 설정. 루트 `opencode.json`과 항상 동일해야 합니다. |

루트 `opencode.json`은 이 어댑터 파일과 내용이 동일해야 하며,
`tests/test_harness.py`의 `test_opencode_config_matches_shared_adapter`가 동기화를 자동 검증합니다.

설정을 변경할 때는 이 어댑터 파일을 먼저 수정한 뒤 루트 `opencode.json`에도 동일하게 반영하세요.

OpenCode 전용 프로젝트 설정이 안정적으로 정리되고 여러 저장소에 공유할 가치가 있을 때만 이 디렉터리에 추가합니다.
