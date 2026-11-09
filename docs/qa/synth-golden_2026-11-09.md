# QA: F-012 합성 골든 + ezdxf 스파이크 독립 검증 (사이클 5)

- 검증자: estimate-verifier, 2026-11-09. 근거: D-012 4항(생성기 작성자 = 정답 계산자 → 독립 검토 필수).
- 대상: `spikes/synth/generate.py`, `data/drawings/samples/synth/*.expected.json`·`manifest.json`, `spikes/tests/`, `spikes/ezdxf_spike/`(a~f), `docs/research/2026-11-09_ezdxf-spike-results.md`.
- 기준: `docs/feature_definition.md` v0.2(F-002, F-003, F-005, F-006, F-009, F-012, T-01~T-21), `docs/decisions.md`(D-009, D-010, D-012, D-014), `LLM_wiki/operating-rules.md`.
- 모든 결과는 합성 자기 일관성 검증이며 실제 정확도가 아니다(D-004).

## 점수: 5 / 10 — 반려

정답 대부분은 독립 재계산과 일치했다. 하지만 정답이 틀렸거나 명세와 어긋난 케이스가 5건 있다(T-08, T-05, T-03 descend_all, T-09, T-16). 정답 없는 케이스(t14b)는 "0개"로 읽힐 수 있는 형식이다. 결정성 주장도 과장됐다. 이 골든으로 집계 코드를 맞추면 틀린 동작을 학습하게 되므로 반려한다.

## 검증 방법

1. **독립 재계산 스크립트**: 생성기를 import하지 않는 짧은 스크립트를 세션 scratchpad에 썼다(저장소에는 남기지 않음). ezdxf 1.4.5로 각 합성 DXF를 직접 열고 명세 규칙을 다시 구현했다.
   - 모델·페이퍼스페이스 INSERT를 재귀로 순회했다.
   - 레이어 `0` 상속, WCS 삽입점(행렬 합성), MINSERT 격자 전개를 계산했다.
   - 동적 블록 원본 이름은 XDATA `AcDbBlockRepBTag` 1005를 직접 읽어 판별했다(`dynblkhelper` 미사용).
   - 규칙은 manifest의 R01~R12 데이터만 읽고, 매칭·우선순위·CONFLICT, 매칭 시 탐색 정지와 `descend`를 적용했다.
   - 탐색을 멈춘 부모의 정의 안 자식 INSERT를 평가해 `NESTED_MATCH_HIDDEN`(handle, 숨은 자식 수, 규칙 ID)을 냈다.
   - F-006 사유 우선순위를 그대로 적용했다: PAPER_SPACE, LAYER_FROZEN(경로), LAYER_OFF(유효 레이어), LEGEND_AREA, ZERO_SCALE, DUPLICATE(같은 공간·같은 매핑 키, 거리 ≤ 도면 단위 환산 1mm, handle 순서상 첫 인스턴스 유지), RULE_IGNORE.
   - 단위 판정과 경고를 계산했다: 헤더 없음/0 → 수량 미출력, `UNIT_USER_SET`/`UNIT_OVERRIDE`, `BLOCK_UNIT_DIFF`. F-003 경고(XREF 정의·INSERT, ACIS, PROXY, UNDERLAY/IMAGE, DYNAMIC_UNRESOLVED)와 NON_BLOCK_SYMBOL도 계산했다.
   - 시나리오 설정(descend, include_hidden, legend_area, user_unit)을 반영했다.
   - 수량, 제외 사유별 key, UNMAPPED, CONFLICT, 경고(코드·handle·개수), 숨김 레이어 제외 건수, DUPLICATE 짝, 컨테이너를 expected.json과 필드별로 비교했다.
   - 대상은 expected 파일 전체(21개 파일, 30개 시나리오)다. 요청된 T-01, T-03, T-05, T-06, T-07, T-09, T-14, T-19를 포함한다.
