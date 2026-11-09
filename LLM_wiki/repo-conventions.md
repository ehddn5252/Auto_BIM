# Repo Conventions

## 문서 계층 (섞지 않는다)

1. **규칙**: `AGENTS.md`, `CLAUDE.md`, `LLM_wiki/operating-rules.md`
2. **정제 지식(RAG용)**: `LLM_wiki/` — 재사용 가치가 확인된 결정·용어·규칙만
3. **결정 기록**: `docs/decisions.md`(CEO), `docs/adr/`(아키텍처)
4. **작업 산출 원문**: `docs/research/`, `docs/qa/`, `docs/planning_document.md`, `docs/feature_definition.md`
5. **세션 기록**: `prompt_backup/<YYYY-MM-DD>_<주제>.md`(사람 정리), `prompt_backup/auto/`(hook 자동, raw는 git 제외)

> 철칙(5minuate_study rule.md 규칙 3): 세션 원본을 wiki에 통째로 넣지 않는다.

## 승격 기준 (하나 이상 만족 시 wiki로)

- 같은 설명을 두 번 이상 했다
- 견적·물량 오류 사고에서 나온 교훈 (거의 항상 승격)
- 여러 에이전트가 공통으로 알아야 하는 결정·용어
- 출처가 확인된 재사용 가능한 자료 위치

## 승격하지 않는 것

- 일회성 로그, 확인 안 된 추정, 해마다 바뀌는 수치 자체(→ `data/prices/`)

## 파일명 규칙

- 조사: `docs/research/<YYYY-MM-DD>_<주제-kebab>.md`
- 검증: `docs/qa/<대상>_<YYYY-MM-DD>.md`
- ADR: `docs/adr/ADR-<3자리 번호>-<주제-kebab>.md`
- 결정: `docs/decisions.md` 안에 `## D-<번호> <날짜> <제목>`
- 세션: `prompt_backup/<YYYY-MM-DD>_<주제>.md`
- 매핑: `data/mappings/<공종>_<대상>.yaml`, 단가: `data/prices/<출처>_<기준일>.csv|yaml`, 요율: `data/prices/rates_<연도>.yaml`
- 산출물: `output/<도면명>_<YYYYMMDD>/`

## 코드 규칙 (초안 — ADR로 확정)

- Python 패키지 `src/auto_bim/`, 테스트 `tests/<단계>/`, `python -m pytest`.
- 단계 간에는 JSON 계약(`estimation-pipeline.md`)으로만 통신 — 단계별로 독립 실행·검증 가능하게.
- 매핑·단가는 데이터 파일로, 코드에 하드코딩하지 않는다.
