# data/

| 경로 | 내용 | git |
|---|---|---|
| `drawings/samples/` | 공개·자작 샘플 도면 (테스트용) | 포함 |
| `drawings/private/` | 고객·실제 도면 — **외부 업로드 금지** | 제외 |
| `mappings/` | 레이어/블록/속성 → 품목 매핑 규칙 (`<공종>_<대상>.yaml`) | 포함 |
| `prices/` | 단가표·요율 — 행마다 출처·기준일 필수 (`<출처>_<기준일>.csv`, `rates_<연도>.yaml`) | 포함 |
| `ground_truth/` | 사람이 만든 정답 내역서 (`<도면명>/`) — 정확도 측정용 | 공개 가능한 것만 |

규칙: `LLM_wiki/operating-rules.md` (특히 규칙 1·2·5·8).