2. DXF 원자료를 직접 조회했다. T-05 구조, T-08 스케일 값, manifest SHA-256, t19 복사본 해시를 확인했다.
3. `.venv/Scripts/python -m pytest spikes/tests`를 실제로 실행했다.
4. 생성기 CLI를 별도 프로세스로 3회(같은 seed 2회, seed 7 1회) 실행해 바이트를 비교했다. `PYTHONHASHSEED=0`으로 고정한 2회도 비교했다.
5. 생성기 import 목록을 확인했다(코드 읽기, 테스트 결과 확인).
6. `spikes/ezdxf_spike/run_all.py`를 재실행해 `results/*.txt`의 RESULT 줄이 재현되는지 확인했다.

## 결과 요약

| 케이스:시나리오 | 결과 |
|---|---|
| t01_basic | 일치(수량 19, 경고 0) |
| t02_nested | 일치(LIGHT 16, OUTLET 8, SWITCH 3, 컨테이너 11). 첫 실행의 "DIFF"는 내 비교 코드의 set() 처리 오류였고 실제 차이는 없다 |
| t03 default | 일치. NESTED_MATCH_HIDDEN 4건의 handle(65, 67, 69, 6B), 숨은 자식 수 2, 자식 규칙(R05/R01) 모두 일치. 대조군(OUTLET_2P⊃PLATE_X)은 경고 0 |
| **t03 descend_all** | **불일치**(F-1) |
| t04_dynamic | 일치(LIGHT_DYN 6, UNMAPPED 55·57, DYNAMIC_UNRESOLVED 2) |
| **t05_attrib** | 수량은 우연히 일치. **handle·블록·경고 불일치**(F-2) |
| t06_mm_file default / user_override_m, t06_m_file, t06_set | 일치. 경고는 UNIT_OVERRIDE 1, BLOCK_UNIT_DIFF 4블록. 세트의 SET_UNIT_DIFF는 4 대 6 |
| t07_missing / t07_zero (default, user_mm) | 일치. 헤더 키 부재와 0을 확인했다. 수량 미출력, user_mm은 UNIT_USER_SET만 나오고 UNIT_OVERRIDE 0 |
| **t08_scale_rot_mirror** | **불일치**(F-3) |
| **t09 default** | 명세 문구 기준 **불일치**(F-4). 부모 경로 기준 OFF로 다시 계산하면 일치 |
| t09 include_hidden | 일치(13) |
| t10, t11(DUPLICATE 짝 포함), t12(두 시나리오, 범례 텍스트 handle 61), t13(XREF 3D·48), t14_minsert(22), t15, t17(8개 handle), t18, t19_floor1~3 + set 합(11/9/8/13), t20_empty, t21 | 일치 |
| **t14b** | 정답 없음인데 형식상 수량 `{}`로 기록됨(F-6) |
| **t16** | 수량 일치. NON_BLOCK_SYMBOL은 명세 문구 기준 **불일치**(F-5) |

pytest: `14 passed in 2.14s`. 기존·신규 실패 없음. 단, 아래 결함 F-1~F-3, F-7은 이 테스트로 잡히지 않는다.
스파이크 a~f 재실행: 6개 모두 rc=0이고 RESULT 줄이 `results/*.txt`와 같다.

## 발견 문제 (정답 불일치 — 수정 필요)

### F-1 T-03 descend_all: 같은 위치 자식이 DUPLICATE 규칙에 걸림

- 생성기가 PANEL_DB 안 BREAKER k개와 WRAP_IGN 안 LIGHT_A m개를 모두 정의 내 (0,0)에 넣었다(`defchild(..., (0, 0))`). 그래서 같은 부모 안 자식들이 WCS상 같은 점에 겹친다.
- F-006 순위 7(같은 공간, 같은 매핑 키, 거리 ≤ 1mm)에 따르면 부모마다 첫 자식만 세고 나머지는 DUPLICATE다.

| 필드 | 기대 | 재계산 |
|---|---|---|
| quantities.SYN-BREAKER | 4 | 2 |
| quantities.SYN-LIGHT-A | 4 | 2 |
| excluded.DUPLICATE | 없음 | 65/5D, 67/5D, 69/61, 6B/61 |

