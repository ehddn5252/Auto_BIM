# Agent Roles — 권한 매트릭스와 질의 프로토콜

> 5minuate_study `docs/agent_permissions.md` + node_trade `LLM_wiki/05_agent_roles.md`를 Auto_BIM에 맞게 합친 것.
> 원칙: 권한 밖 판단은 같은 컨텍스트에서 관점만 바꿔 자문자답하지 않는다(자기 결과 자기 평가 금지). 실제로 분리된 서브에이전트를 호출한다.

## 구조

```
                  사용자 (CEO가 결정 못 하는 것만)
                     ▲ ESCALATE_TO_USER
                  bim-ceo  ── 결정 로그 docs/decisions.md
                     ▲ 질의 (Gate 1~3, 충돌 조정)
메인 세션 (auto-bim-router 스킬로 오케스트레이션)
   ├─ bim-researcher   조사
   ├─ bim-planner      기획/F-ID
   ├─ cad-parser       ─┐
   ├─ quantity-takeoff  ├ 파이프라인(생성)
   ├─ cost-estimator   ─┘
   ├─ estimate-verifier 독립 검증(평가)
   └─ bim-docs         문서·wiki
```

서브에이전트는 다른 서브에이전트를 직접 호출할 수 없다 → 보고에 `질의 필요: <대상> — <질문>`을 적으면 메인 세션이 중계한다.

## 권한 매트릭스

| 역할 | 모델 | 소유 파일/결정 | 자가 승인 범위 | 벗어나면 질의 |
|---|---|---|---|---|
| `bim-ceo` | opus | `docs/ceo_prompt.md`, `docs/decisions.md` | Gate 1~3, 범위·우선순위, 충돌 조정 | 돈·계정·외부 업로드/게시·사용자만 아는 사실 → **사용자** |
| `bim-researcher` | sonnet | `docs/research/`, `data-sources.md`(추가) | 조사·정리(검색 사전 허용) | 결정 → planner/CEO |
| `bim-planner` | opus | `docs/planning_document.md`, `docs/feature_definition.md` | 페르소나·저니·범위안·F-ID | 기술 결정 → 개발 계열 ADR → CEO / 비전 변경 → CEO |
| `cad-parser` | sonnet | `src/auto_bim/parsing/`, 파싱 ADR 초안 | 승인된 F-ID 범위 내 구현 | 라이브러리·포맷 범위 → CEO(Gate 2) / 새 기능 → planner |
| `quantity-takeoff` | sonnet | `src/auto_bim/takeoff/`, `data/mappings/` | 매핑 규칙 추가, 산출 로직 | 품목 체계 → estimator, 충돌 → CEO / 파싱 이상 → parser |
| `cost-estimator` | opus | `src/auto_bim/pricing/`, `data/prices/` | 출처 있는 단가 적용, 원가계산 | 견적 방식 미정·유료 자료 → CEO / 조사 → researcher |
| `estimate-verifier` | opus | `docs/qa/` | 판정·반려 (수정 권한 없음) | 수정은 해당 생성 에이전트로 반환 |
| `bim-docs` | sonnet | `LLM_wiki/`, `prompt_backup/` | 승격·인덱싱 | 코드 → 해당 개발 에이전트 |

## 질의 응답 처리

- **승인 + 산출물**: 반영하고 원래 작업을 이어간다. 질의 대상의 자기검증을 거쳤으므로 다시 자문자답 검증하지 않는다.
- **반려**: 사유를 기록하고 그 작업은 하지 않는다(우회 금지).
- **질의 대상도 권한 밖**: 표를 따라 상위로(최종 CEO). CEO가 ESCALATE면 사용자에게.
- 질의는 실제 경계를 넘을 때만 — 승인된 범위 안의 세부 구현까지 매번 묻지 않는다.

## 기본 흐름

1. Router가 분류 → 2. 필요시 researcher가 근거 수집 → 3. planner가 기능화 → 4. CEO 게이트 → 5. 생성 에이전트 구현/실행 → 6. verifier 검증 → 7. docs 승격.
고정 순차가 아니라 router가 필요한 단계만 고른다(node_trade 방식). 새 전문 영역이 필요하면 에이전트 파일 하나 + router 표 한 줄 추가로 확장한다.
