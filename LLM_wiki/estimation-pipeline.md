# Estimation Pipeline — 단계별 입출력 계약

> 초안(2026-11-09). 스키마 확정은 개발 계열 ADR → `bim-ceo` 판정(Gate 2) 후. 바뀌면 이 문서를 갱신한다.

```
[도면 DWG/DXF/IFC]
   │ 1. 파싱 (cad-parser)
   ▼
drawing.json ── 단위·레이어·블록·엔티티(handle)·텍스트·치수·unsupported
   │ 2. 물량산출 (quantity-takeoff) + data/mappings/
   ▼
takeoff.json ── 품목·규격·단위·순수량·근거 handle·산출식·UNMAPPED
   │ 3. 단가·원가 (cost-estimator) + data/prices/
   ▼
estimate.json / estimate.xlsx ── 내역서·원가계산서·UNPRICED/ESTIMATED/STALE
   │ 4. 독립 검증 (estimate-verifier) → docs/qa/
   │ 5. 확정 (bim-ceo Gate 3)
   ▼
estimate_final.xlsx
```

## 1. drawing.json (초안)

```json
{
  "source": {"file": "A-101.dxf", "format": "DXF", "version": "AC1032", "sha256": "..."},
  "units": {"insunits": 4, "unit": "mm", "confidence": "header|inferred|unknown", "scale_note": "1/100"},
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