- 테스트 `test_t03_warning_counts`는 `wrappers*lights_per_wrapper`를 정답으로 고정하고 있어 잘못된 값을 강제한다.
- 수정안: 자식 삽입점을 서로 1mm보다 멀리 둔다(권장). 아니면 descend_all에 DUPLICATE 귀속을 넣는다.

### F-2 T-05: ATTRIB 블록이 익명 `*U`로 감싸져 있어 정답 구조가 틀림

- `add_auto_blockref`는 익명 블록 `*U1`~`*U8`을 만들고, 그 안에 ATTRIB(WATT)이 붙은 LIGHT_W INSERT를 넣는다. 그래서 DXF 실제 구조가 정답과 다르다.
  - 모델스페이스 INSERT 42 = `*U1`(ATTRIB 0개, XDATA 없음, 익명 플래그 1)
  - 그 안의 INSERT 3F = LIGHT_W, WATT=20
- 정답 쪽은 모순이다. 정답은 key `42`, block `*U1`, attribs `{}`인 인스턴스를 SYN-LIGHT-20W로 매핑한다. 그런데 R08은 block=LIGHT_W이고 WATT=20이어야 한다.
- 명세대로 처리하면 다음과 같다.
  - `*U`는 원본 이름 판별 불가 → `DYNAMIC_UNRESOLVED` 경고 8건(F-003, F-005 5항)
  - 규칙에 매칭되지 않으므로 안으로 내려가 LIGHT_W를 매칭한다.

| 필드 | 기대 | 재계산 |
|---|---|---|
| unmapped | 72, 7A | 72/6F, 7A/77 |
| 매핑 인스턴스 key | 42 등 최상위 | 42/3F 등 중첩 |
| warnings | [] | DYNAMIC_UNRESOLVED 8건 |
| quantities | 20W 4, 40W 2 | 20W 4, 40W 2(일치) |

- 결과적으로 T-05는 "같은 블록 INSERT에 붙은 ATTRIB로 규격이 갈림"을 시험하지 못하고, 익명 래퍼 처리를 시험하게 된다.
- `test_expected_attribution_and_handles`는 정답의 block 값을 DXF에서 다시 읽어 넣었기 때문에(`*U1`) 이 결함을 잡지 못한다.
- 수정안: `add_blockref("LIGHT_W")` + `add_auto_attribs`/`add_attrib`로 최상위 INSERT에 ATTRIB를 붙인다.

### F-3 T-08: ZERO_SCALE 인스턴스가 DXF에 없음

- 생성기가 `xscale=0.0`을 넘겼지만 ezdxf가 저장 전에 1로 바꿨다. 정답 자신의 instance 레코드도 `scale: [1, 1.0, 1.0]`이다.
- DXF를 다시 읽으면 handle 51, 53, 55에 xscale 속성이 없다(기본 1).
- 그런데 정답은 이 3개를 `EXCLUDED:ZERO_SCALE`로 둔다.

| 필드 | 기대 | 재계산 |
|---|---|---|
| quantities.SYN-LIGHT-A | 10 | 13 |
| excluded.ZERO_SCALE | 51, 53, 55 | 없음 |

- 같은 정답 파일 안에서 fate와 scale 필드가 서로 모순이다. manifest는 T-08을 SYNTHESIZED로 표시하지만 ZERO_SCALE 하위 케이스는 실제로 합성되지 않았다.
- 수정안(둘 중 하나):
  - 저장 후 DXF 텍스트에서 그룹 코드 41을 0으로 패치한다. 패치 후 ezdxf가 읽을 때 다시 고치는지 확인해야 한다.
  - ezdxf로는 합성 불가로 표시한다.
- 어느 쪽이든 "ZERO_SCALE fate면 다시 읽은 scale에 0이 있다"는 자체 검사를 추가한다.

### F-4 T-09 default: LAYER_OFF 판정이 명세 문구와 다름 (66/4C)

