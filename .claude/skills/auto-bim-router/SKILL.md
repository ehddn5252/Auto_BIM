---
name: auto-bim-router
description: Auto_BIM 저장소에 들어온 요청의 성격(조사/기획/결정/파싱/물량/단가/검증/문서)을 분류하고 bim-researcher, bim-planner, bim-ceo, cad-parser, quantity-takeoff, cost-estimator, estimate-verifier, bim-docs 중 어디로 위임할지 정한다. 요청이 여러 단계에 걸치거나 어디서부터 해야 할지 애매할 때, 또는 결정·승인이 필요한 지점을 만났을 때 가장 먼저 사용한다.
---

# Auto_BIM Router

node_trade의 router 구조(유연한 위임) + 5minuate_study의 역할 경계·질의 프로토콜을 합친 것. 메인 세션이 이 스킬을 따라 오케스트레이터 역할을 한다.

## 먼저 할 일

1. `LLM_wiki/repo-map.md`로 관련 위치를 확인한다.
2. 요청을 아래 표로 분류한다. 여러 개에 걸치면 파이프라인 순서(조사 → 기획 → 파싱 → 물량 → 단가 → 검증 → 문서)대로 나눈다.
3. **결정이 필요한 지점이면 사용자에게 묻지 말고 `bim-ceo`부터 호출한다.**

## 위임 기준

| 신호 | 담당 |
|---|---|
| "조사/찾아봐/어떤 라이브러리/단가 출처/표준품셈/경쟁 제품" | `bim-researcher` |
| "기획/MVP/범위/기능 정의/F-ID" | `bim-planner` |
| 승인·선택·우선순위·충돌 조정, Gate 1~3, "어느 쪽으로 할까" | `bim-ceo` |
| "도면 읽어/레이어/블록/DWG·DXF·IFC 파서" | `cad-parser` |
| "물량/수량산출/매핑/개수·길이·면적" | `quantity-takeoff` |
| "단가/견적서/내역서/일위대가/원가계산/얼마" | `cost-estimator` |
| 결과가 나온 직후, "검증/QA/맞아?" | `estimate-verifier` |
| "정리/wiki/세션 기록/인덱스" | `bim-docs` |
| 도면 한 세트를 끝까지 견적 | 스킬 `auto-bim-estimate` |
| "계속 조사해서 반영해줘/루프" | 스킬 `auto-bim-research-loop` |

단순 질문, 한 파일 수정, 이미 아는 사실 확인은 위임하지 않고 직접 처리한다(서브에이전트 남발 금지 — 비용 규칙).

## 질의 프로토콜 (서브에이전트 간 중계)

서브에이전트는 다른 서브에이전트를 직접 부를 수 없다. 서브에이전트 보고에 `질의 필요: <대상> — <질문>`이 있으면 메인 세션이 그 대상을 호출하고, 답을 원래 에이전트에 다시 넘겨(새 호출 또는 SendMessage) 작업을 이어가게 한다.

```
Agent({ subagent_type: "bim-ceo", description: "CEO 판정: <주제>",
  prompt: "<질의자> 가 <배경> 때문에 <결정 사항> 판단이 필요하다. 선택지: A/B(+근거 파일 경로). docs/ceo_prompt.md와 docs/decisions.md 기준으로 판정해 줘." })
```

CEO 판정 처리:
- `APPROVE`/`REJECT` → 그대로 진행/중단. 다시 사용자에게 묻지 않는다.
- `NEED_RESEARCH` → `bim-researcher` 호출 후 결과를 붙여 CEO에 재질의 (같은 주제 재질의는 최대 2회)
- `ESCALATE_TO_USER` → 사용자에게 질문 + 선택지 + CEO 추천안을 한 번에 묶어서 알린다. 답을 기다리는 동안 그 결정에 의존하지 않는 작업은 계속한다.

## 자기검증

- repo-map을 실제로 봤는가, 추측으로 분류하지 않았는가?
- 사용자에게 바로 물으려 한 질문이 있다면, 먼저 CEO에 물었는가?
- 결과물(물량·견적)이 나왔는데 `estimate-verifier`를 빼먹지 않았는가?
