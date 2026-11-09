# Repo Map

> 2026-11-09 기준. 정식 코드(`src/`)는 없고 `spikes/`에 조사용 스파이크만 있다 — 아래 `src/`·`tests/` 구조는 계획이며, Gate 2 ADR 승인 후 생성 시 이 문서를 갱신한다(D-012).

## 폴더 역할

| 경로 | 역할 | 소유 에이전트 |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md` | AI 공통 규칙 / Claude 전용 지침 | 사용자 (+ `bim-docs` 정리) |
| `.claude/agents/` | 서브에이전트 8종 정의 | — |
| `.claude/skills/` | 워크플로 스킬(router, estimate, research-loop) | — |
| `.claude/hooks/backup-session.cjs` | 세션 종료 시 `prompt_backup/auto/` 자동 백업 | — |
| `LLM_wiki/` | 정제 지식 | `bim-docs` |
| `docs/ceo_prompt.md`, `docs/decisions.md` | 비전·제약 / 결정 로그 | `bim-ceo` |
| `docs/planning_document.md` | 기획 문서(Gate 1 조건부 승인, D-008). 대상 사용자·저니·성공 지표·사용자 질의 | `bim-planner` |
| `docs/feature_definition.md` | 기능 정의서 v0.2: F-ID, 공통 규칙 C-1~C-8, 함정 T-01~T-21, 0절 상태 어휘·경고 코드·단가 출처 유형 표 | `bim-planner` |
| `spikes/` | ezdxf 스파이크 전용 조사용 코드(D-012). **정식 코드 아님**, `src/` 밖, ezdxf 버전 고정, 입력은 합성·예제 DXF만. 결과는 Gate 2 ADR 입력 | `cad-parser` |
| `docs/adr/` | 아키텍처 결정 기록 (ADR 초안 → CEO 판정) | 개발 계열 에이전트 |
| `docs/research/` | 조사 원문 | `bim-researcher` |
| `docs/qa/` | 검증 리포트 | `estimate-verifier` |
| `src/auto_bim/parsing/` (계획) | 도면 → `drawing.json` | `cad-parser` |
| `src/auto_bim/takeoff/` (계획) | `drawing.json` → `takeoff.json` | `quantity-takeoff` |
| `src/auto_bim/pricing/` (계획) | `takeoff.json` → `estimate.json/xlsx` | `cost-estimator` |
| `tests/<단계>/` (계획) | 단계별 테스트 | 각 단계 소유자 |
| `data/drawings/samples/` | 공개·자작 샘플 도면 (git 포함) | — |
| `data/drawings/private/` | 고객·실제 도면 (**git 제외, 외부 반출 금지**) | — |
| `data/mappings/` | 레이어/블록/속성 → 품목 매핑 규칙(yaml) | `quantity-takeoff` |
| `data/prices/` | 단가표·요율(출처·기준일 필수) | `cost-estimator` |
| `data/ground_truth/` | 사람이 만든 정답 내역서(정확도 측정용) | — |
| `output/` | 실행 산출물 (`output/private/`는 git 제외) | — |
| `prompt_backup/` | 사람이 정리한 세션 기록 / `auto/`는 hook 자동 백업 | `bim-docs` |

## 질문 유형별 탐색 순서

- **도면 읽기·포맷 문제** → `domain-terms.md`(CAD) → `docs/adr/` → `src/auto_bim/parsing/` → `docs/research/`
- **수량이 이상함** → `operating-rules.md` → `data/mappings/` → `src/auto_bim/takeoff/` → `docs/qa/` → `incident-log.md`
- **단가·금액** → `data-sources.md` → `data/prices/` → `src/auto_bim/pricing/`
- **무엇을 만들지/범위** → `docs/ceo_prompt.md` → `docs/decisions.md` → `docs/planning_document.md`
- **예전에 비슷한 일** → `prompt_backup/` 파일명(날짜_주제) → `incident-log.md`

## 참고 저장소 (읽기 전용)

- `C:\git_repository\5minuate_study` — `docs/rule.md`(CEO 오케스트레이션 규칙), `docs/agent_permissions.md`(권한 매트릭스)
- `C:\git_repository\node_trade` — `AGENTS.md`, `LLM_wiki/`(operating-rules·incident-log 구조), router 위임 스킬
