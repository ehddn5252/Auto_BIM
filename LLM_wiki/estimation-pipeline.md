# Estimation Pipeline — 단계별 입출력 계약

> 초안(2026-11-09). **모든 스키마·필드명은 잠정**이다. 확정은 개발 계열 ADR → `bim-ceo` 판정(Gate 2) 후(D-012: 레코드 스키마, 규칙 파일 형식, xlsx 생성 수단, 프로젝트 구조). 바뀌면 이 문서를 갱신한다.
> 반영한 결정: D-002(입력 어댑터·변환 이력), D-007(MVP 산출물 범위), D-010·D-014(단위 판정 출처), D-009(제외·경고). 아래 JSON 예시는 아직 갱신 전 초안이므로 필드는 의미 예시로만 읽는다.

```
[도면 DWG] ──(코어 밖 전처리 어댑터, 선택)──┐
   MVP 기본: 사용자가 CAD에서 DXF로 저장     │  변환 이력 기록(변환기명·버전,
   (MANUAL_SAVE / ORIGINAL_DXF)              │  원본 해시, DXF 해시) ← 0. 입력 전처리
                                             ▼
[DXF]  (IFC·RVT는 MVP 제외, 2단계 후보 — 어댑터로 같은 레코드를 채움)
   │ 1. 파싱 (cad-parser, DXF + ezdxf)
   ▼
drawing.json ── 포맷 중립 정규화 레코드: 원본 파일·레이어·블록·원본 객체 ID(handle)·단위(판정 출처)
   │              + 변환 이력 + unsupported 경고(XREF, ACIS, UNDERLAY…)
   │ 2. 물량산출 (quantity-takeoff) + data/mappings/
   ▼
takeoff.json ── 품목·규격·단위·순수량·근거 handle·산출식
   │              + MAPPED / EXCLUDED:<사유> / UNMAPPED / CONFLICT 귀속, 경고
   │ ▶ MVP 산출물 ①: 수량산출서 xlsx (7시트, 출력 양식 v1)
   │ 3. 단가 (cost-estimator) + data/prices/   ← 직접공사비까지
   ▼
estimate.json / estimate.xlsx ── 내역서(재료비·노무비·경비 분리 열): PRICED / UNPRICED / NA / PARTIAL / STALE
   │ ▶ MVP 산출물 ②: 직접공사비 내역서 xlsx
   │ (원가계산서·제비율 적용은 MVP 범위 밖, 견적 방식 확정 후 — D-007)
   │ 4. 독립 검증 (estimate-verifier) → docs/qa/
   │ 5. 확정 (bim-ceo Gate 3)
   ▼
estimate_final.xlsx
```

## 0. 입력 전처리 계약 (잠정, D-002)

- 코어 입력은 DXF다. DWG 변환은 코어 밖의 교체 가능한 어댑터이며 계약은 "원본 경로 → DXF 경로 + 이력 레코드"다. 실패하면 이력에 실패를 기록하고 DXF를 내지 않는다.
- MVP에서 실행 가능한 것은 `MANUAL_SAVE`(사용자가 저장), `ORIGINAL_DXF`(기록만 하는 no-op)뿐이다. AutoCAD/BricsCAD 어댑터는 사용자 보유 확인 후, ODA File Converter는 사용자가 업무 사용을 수용한 뒤에만 선택형으로 추가한다. 그 전에는 개발 PC에도 설치·실행하지 않는다. LibreDWG는 제외.
- 변환 이력 레코드: 변환 수단, 변환기명·버전("미상" 허용), 원본 해시("원본 미제공" 허용), DXF 해시, DXF 헤더 버전, 기록 시각. 수량산출서·내역서의 실행정보 시트에 들어간다.
- 단위: `$INSUNITS`가 없거나 0이면 `UNIT_UNKNOWN`으로 수량을 내지 않는다. 사용자가 단위를 지정하면 판정 출처 `user`로 기록하고 `UNIT_USER_SET`/`UNIT_OVERRIDE` 경고를 낸다. 시스템이 좌표로 추정한 단위는 수량에 쓰지 않는다(D-010, D-014).

