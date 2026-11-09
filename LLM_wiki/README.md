# Auto_BIM LLM Wiki

AI 에이전트가 작업 전에 읽는 **정제된** 지식 기반. 세션 원본(`prompt_backup/`)이나 조사 원문(`docs/research/`)을 통째로 옮기지 않고, 재사용 가치가 확인된 결정·규칙·용어만 담는다.

Auto_BIM 목표: CAD/BIM 도면 → 필요한 자재·품목을 실제 견적 수준으로 산출. 견적 숫자가 실제 돈에 쓰인다는 전제로 쓰였다.

## 문서

| 문서 | 내용 | 언제 읽나 |
|---|---|---|
| [repo-map.md](repo-map.md) | 폴더 역할, 질문 유형별 탐색 순서 | 모든 작업 시작 시 |
| [operating-rules.md](operating-rules.md) | **견적 정확도·추적성·보안 규칙** (번호 고정) | 물량·단가·견적 작업 전 |
| [agent-roles.md](agent-roles.md) | 에이전트 권한 매트릭스, 질의 프로토콜, CEO 게이트 | 권한 밖 판단이 필요할 때 |
| [estimation-pipeline.md](estimation-pipeline.md) | 파이프라인 단계별 입출력 계약(JSON) | 파서·물량·단가 구현/실행 시 |
| [domain-terms.md](domain-terms.md) | CAD/BIM·적산·원가계산 용어 | 도메인 용어가 나올 때 |
| [data-sources.md](data-sources.md) | 확인된 단가·기준·포맷 자료 출처 | 단가·기준 조사 전(중복 방지) |
| [repo-conventions.md](repo-conventions.md) | 문서 계층, 승격 기준, 파일명 규칙 | 문서 추가 시 |
| [incident-log.md](incident-log.md) | 견적·물량 오류 사고 기록 | 규칙의 근거 확인 시 |

## 관련 문서 (wiki 밖)

- `../AGENTS.md` — 공통 AI 규칙(최상위)
- `../docs/ceo_prompt.md` — 비전·제약·비목표 (CEO 소유)
- `../docs/decisions.md` — CEO 결정 로그
- `../docs/planning_document.md`, `../docs/feature_definition.md` — 기획·기능 정의 (planner 소유, 미작성 시 생성 예정)
- `../docs/adr/` — 아키텍처 결정 기록
- `../docs/research/` — 조사 원문
- `../docs/qa/` — 검증 리포트

## 운영 원칙

- 짧고 검색 가능하게. 사실·규칙·절차를 분리해서 쓴다.
- 해마다 바뀌는 수치(노임단가, 제경비 요율 등)는 wiki에 숫자로 박지 않고 `data/prices/`에 출처·기준일과 함께 둔다. wiki에는 "어디서 확인하는지"만.
- 자주 바뀌는 내용은 날짜와 배경을 같이 쓴다.
- 문서를 추가·변경하면 이 표를 갱신한다.
