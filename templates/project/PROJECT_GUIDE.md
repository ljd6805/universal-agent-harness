# Project Guide

이 파일은 Codex project harness에서 사용하는 프로젝트별 작업 지침 template입니다.

Codex base harness의 공통 규칙은 `.agent-harness/rules/CODEX.md`에 있고, 이 파일은 해당 프로젝트에만 적용되는 추가 지침을 담습니다.

## 프로젝트 개요

이 프로젝트가 무엇을 하는지 간단히 설명합니다.

예시:

```text
이 프로젝트는 여러 사용자가 공유 todo list를 만들고 권한에 따라 확인/수정할 수 있는 web service입니다.
```

## 작업 전 확인

Codex는 작업을 시작하기 전에 다음을 확인합니다.

- 관련 README, docs, architecture 문서를 먼저 읽습니다.
- 변경 대상 파일과 연관된 테스트를 확인합니다.
- git 상태를 확인하고, 기존 사용자 변경을 덮어쓰지 않습니다.
- 프로젝트별 보호 경로를 확인합니다.

## 프로젝트별 검증 명령

이 프로젝트에서 주로 사용하는 검증 명령을 적습니다.

| 목적 | 명령 |
| --- | --- |
| Build | `replace-with-build-command` |
| Test | `replace-with-test-command` |
| Lint | `replace-with-lint-command` |
| Typecheck | `replace-with-typecheck-command` |

명령이 없거나 아직 정해지지 않았다면 그 사실을 명확히 적습니다.

## 수정 주의 경로

Codex가 임의로 수정하거나 출력하면 안 되는 경로를 적습니다.

기본 보호 경로는 `.agent-harness/harness.config.json`의 `paths.protected`에 둡니다. 아래 예시 중 이 프로젝트에 실제로 필요한 항목만 config에 추가합니다.

예시:

- `.env`
- `secrets/`
- production 설정 파일
- migration 파일
- 자동 생성 파일

## 프로젝트별 예외

Codex 공통 규칙과 다르게 적용해야 하는 프로젝트별 예외를 적습니다.

예시:

- legacy code 영역은 테스트가 없을 수 있으므로 TDD guard는 warning으로만 처리합니다.
- 문서만 수정하는 경우 build/test는 생략할 수 있습니다.
- API contract 변경 시 frontend/backend 영향도를 함께 확인합니다.

## 완료 보고 규칙

작업 완료 시 Codex는 다음을 보고합니다.

- 변경 요약
- 실행한 검증 명령과 결과
- 실행하지 못한 검증과 이유
- 남은 위험 또는 후속 작업
