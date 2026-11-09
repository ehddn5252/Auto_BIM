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

- 2026-11-09 실행 1 (5사이클, 독립 조사 3건 병렬)
  - C1 도면 입력 수단 → D-002 APPROVE(DXF+ezdxf 코어, DWG는 사용자 DXF 저장 기본) — `docs/research/2026-11-09_drawing-input-tools.md`
  - C2 적산 기준·단가 출처 → D-005~D-007 APPROVE(무료 CSV 스냅샷, CAK 노임, 제비율 기본값 없음, MVP=수량산출서+직접공사비 내역서) — `docs/research/2026-11-09_cost-standards-and-price-sources.md`
  - C3 샘플·공종·경쟁 → D-003(전기 기구 개수, 잠정), D-004(합성 DXF) — `docs/research/2026-11-09_samples-trade-scope-competitors.md`
  - C4 기획·F-ID → Gate 1 조건부 승인 D-008~D-012, 후속 D-013~D-016 — `docs/planning_document.md`, `docs/feature_definition.md` v0.2
  - C5 ezdxf 스파이크 + 합성 DXF 생성기(spikes/) — `docs/research/2026-11-09_ezdxf-spike-results.md`

## 보류 (다음 사이클 참고, 바로 만들지 말 것)

- 조사: 전기공사 직종 노임 공표 기관·위치 (D-015)
- 조사: 예정가격작성기준 현행 예규 번호·원 미만 처리 조문 (D-016)
- Gate 2 ADR: 레코드 스키마·규칙 파일 형식·xlsx 생성 수단·프로젝트 구조 (스파이크 결과 기반, D-012) — 승인 후 `src/auto_bim/` 정식 코드 착수
- 명세 공백(스파이크 발견, planner→CEO): F-009 귀속 등식 분모에 컨테이너 INSERT·XREF INSERT 포함 여부 / 자체 도형 있는 래퍼 블록의 UNMAPPED 여부 / F-006 `LAYER_OFF`의 부모 경로 문구
- 실CAD 확인 필요: 동적 블록 마커 실제 형태, 동결·끔 표시 규칙, MINSERT spacing 0 (실도면/CAD 확보 후)
- ezdxf 저장소 예제 DXF 스모크(D-004 b) 미실행
- 사용자 질문 1~13 답변 대기 (업무 분야, 도면 형식, CAD 보유, ODA, 유료 SDK, 나라장터, 정답 데이터, data.go.kr, 물가정보지, 사용 형태, 정답 세트, 품셈 열람, 실무 도구)
