# prompt_backup/

- 루트: 사람(또는 `bim-docs`)이 정리한 세션 기록 `<YYYY-MM-DD>_<주제>.md` — 작업 항목, 바뀐 파일·이유, 결정, 커밋, 남은 일.
- `auto/`: `.claude/hooks/backup-session.cjs`가 매 턴 끝에 남기는 자동 백업(프롬프트+최종 응답). `auto/raw/`는 원본 transcript(git 제외).
- 재사용 가치가 높은 교훈은 `LLM_wiki/`로 승격한다. 원본을 wiki에 그대로 옮기지 않는다.