- 부모 ROOM_W3은 꺼진 레이어 E-OFF에 있고, 자식 4C는 켜진 E-LIGHT에 있다(유효 레이어 E-LIGHT).
- F-006 순위 3은 "유효 레이어가 꺼져 있음"이다. 이 문구로는 4C가 MAPPED여야 한다.

| 필드 | 기대 | 명세 문구 재계산 |
|---|---|---|
| quantities.SYN-LIGHT-A | 3 | 4 |
| excluded.LAYER_OFF | 5C, 66/4C, 66/4E | 5C, 66/4E |
| hidden_layer_excluded.LAYER_OFF | 3 | 2 |

- 부모 경로 기준 OFF로 다시 계산하면 정답과 완전히 일치한다. 즉 차이는 이 판정 하나뿐이다.
- 생성기 notes와 보고서 5절이 이 공백을 밝혔고 T-09를 PARTIAL로 둔 것은 맞다.
- 그러나 다음 두 가지가 문제다.
  - expected의 scenario 필드는 이 값을 확정 정답처럼 담고 있다. 기계 비교에서 구분되지 않는다.
  - 생성기 note는 "truth follows AutoCAD display (a hidden parent INSERT hides all children)"라고 AutoCAD 동작을 단정한다.
- 검증자 기억(미검증, 출처 미확인): AutoCAD에서 블록 참조의 레이어를 **동결**하면 블록 전체가 숨는다. **끄면**(off) 레이어 0/BYLAYER 성분만 숨고, 다른 켜진 레이어의 블록 내부 객체는 보인다.
  - 이 기억이 맞으면 명세 문구 쪽이 AutoCAD와 같고, 생성기 정답이 틀렸다.
  - 스파이크 b도 같은 가정('off:E-OFF'가 E-FIX 자식까지 숨김)을 쓰고 있어 함께 재검토가 필요하다.
- 수정안: 66/4C를 "판정 보류"로 분리해 표시한다(기계 비교에서 제외). bim-planner/CEO 판정과 실제 CAD 확인 후 확정한다.

### F-5 T-16: NON_BLOCK_SYMBOL "기구 레이어" 정의 불일치

- F-009 3항은 기구 레이어를 "매핑 규칙이 조건으로 참조하는 레이어"로 정의한다.
- t16의 활성 규칙은 R01(block=LIGHT_A)뿐이고 레이어 조건이 없다. 따라서 명세 문구대로면 기구 레이어가 없고 경고는 0건이다.
- 정답은 E-LIGHT의 43, 44, 45, 46을 경고로 기대한다. 생성기 FIX 표의 "home layer"를 기구 레이어로 본 해석이다.
- "매핑된 INSERT가 놓인 레이어"로 해석해 다시 계산하면 일치한다.
- 수정안(둘 중 하나):
  - t16 활성 규칙에 `effective_layer: E-LIGHT` 조건이 있는 규칙을 둔다.
  - bim-planner가 정의를 개정한다.

## 발견 문제 (형식·주장)

### F-6 t14b: 정답 없음이 "수량 0"으로 읽힘

- scenario `default`는 `quantities: {}`, `emit_quantities: true`, `file_status: OK`, attribution total 0이다. "정답 없음" 표시는 `extra.ambiguity`에만 있다.
- 자동 비교기는 이 파일을 "0개가 정답"으로 채점한다. 테스트 없는 항목을 통과로 세지 않는다는 규칙 10 취지에 어긋난다.
- 수정안: scenario를 아예 두지 않거나, 채점 제외 플래그를 기계가 읽는 필드에 둔다.
- 참고(판정 아님): 명세 F-006 DUPLICATE를 적용하면 두 해석 모두 MAPPED 4가 된다.
  - 선언대로 3×4=12로 전개하면 8개가 DUPLICATE로 빠진다.
  - ezdxf mcount를 쓰면 처음부터 4개다.
  - 귀속만 다르므로 CEO 판정으로 정할 수 있다.

