---
name: auto-bim-estimate
description: Auto_BIM에서 도면 한 장(또는 한 세트)을 받아 파싱 → 물량산출 → 단가 적용 → 독립 검증 → 견적서 출력까지 end-to-end로 실행하는 절차. 사용자가 도면 파일을 주며 "견적 뽑아줘", "이 도면 자재 뽑아줘", "물량이랑 금액 계산해줘"라고 할 때 사용한다.
---

# Auto_BIM Estimate (end-to-end)

파이프라인 계약은 `LLM_wiki/estimation-pipeline.md`. 각 단계는 담당 서브에이전트에 위임하고, 메인 세션은 단계 간 산출물 전달과 게이트만 맡는다.

## 0. 준비

- 입력 도면 경로와 성격을 확인한다: 공개/자작 샘플 → `data/drawings/samples/`, 고객/실제 도면 → `data/drawings/private/`(git 제외, 외부 업로드 금지).
- 출력 폴더: `output/<도면명>_<YYYYMMDD>/` (고객 도면이면 `output/private/...`).
- 아직 코드가 없는 단계(초기)라면, 각 에이전트가 스크립트/라이브러리로 직접 분석해 같은 형식의 JSON을 만든다 — 그 과정에서 반복되는 로직은 `src/auto_bim/`로 옮길 후보로 기록한다.
- 견적 방식(공공 원가계산/민간 실행견적)·공종 범위가 `docs/decisions.md`에 없으면 `bim-ceo`에 먼저 질의한다.

## 1. 파싱 → `cad-parser`

산출: `drawing.json` (단위, 레이어, 블록, 엔티티+handle, unsupported 집계)
- 단위가 unknown이면 여기서 멈추고 도면 내 근거(치수 텍스트, 축척 표기)를 더 찾는다. 그래도 불명이면 `bim-ceo`에 질의(가정 단위로 진행해도 되는지).

## 2. 물량산출 → `quantity-takeoff`

산출: `takeoff.json` (품목·규격·단위·순수량·근거 handle·산출식, UNMAPPED 목록)
- UNMAPPED 비중이 크면 매핑 규칙 추가 후보를 정리해 보고에 넣는다.

## 3. 단가·원가 → `cost-estimator`

산출: `estimate.json`, `estimate.xlsx` (내역서 + 원가계산서 해당 시)
- UNPRICED/ESTIMATED/STALE 분리 합계 필수.

## 4. 독립 검증 → `estimate-verifier`

- 7점 미만 반려 → 지적된 단계의 담당 에이전트에 반려 사유를 넘겨 수정 → 재검증. **같은 단계 반려 3회면 멈추고 보고**(no-progress).
- 검증 리포트: `docs/qa/<도면명>_<YYYY-MM-DD>.md`

## 5. 확정 → `bim-ceo` (Gate 3)

- 검증 리포트 + 요약(총액, UNPRICED 비율, 주요 가정)을 넘겨 확정본 여부 판정.
- `APPROVE`면 `estimate.xlsx`를 확정본으로 표시(파일명 `_final`), 아니면 `_draft` 유지.

## 6. 보고

사용자에게: 총액(확정/미확정 분리), 품목 수, UNMAPPED·UNPRICED 개수와 대표 예, 주요 가정, 검증 점수, 산출물 경로. 이어서 `bim-docs`가 새 매핑·단가 출처·교훈을 wiki로 승격할지 판단한다.

## 자기검증

- 단계마다 산출물 파일이 실제로 생겼는가?
- 검증을 생성 에이전트와 다른 에이전트(verifier)가 했는가?
- 확정본 여부를 CEO 판정 없이 정하지 않았는가?