## 1. drawing.json (초안)

```json
{
  "source": {"file": "A-101.dxf", "format": "DXF", "version": "AC1032", "sha256": "..."},
  "conversion": {"method": "MANUAL_SAVE|ORIGINAL_DXF|UNKNOWN", "tool": "미상", "origin_sha256": "원본 미제공", "dxf_sha256": "..."},
  "units": {"insunits": 4, "unit": "mm", "source": "header|user|unknown", "scale_note": "1/100"},
  "layers": [{"name": "A-DOOR", "entity_count": 42, "frozen": false}],
  "blocks": [{"name": "DOOR_900", "insert_count": 12, "attribs": ["TYPE", "SIZE"]}],
  "entities": [
    {"handle": "2F1", "type": "INSERT", "layer": "A-DOOR", "space": "Model",
     "block": "DOOR_900", "insert_path": [], "attribs": {"TYPE": "SD1"},
     "geom": {"insert": [1200, 3400, 0], "rotation": 90, "scale": [1, 1, 1]}}
  ],
  "texts": [{"handle": "3A0", "layer": "A-ANNO", "text": "CH=2700", "pos": [0, 0]}],
  "unsupported": [{"type": "PROXY_ENTITY", "count": 3}],
  "stats": {"total": 1234, "parsed": 1231, "unsupported": 3}
}
```

## 2. takeoff.json (초안)

```json
{
  "drawing": "A-101.dxf",
  "items": [
    {"item_code": "DOOR-STEEL-900x2100", "name": "강재문", "spec": "900x2100",
     "unit": "EA", "qty": 12, "formula": "INSERT(DOOR_900) count",
     "evidence": ["2F1", "2F7", "..."], "mapping_rule": "mappings/doors.yaml#DOOR_900"}
  ],
  "unmapped": [{"layer": "X-TEMP", "block": null, "type": "LINE", "count": 88}],
  "excluded": [{"reason": "Paper space viewport 중복", "count": 40}],
  "needs_input": [{"what": "층고", "why": "벽 면적 산출"}]
}
```

## 3. estimate.json (초안)

> MVP(D-007)는 직접공사비 내역서까지다. 내역서 열: 품목, 규격, 단위, 수량, 재료비·노무비·경비 단가와 금액, 출처, 도면 근거(성분별 상태·출처·근거 포함, D-008 Q4). 아래 `cost_sheet`는 MVP에서 만들지 않는다. 단가 출처 유형에 `QUOTE`(사용자 견적)를 처음부터 예약한다(D-011). 상태 값은 operating-rules 규칙 2 어휘를 따른다.

```json
{
  "basis": "public_cost_calc | private_execution",
  "currency": "KRW", "vat_included": false,
  "lines": [
    {"item_code": "DOOR-STEEL-900x2100", "qty": 12, "unit": "EA",
     "material_unit_price": 0, "labor_unit_price": 0, "expense_unit_price": 0,
     "loss_rate": 0.0, "amount": 0,
     "price_source": {"org": "...", "doc": "...", "as_of": "YYYY-MM", "url": "..."},
     "status": "PRICED | UNPRICED | ESTIMATED | STALE"}
  ],
  "totals": {"priced": 0, "estimated": 0, "unpriced_count": 0},
  "cost_sheet": {"note": "원가계산서 — 방식이 공공일 때만"}
}
```

## 정확도 측정 (정답 데이터가 생기면)

- `data/ground_truth/<도면명>/` 에 사람이 만든 내역서를 두고 비교: 품목 재현율, 품목별 수량 오차율, 총액 오차율, UNPRICED 비율.
- 회귀 테스트로 고정해 변경마다 비교한다.