### F-7 결정성 주장 과장

- 보고서 3절은 "같은 seed로 두 번 생성 시 모든 파일이 바이트 동일"이라고 주장한다. 프로세스 안에서만 참이다.
- CLI를 별도 프로세스로 같은 seed 2회 실행하면 DXF 27개와 manifest.json이 다르다.
  - 원인은 OBJECTS 섹션에서 LAYOUT/ACDBPLACEHOLDER 순서가 바뀌는 것이다.
  - 같은 프로세스 안 생성은 문자열 해시 seed가 같아 테스트가 통과한다.
  - `PYTHONHASHSEED=0`으로 고정하면 2회가 완전히 동일하다.
- expected.json은 프로세스가 달라도 바이트가 같다. 따라서 F-012 검증 조건(정답 파일 바이트 동일, 엔티티 구성 동일)은 충족된다.
- 하지만 manifest의 DXF SHA-256은 재생성할 때마다 바뀐다. 현재 커밋 대상 파일과 manifest 해시 28개는 일치한다.
- 수정안: 생성 시 해시 seed를 고정하거나 객체 순서를 안정화한다. 테스트를 subprocess 2회 실행으로 바꾸고, 보고서 문구를 고친다.

### F-8 커버리지 공백 (명세 요구, 합성 없음)

- D-014 Q15: 숨은 자식이 **IGNORE 규칙에만** 매칭되는 경우가 없다. T-03의 숨은 자식은 모두 품목 매칭이다.
- F-005 2-1은 숨은 자식 수를 품목/IGNORE로 나눠 적으라고 한다. 정답 형식은 `hidden_by_result` 문자열 하나에 `hidden_children` 하나뿐이라 둘이 섞인 경우를 표현할 수 없다.
- F-002 "사용자 지정 = 헤더 값" 케이스(경고 코드 없이 기록 행 1건)가 없다.
- T-07 default(UNIT_UNKNOWN)의 attribution은 total 0이다. 실제 레코드는 11개다. "귀속 미산출"인지 "인스턴스 0개"인지 구분할 표시가 필요하다(경미).
- T-02(자체 도형이 있는 래퍼)와 T-13(XREF INSERT를 `unclassified_by_spec`로 둠)은 명세 공백으로 이미 밝혀져 있다. planner 질의 대상으로 유지한다.

## 확인된 항목 (통과)

- **생성기 import**: ezdxf(`dynblkhelper`, `lldxf.const`, `lldxf.tags/types`)와 표준 라이브러리만 쓴다. auto_bim·takeoff·parsing import는 0이다. 정적 테스트(`test_generator_imports_no_aggregation_code`)도 통과했다.
- **정답 계산 방식**: 정답은 배치 파라미터(`children_of` 레지스트리, fate 지정)로 만든다. 다만 F-2와 F-3은 "파라미터로 의도한 것"과 "DXF에 실제로 써진 것"이 어긋났다. 그런데 파라미터 기반 정답이 이를 감지하지 못했다. 정답을 다시 읽은 DXF 속성(scale, ATTRIB, 블록 이름의 규칙 매칭 가능성)과 맞춰 보는 자체 검사가 필요하다.
- **명세 규칙과 맞음**:
  - 중복 1mm(T-11): 0.5mm와 회전만 다른 경우는 DUPLICATE, 50mm 떨어진 경우는 둘 다 셈. 짝 handle 일치
  - 동결 기본 제외와 포함 시나리오, 동결이 끔보다 우선(T-09)
  - 중첩 매칭 시 탐색 정지와 NESTED_MATCH_HIDDEN(T-03 default의 (a)(b) 경고, (c)(d) 무경고)
  - UNIT_USER_SET/UNIT_OVERRIDE 구분(T-06, T-07)
  - 범례는 명시 규칙으로만 제외. 규칙이 없으면 LEGEND_SUSPECT만 내고 수량은 그대로(T-12)
