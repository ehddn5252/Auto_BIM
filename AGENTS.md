# AGENTS.md

## 목적

Auto_BIM은 **CAD/BIM 도면(DWG·DXF·IFC 등)을 넣으면, 그 도면에 필요한 자재·품목을 실제 견적에 쓸 수 있는 수준으로 뽑아내는 것**을 최종 목표로 한다.

```
도면 입력 → 파싱(엔티티·레이어·블록·속성) → 물량산출(개수·길이·면적·체적) → 품목/규격 매핑 → 단가 적용 → 견적서(내역서) 출력
```

AI 에이전트는 일반적인 코드 작업 원칙에 더해 **"이 숫자가 실제 돈이 오가는 견적서에 들어간다"는 전제**를 항상 깔고 작업한다. 틀린 숫자보다 "모른다/확인 필요"가 낫다.

## 기본 원칙

- 작업 전 `LLM_wiki/README.md` → `LLM_wiki/repo-map.md`를 읽고 구조를 파악한다. 견적·물량 관련이면 `LLM_wiki/operating-rules.md`와 `LLM_wiki/domain-terms.md`를 먼저 확인한다.
- **추적성(traceability)이 최우선 규칙이다.** 견적서의 모든 수량은 도면 근거(파일·레이어·블록·엔티티 handle)로, 모든 단가는 출처(기관·자료명·기준일·URL)로 되돌아갈 수 있어야 한다. 근거 없는 숫자는 만들지 않는다.
- **단가를 지어내지 않는다.** 단가를 못 찾으면 `UNPRICED`(단가 미확인)로 표시하고 견적서에 그대로 남긴다. "대략 이 정도일 것" 같은 추정 단가는 사용자가 명시적으로 요청한 경우에만, `ESTIMATED` 표시와 근거를 붙여 쓴다.
- **단위를 항상 명시한다.** 도면 단위(`$INSUNITS`, 축척)를 먼저 확정하고, mm/m/m²/m³/EA/식 중 무엇인지 모든 수량에 붙인다.
- 코드 변경은 가장 작은 범위로 하고, 관련 테스트를 즉시 돌린다(`python -m pytest`). 샘플 도면 기준 회귀(골든 결과 비교)가 있으면 같이 돌린다.
- 불확실하면 추정 대신 도면·코드·공식 자료에서 근거를 찾고 기록한다.
- **생성과 검증을 분리한다.** 견적·물량을 만든 에이전트가 자기 결과를 최종 승인하지 않는다 — `estimate-verifier`가 독립적으로 검증한다(`LLM_wiki/agent-roles.md`).

## 사전 허용 범위 (반복 확인하지 말고 진행 후 보고)

사용자는 다음을 사전 허용했다:

- **조사/검색은 무조건 허용**: 웹 검색(WebSearch), 공개 웹 페이지·문서 조회(WebFetch), 공개 표준·법령·고시·가격 공표 자료, 오픈소스 라이브러리 문서·저장소 조회. 묻지 말고 바로 찾는다.
- 로컬 파일 조회(이 저장소와 참고 저장소 `5minuate_study`, `node_trade` 포함) — 항상 허용.
- 이 저장소 안의 코드·문서 작성/수정, 테스트 실행, 샘플 도면 분석.

이 포괄 허용에 **포함되지 않는 것**(별도 확인 필요):

- 유료 결제, 유료 가격정보 서비스 가입·구독, 계정 생성, 인증정보 입력·사용
- **고객/실제 도면을 외부 서비스(온라인 변환기, 외부 API, 공개 저장소)에 업로드** — 도면은 기밀로 취급한다
- 외부로 데이터를 쓰거나 게시(이슈·PR 코멘트·메일 등), `git push`
- 파괴적·되돌리기 어려운 변경(대량 삭제, 히스토리 재작성)
- 최종 견적서를 "확정본"으로 내보내는 것 — `bim-ceo` Gate 3 통과 후에만

## 역할 분담

전문 서브에이전트(`.claude/agents/`)와 워크플로 스킬(`.claude/skills/`)로 구현돼 있다. 상세 권한 매트릭스는 `LLM_wiki/agent-roles.md`.

| 역할 | 정의 | 소유 범위 |
|---|---|---|
| Router | skill `auto-bim-router` | 요청 분류·위임 (메인 세션이 수행) |
| CEO | agent `bim-ceo` | 최종 의사결정(Gate 1~3, 범위·우선순위·충돌 조정) → `docs/ceo_prompt.md`, `docs/decisions.md` |
| Researcher | agent `bim-researcher` | 외부 조사: 포맷 스펙, 라이브러리, 표준품셈·단가 출처, 경쟁 제품 → `docs/research/` |
| Planner/FO | agent `bim-planner` | 기획 문서·기능 정의서(F-ID) → `docs/planning_document.md`, `docs/feature_definition.md` |
| CAD Parser | agent `cad-parser` | 도면 읽기·정규화 → `src/auto_bim/parsing/` |
| Quantity Takeoff | agent `quantity-takeoff` | 물량산출·레이어/블록→품목 매핑 → `src/auto_bim/takeoff/`, `data/mappings/` |
| Cost Estimator | agent `cost-estimator` | 품목·규격·단가·할증·원가계산 → `src/auto_bim/pricing/`, `data/prices/` |
| Verifier | agent `estimate-verifier` | 독립 검증(생성 결과 재계산·교차검증), 코드 수정 없음 → `docs/qa/` |
| Docs | agent `bim-docs` | `LLM_wiki/`, `prompt_backup/` 정리·승격·인덱싱 |

