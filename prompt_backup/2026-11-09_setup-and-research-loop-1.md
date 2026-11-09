# 2026-11-09 초기 세팅 + 리서치 루프 실행 1 (인수인계)

> 다음 세션은 이 파일부터 읽는다. 새 세션에서 "prompt_backup/2026-11-09_setup-and-research-loop-1.md 보고 이어서 진행"이라고 하면 된다.

## 한 일

1. AI 규칙·에이전트 세팅 (커밋 `89452e2`, 브랜치 `setup/ai-agent-config`)
   - AGENTS.md / CLAUDE.md, `.claude/agents/` 8종, `.claude/skills/` 3종, settings·hook, LLM_wiki, docs 골격
   - 사용자 지시: 결정은 `bim-ceo` 먼저 → CEO가 못 하면 사용자 / 파일 조회·검색·프로젝트 내 쓰기는 묻지 않음
2. 리서치 루프 실행 1 (5사이클) — 상세는 `.claude/skills/auto-bim-research-loop/SKILL.md`의 "기록"
   - 조사 4건: `docs/research/2026-11-09_*.md`
   - CEO 결정 D-001~D-016: `docs/decisions.md` (ceo_prompt v0.5)
   - 기획 v0.2: `docs/planning_document.md`, `docs/feature_definition.md` (F-001~F-019, Gate 1 조건부 승인)
   - ezdxf 스파이크 + 합성 DXF 생성기: `spikes/`, `data/drawings/samples/synth/` (pytest 14 passed)

## 진행 중이던 것 (세션 종료 시점)

- `estimate-verifier`의 합성 정답 독립 검증 (D-012 4항). 결과 파일: `docs/qa/synth-golden_2026-11-09.md`
  - **파일이 없으면 검증이 끊긴 것** → `estimate-verifier`를 다시 호출한다(대상: `spikes/synth/generate.py`, `data/drawings/samples/synth/*.expected.json`, 기준 F-002/F-005/F-006/F-009/F-012, D-009/D-010/D-012/D-014).
  - 7점 미만 반려면 cad-parser에 수정 요청 → 재검증.

## 다음 할 일 (순서대로)

1. 검증 결과 확인/재실행 (위)
2. 명세 공백 3건을 planner → CEO로 (SKILL.md "보류" 참고)
3. Gate 2 ADR 초안: 레코드 스키마·규칙 파일 형식·xlsx 생성 수단·프로젝트 구조 (`docs/research/2026-11-09_ezdxf-spike-results.md`의 "ADR에 넘길 핵심 사실" 기반) → `bim-ceo` 판정 → 승인 후 `src/auto_bim/` 정식 코드(F-001~F-010) 착수
4. 조사 보류 2건: 전기 직종 노임 공표처(D-015), 예정가격작성기준 예규 번호·끝수 조문(D-016)
5. 브랜치 정리: 원격 push/PR 또는 로컬 main 머지 — **사용자 확인 필요**

## 사용자에게 물어둔 질문 (답 대기, CEO 추천안 포함 — 답 없으면 추천안으로 진행)

1. 업무 분야(전기/건축/설비) — 추천: 전기로 진행
2. 받는 도면 형식·DWG 버전(2018 이후?) — 추천: DXF 저장본으로 시작
3. 업무 PC에 AutoCAD/BricsCAD 보유, DXF 직접 저장 가능 여부
4. ODA File Converter 업무 사용 — 추천: 사용 안 함
5. 유료 DWG SDK 구매 — 추천: MVP에서 안 함
6. 나라장터 등 계정으로 도면+내역서 쌍 확보 가능 여부
7. 실도면에 정답 내역서가 있는지, 공공 원가계산 vs 민간 실행견적
8. data.go.kr 가입·API 활용신청 — 추천: 보류(CSV로 진행)
9. 물가정보지 구독 — 추천: 보류, 필요 시 업체 견적 수기 입력
10. 사용 형태(명령 실행 + 엑셀 결과 + 텍스트 규칙 파일) 괜찮은지 — 추천: 이걸로 시작
11. 과거 전기 도면 세트 3개 + 수량산출서(순수량) 제공
12. 전기공사 표준품셈 열람 가능 여부·노무비 처리 — 추천: 당분간 UNPRICED
13. 실제 쓰는 적산 도구·양식(빈 양식 1부가 가장 도움)

## 메모

- 2026-11-09 중간에 네트워크 오류로 에이전트 2개가 끊겼다가 재개됨 — 산출물은 정상.
- `.venv/`(gitignore)에 ezdxf 1.4.5 설치됨. 테스트: `.venv/Scripts/python -m pytest spikes/tests`