- **보고서의 '부분' 4건**:
  - T-04, T-09, T-14, T-17은 manifest와 보고서 모두 PARTIAL로 표시돼 있다. 보고서는 "합성 통과를 실도면 근거로 세면 안 된다"고 적었다.
  - 다만 T-09(F-4)와 t14b(F-6)는 기계가 읽는 정답 필드에 보류 표시가 없다. 그래서 회귀 채점에서 확정 정답처럼 쓰일 위험이 있다.
  - PARTIAL이 아닌 T-05와 T-08은 SYNTHESIZED로 표시됐지만 실제로는 의도한 함정을 합성하지 못했다(F-2, F-3). 이쪽이 더 큰 과대 주장이다.
- **스파이크 a~f**: 재실행 결과가 기록과 같다. 보고서 1절의 상태 표기(a 부분, b~f 성공)는 출력과 맞다.

## 검증 못 한 부분

- **실제 AutoCAD 동작**: 끔/동결 레이어 표시 규칙, MINSERT spacing 0, 동적 블록 마커 모양. CAD 프로그램과 웹 조회 수단이 없었다. F-4의 AutoCAD OFF 동작은 검증자 기억이며 출처로 확인하지 않았다.
- **다른 CAD가 쓴 DXF**: ezdxf가 쓰고 ezdxf가 읽는 구조라 문법 차이는 검증 범위 밖이다.
- **내 재계산 스크립트도 독립 구현 1개뿐이다**. 같은 ezdxf 라이브러리에 기대므로, ezdxf 자체의 읽기 오류는 둘 다 놓친다.
- **LEGEND_SUSPECT**: 텍스트 handle과 범례 기호 handle만 확인했다. "주변·여러 개" 판정 기준값은 명세상 미정이라 재현하지 않았다.
- **F-003 경고의 부가 필드**(layer, entity_type, xref_path)는 handle과 코드만 비교했다.
- **T-20 corrupt**: 읽기 실패는 pytest 결과로만 확인하고 직접 재현하지 않았다. **t19_dup_hash**: 두 파일 해시가 같다는 것만 확인했다.
- **ezdxf 저장소 예제 DXF 스모크**: 생성자도 하지 않았고 나도 하지 않았다.
- **정답 데이터 비교**: 실도면이나 사람이 만든 정답이 없어 오차율 회귀 비교는 하지 않았다(D-004).

## 생성 에이전트에게 돌려줄 수정 사항

1. F-3: T-08 ZERO_SCALE을 실제로 합성하거나 합성 불가로 표시한다. scale과 fate가 서로 맞는지 보는 검사를 추가한다.
2. F-2: T-05에서 ATTRIB를 최상위 LIGHT_W INSERT에 붙인다. 익명 래퍼 케이스가 필요하면 별도 케이스로 만들고 DYNAMIC_UNRESOLVED와 중첩 key를 정답에 넣는다.
3. F-1: T-03 자식 삽입점을 서로 떨어뜨린다. `test_t03_warning_counts` 기대값이 명세 DUPLICATE 규칙과 맞는지 다시 확인한다.
4. F-4: T-09의 66/4C를 판정 보류로 분리 표시한다. "AutoCAD display" 단정 문구를 미검증으로 고친다. bim-planner 질의를 유지한다.
5. F-5: t16 규칙에 레이어 조건을 넣거나 planner 정의 개정을 요청한다.
6. F-6: t14b scenario에 기계가 읽는 채점 제외 표시를 둔다.
7. F-7: 프로세스 간 결정성을 확보하고 테스트와 보고서 문구를 고친다.
8. F-8: IGNORE-only 숨은 자식 케이스와 품목/IGNORE 분리 카운트 필드를 넣는다. "사용자 지정 = 헤더" 케이스를 추가한다.
9. 정답의 매핑 fate마다 "다시 읽은 DXF 속성(블록 이름, ATTRIB, scale, 레이어)이 해당 규칙 조건을 만족한다"는 자체 검사를 테스트로 추가한다. F-2와 F-3 같은 의도와 실제의 어긋남을 막기 위해서다.
