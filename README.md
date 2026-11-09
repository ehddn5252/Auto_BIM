# Auto_BIM

CAD/BIM 도면(DWG·DXF·IFC)을 넣으면 그 도면에 필요한 자재·품목을 **실제 견적에 쓸 수 있는 수준**으로 뽑아내는 것을 목표로 하는 프로젝트.

```
도면 → 파싱(drawing.json) → 물량산출(takeoff.json) → 단가·원가(estimate.xlsx) → 독립 검증 → 확정
```

## 현재 상태 (2026-11-09)

- AI 작업 규칙·에이전트·지식 기반 세팅 완료. 코드는 아직 없음 — 첫 단계는 조사 → 기획 → 아키텍처 결정(CEO 게이트).

## AI 작업 구조

- 규칙: [AGENTS.md](AGENTS.md) (공통), [CLAUDE.md](CLAUDE.md) (Claude Code)
- 지식: [LLM_wiki/](LLM_wiki/README.md) — 운영 규칙, 파이프라인 계약, 도메인 용어, 출처
- 에이전트 (`.claude/agents/`): `bim-ceo`(결정) · `bim-researcher`(조사) · `bim-planner`(기획/F-ID) · `cad-parser` · `quantity-takeoff` · `cost-estimator` · `estimate-verifier`(독립 검증) · `bim-docs`
- 스킬 (`.claude/skills/`): `auto-bim-router`(분류·위임) · `auto-bim-estimate`(도면 1세트 end-to-end) · `auto-bim-research-loop`(자율 조사 루프)
- 결정: [docs/ceo_prompt.md](docs/ceo_prompt.md), [docs/decisions.md](docs/decisions.md)

## 핵심 원칙

1. 모든 수량은 도면 근거(handle), 모든 단가는 출처·기준일로 추적 가능
2. 모르면 `UNMAPPED`/`UNPRICED`로 표시 — 숫자를 지어내지 않음
3. 고객 도면은 로컬에서만 처리(`data/drawings/private/`, git 제외)
4. 결정은 CEO 에이전트 먼저, CEO가 못 하는 것만 사용자에게
