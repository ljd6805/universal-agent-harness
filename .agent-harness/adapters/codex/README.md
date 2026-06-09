# Codex 어댑터

이 디렉터리는 Codex 전용 harness에서 Codex 관련 adapter 문서를 보관합니다.

## 현재 연결 방식

Codex의 루트 진입점은 `AGENTS.md`입니다.

```text
AGENTS.md -> .agent-harness/rules/CODEX.md
```

`AGENTS.md`는 짧고 안정적인 entrypoint로 유지하고, 실제 작업 규칙은 `CODEX.md`에 둡니다.

## 현재 자동화 상태

현재 이 adapter는 Codex native auto-hook 설정이 있다고 주장하지 않습니다.

대신 다음 script를 Codex 작업 검증에 사용할 수 있도록 유지합니다.

```text
.agent-harness/hooks/format_changed_file.py
.agent-harness/hooks/run_tests.py
.agent-harness/hooks/tdd_guard.py
```

Codex가 project-level hook 또는 lifecycle 설정을 안정적으로 제공하면, 그때 이 디렉터리에 runtime config나 wrapper script를 추가합니다.

## 유지 원칙

- Codex 관련 설정과 문서만 이 디렉터리에 둡니다.
- Claude, Gemini, OpenCode 설정은 이 branch에 추가하지 않습니다.
- 실제로 자동 실행되지 않는 기능은 자동화된 것처럼 문서화하지 않습니다.