워크플로 스킬:
- `auto-bim-estimate` — 도면 한 장(세트)에 대해 파싱→물량→단가→검증→견적서를 끝까지 돌리는 절차
- `auto-bim-research-loop` — 조사→기획 반영을 자율로 반복하는 루프(사이클 상한 있음)

## 작업 흐름

1. 요청을 읽고 성격을 분류한다(`auto-bim-router`): 조사 / 기획 / 파싱 / 물량 / 단가 / 검증 / 문서.
2. `LLM_wiki/repo-map.md`, 관련 wiki를 확인한다.
3. 권한 밖 판단이 필요하면 같은 컨텍스트에서 관점만 바꾸지 말고, 해당 역할의 서브에이전트를 실제로 호출해 판단받는다(`LLM_wiki/agent-roles.md`의 질의 프로토콜). 최종 결정은 `bim-ceo`, CEO가 못 하면 사용자.
4. 견적·물량 결과를 냈으면 `estimate-verifier`로 독립 검증한다.
5. 코드를 바꿨으면 커밋 전에 테스트(최소 `pytest`)를 돌린다.
6. 결과를 문서·코드·근거 형태로 남기고, 새 지식은 `LLM_wiki/`에 승격하며 `LLM_wiki/README.md` 인덱스를 갱신한다.

## 결정 게이트 — CEO 에이전트 우선 (사용자에게 직접 묻지 않는다)

사용자 지시(2026-11-09): **결정이 필요하면 사용자에게 묻지 말고 `bim-ceo` 에이전트에게 먼저 묻는다. CEO가 결정 못 하는 것만 사용자에게 알린다.** 이 프로젝트 안의 파일 작성·수정은 항상 허용이며 확인을 묻지 않는다.

| 게이트 | 시점 | 1차 결정 |
|---|---|---|
| Gate 1 기획 승인 | `docs/planning_document.md`·`feature_definition.md` 확정 시 | `bim-ceo` |
| Gate 2 아키텍처 승인 | 기술 스택·입력 포맷 범위·데이터 출처 확정(`docs/adr/`) 후 개발 착수 전 | `bim-ceo` |
| Gate 3 견적서 확정 | 견적서를 확정본으로 내보내기 전(검증 통과 + 기준 충족) | `bim-ceo` |

- CEO 판정이 `ESCALATE_TO_USER`일 때만 사용자에게 알린다 — 질문 + 선택지 + CEO 추천안을 묶어서 한 번에.
- CEO가 결정할 수 없는 것(정의: `.claude/agents/bim-ceo.md`): 돈이 나가는 것, 계정·인증정보, 고객 도면 외부 업로드·외부 게시·`git push`, 사용자만 아는 사실, 사용자의 기존 지시를 뒤집는 것.
- 모든 CEO 결정은 `docs/decisions.md`에 기록된다.

## 저장소별 규칙

- 참고 저장소: `C:\git_repository\5minuate_study`(역할 기반 기획 파이프라인·`docs/rule.md`), `C:\git_repository\node_trade`(`AGENTS.md`+`LLM_wiki/` 구조·router 위임). 패턴을 가져올 때 원문을 확인한다. 참고 저장소 파일은 수정하지 않는다.
- 비용 규칙: 서브에이전트 호출은 실제로 역할 경계를 넘는 판단·전문 작업이 필요할 때만 한다. 자율 루프는 반드시 사이클 상한과 no-progress 중단 조건을 둔다(같은 실패 3회 → 멈추고 보고).
- 세션 작업이 끝나면 `.claude/hooks/backup-session.cjs`가 `prompt_backup/auto/`에 자동 백업한다. 재사용 가치가 높은 교훈은 사람이(또는 `bim-docs`가) `LLM_wiki/`로 승격한다. 세션 원본과 정제 지식을 섞지 않는다.
- 견적·물량 관련 오류(틀린 수량·단가가 결과물에 나간 경우)는 `LLM_wiki/incident-log.md`에 기록하고, 교훈은 `LLM_wiki/operating-rules.md`에 규칙으로 올린다.

## 기대 결과

AI 작업은 빠르게 찾고, 근거를 남기고, 모르는 것은 모른다고 표시하는 방식으로 동작해야 한다. 이 저장소에서는 **견적 숫자의 정확성과 추적 가능성이 곧 신뢰도다.**
