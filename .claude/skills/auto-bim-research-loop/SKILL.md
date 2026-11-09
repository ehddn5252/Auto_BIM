---
name: auto-bim-research-loop
description: Auto_BIM을 위해 인터넷 조사 → 기획/결정 반영 → (승인되면) 구현까지를 자율로 반복하는 루프. "계속 조사해서 반영해줘", "리서치 루프 돌려", "자율로 개선해줘", /loop로 이 프로젝트를 계속 발전시키라고 할 때 사용한다. 사이클 상한과 중단 조건이 있다.
---

# Auto_BIM Research Loop

5minuate_study `study-research-loop`를 옮긴 것. 차이: 자문자답 대신 **실제 분리된 에이전트**(researcher → planner → ceo → 개발 계열 → verifier)를 거친다(`LLM_wiki/agent-roles.md`).

## 매 사이클 절차

1. **현황 파악** (메인 세션, 직접): `docs/decisions.md` 최근 항목, `docs/feature_definition.md`의 미구현 F-ID, `docs/research/` 최근 파일, 이 파일 하단 "기록"·"보류".
2. **조사 주제 1개 선정**: 현재 병목 기준(예: DWG 읽기 수단 미정 → 그걸 조사). 이미 조사한 주제의 변형은 피한다.
3. **조사** → `bim-researcher` (산출: `docs/research/<날짜>_<주제>.md`)
4. **반영안** → `bim-planner` (기획/F-ID 변경안) 또는 개발 계열 ADR 초안
5. **결정** → `bim-ceo` 판정. ESCALATE면 사용자 알림 목록에 쌓고 다음 사이클로(기다리지 않음).
6. **구현** (APPROVE이고 구현 대상이면) → 담당 개발 에이전트, 이어서 `estimate-verifier`
7. **기록**: 아래 "기록"에 한 줄(날짜, 주제, 판정, 산출물 경로). 재사용 지식은 `bim-docs`에 승격 요청.

## 스코프 가드레일

- 한 사이클 = 주제 1개, 구현은 F-ID 1개 이하.
- 비목표(`docs/ceo_prompt.md`)에 해당하는 아이디어는 조사만 기록하고 반영하지 않는다.
- 돈·계정·외부 업로드가 필요한 아이디어는 반영하지 않고 사용자 알림 목록으로.

## 루프 지속/중단

- 상한: 한 번 실행에 **최대 5사이클**(사용자가 따로 정하면 그 값).
- 중단: 연속 2사이클 판정이 REJECT/NEED_RESEARCH만 나옴, 같은 실패 3회, 조사할 병목이 없음.
- 끝나면 사용자에게: 사이클별 한 줄 요약 + 쌓인 ESCALATE 질문(선택지·CEO 추천안 포함).

## 기록 (이 루프가 반영한 것)

- (아직 없음)

## 보류 (다음 사이클 참고, 바로 만들지 말 것)

- (아직 없음)
