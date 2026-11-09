# Auto_BIM — Claude Code 지침

공통 규칙은 AGENTS.md에 있다(다른 AI 도구와 공유). 반드시 먼저 따른다.

@AGENTS.md

## Claude Code 전용

- 새 요청이 들어오면 먼저 `auto-bim-router` 스킬 기준으로 분류하고, 전문 작업은 `.claude/agents/`의 서브에이전트에 위임한다. 단순한 질문·한 파일 수정은 위임하지 않고 직접 처리한다(비용 규칙).
- 조사·검색(WebSearch/WebFetch)은 사전 허용 — 확인 질문 없이 바로 실행한다.
- 도면 원본을 외부로 보내는 도구 호출(온라인 변환기 업로드, 외부 API 전송)은 하지 않는다. 변환은 로컬 도구로만.
- Windows 환경: Python 3.14(`python`), Node 24. 셸은 PowerShell 5.1 기본 + Git Bash. PowerShell 스크립트에 한글이 들어가면 UTF-8 BOM으로 저장한다.
- 커밋 메시지에 큰따옴표가 들어가면 메시지 파일 + `git commit -F`를 쓴다.
