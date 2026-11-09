# ezdxf 스파이크 결과 + F-012 합성 생성기 (사이클 5)

- 작성: cad-parser, 2026-11-09. 근거 결정: D-012. 입력은 합성 DXF만 사용(실도면·ezdxf 예제 DXF 미사용).
- 환경: Python 3.14.4, ezdxf 1.4.5 고정(`spikes/requirements.txt`, freeze 전체), 프로젝트 루트 `.venv`(gitignore됨).
- 코드: `spikes/ezdxf_spike/`(a~f 스크립트, `run_all.py`, 증거 출력 `results/*.txt`), `spikes/synth/generate.py`, `spikes/tests/`.
- 생성 산출물: `data/drawings/samples/synth/` (DXF 28개 + 정답 JSON + manifest.json). 모든 정답은 "자기 일관성 검증 — 실제 정확도 아님"(D-004)이며 형식은 ADR 전까지 잠정.
- 한계: ezdxf 저장소 예제 DXF 스모크는 하지 못했다(네트워크는 pip 설치만 허용, sdist 다운로드는 빌드 의존성 오류). 필요하면 후속.

## 1. D-012 확인 항목 결과

| 항목 | 결과 | 핵심 증거 / 사실 |
|---|---|---|
| (a) 동적 블록 원본 이름 | **부분** | ezdxf 1.4.5에 `ezdxf.dynblkhelper`가 있다. 정의 BLOCK_RECORD의 XDATA `AcDbDynamicBlockGUID`, `*U` BLOCK_RECORD의 XDATA `AcDbBlockRepBTag`(1005=정의 핸들)로 원본 이름을 찾는다. 합성 4개 INSERT 중 2개 해결(`*U1`→`LIGHT_DYN_A`, 정의 직접 참조), 태그 없음/핸들 불량 `*U`는 None(→`DYNAMIC_UNRESOLVED`). **마커는 우리가 합성한 것**이라 실제 AutoCAD 출력과 같은 모양인지는 미확인. `AcDbDynamicBlockPurgePreventer`는 ezdxf 지원 없음·미검증. 확장 딕셔너리 경로(ACAD_ENHANCEDBLOCK)는 시도하지 못함. |
| (b) 중첩 + 동결/끔 | **성공(자체 로직 필요)** | ezdxf는 `layer.is_frozen()/is_off()`와 원 레이어명만 준다. 레이어 `0` 상속, 부모가 숨겨지면 자식도 숨김은 **해 주지 않는다**(`virtual_entities()`가 자식 레이어 `0`을 그대로 반환). 파서가 insert 경로를 따라 유효 레이어·숨김 원인을 계산해야 한다. 엔티티 `invisible` 플래그도 별도 원인. AutoCAD 실제 표시와의 일치는 CAD 프로그램이 없어 미검증. |
| (c) MINSERT | **성공** | `Insert.multi_insert()`로 3x4→12, 90도 회전 격자도 정확. **함정**: `row_spacing=0`이면 `mcount`가 그 방향을 1로 접는다(3x4 선언→4). AutoCAD가 실제로 몇 개로 보는지 불명 → T-14b는 정답 미지정. `row_count*column_count`를 쓰지 말고 `mcount`/`multi_insert`를 쓴다. |
| (d) ACIS·PROXY·UNDERLAY·XREF 합성 | **성공(스텁 수준)** | 3DSOLID/REGION/BODY(**빈 껍데기는 저장 시 조용히 사라짐** → 가짜 SAT 페이로드 필요), ACAD_PROXY_ENTITY(Tags 직접 구성), PDF 언더레이, IMAGE, XREF 정의+INSERT(대상 파일 없음) 모두 저장·재로딩 후 유형 보존. 미지 엔티티 유형(`FOOBAR_THING`)은 `DXFTagStorage`로 읽힘. 실제 ACIS/SAB(R2013+), 실제 프록시 그래픽은 합성 불가. PDF·DWF·DGN 언더레이와 IMAGE 모두 합성 성공(`t17` 정답 `synthesis_failures` 비어 있음). `Insert.is_xref()`는 **메서드**다. audit 오류 0. |
| (e) Python 3.14 | **성공** | 3.14.4 + ezdxf 1.4.5(C 확장 사용) 설치, 생성·저장·재로딩·audit 오류 0, `warnings=error`에서도 경고 없음. pytest 9.2도 동작. |
| (f) handle 역추적 | **성공** | 저장·재로딩 후 handle 유지. `entitydb.get(handle)`로 INSERT와 insert_path의 모든 부모를 재조회, 소유 블록 이름이 경로와 일치(5/5, 페이퍼스페이스 포함). 같은 블록 정의 안 엔티티는 인스턴스마다 같은 handle이므로 **식별 키 = insert_path + handle**(MINSERT는 + 격자 인덱스). `virtual_entities()`는 handle=None이라 증거로 못 쓰고, 원본은 `source_of_copy`로 찾는다 → 파서는 INSERT를 직접 재귀 순회해야 한다. |

## 2. F-012 합성 케이스

- 정답 구조(잠정): 인스턴스별 레코드(key, handle, insert_path, 블록, 레이어, 유효 레이어, 공간, 스케일, 회전, ATTRIB, 격자) + 시나리오별(기본/설정 변경) 귀속(MAPPED 품목별 수량, EXCLUDED 사유별 key, UNMAPPED, CONFLICT, 분류 불가) + 귀속 등식 + 경고(코드·handle) + 파일 상태. 합성 규칙 사전 R01~R12와 합성용 품목은 manifest.json에 있다.
- 정답은 배치 파라미터(레지스트리)에서 계산하며 집계 모듈을 import하지 않는다(테스트로 강제).
- 단위 경고는 D-014 Q13 반영: 헤더 없음/0 + 사용자 지정 → `UNIT_USER_SET`, 헤더 값과 다른 지정 → `UNIT_OVERRIDE`(t06_mm_file의 `user_override_m` 시나리오).

| T-ID | 상태 | 파일 / 비고 |
|---|---|---|
| T-01 | 합성 | t01_basic |
| T-02 | 합성 | t02_nested (2단·3단) |
| T-03 | 합성 | t03_nested_match_hidden (default/descend_all, 오경보 대조군 포함) |
| T-04 | **부분** | t04_dynamic. (b) 완전 합성. (a)는 합성 마커라 실도면에서 재확인 필요 |
| T-05 | 합성 | t05_attrib (WATT 60은 UNMAPPED) |
| T-06 | 합성 | t06_mm_file, t06_m_file, t06_set (`SET_UNIT_DIFF`, `BLOCK_UNIT_DIFF`) |
| T-07 | 합성 | t07_insunits_missing, t07_insunits_zero |
| T-08 | 합성 | t08_scale_rot_mirror (ZERO_SCALE 제외 포함) |
| T-09 | **부분** | t09_hidden_layers. 부모 숨김→자식 숨김의 정답이 AutoCAD 표시 규칙 가정, VP별 동결 미합성 |
| T-10 | 합성 | t10_paper_space (Layout1/2) |
| T-11 | 합성 | t11_duplicates (동일/0.5mm/회전만 다름/50mm) |
| T-12 | 합성 | t12_legend (규칙 없음/있음 시나리오) |
| T-13 | 합성 | t13_xref (INCOMPLETE) |
| T-14 | **부분** | t14_minsert(3x4, 회전 2x5) 정답 있음. t14b spacing 0은 정답 없음 |
| T-15 | 합성 | t15_layer0_inherit |
| T-16 | 합성 | t16_non_block_symbols (원 2~3, 닫힌 폴리라인, 대조군) |
| T-17 | **부분** | t17_acis_proxy_underlay (R2010, 스텁). 실제 ACIS/SAB·프록시 그래픽 합성 불가 |
| T-18 | 합성 | t18_conflict |
| T-19 | 합성 | t19_floor1~3, t19_set, 해시 동일 복사본(t19_dup_hash) |
| T-20 | 합성 | t20_corrupt(손상 바이트, 읽기 실패 확인), t20_empty |
| T-21 | 합성 | t21_unused_definitions |

"완전 합성 불가"로 분모에서 뺄 케이스는 없다. 단 부분 4건(T-04a, T-09, T-14b, T-17 실제 페이로드)은 합성 통과를 실도면 근거로 세면 안 된다.

## 3. 테스트 실행 (`python -m pytest spikes/tests`, .venv)

14 passed in 2.49s. 검증: 같은 seed로 두 번 생성 시 모든 파일이 바이트 동일(`write_fixed_meta_data_for_testing` 사용), seed가 다르면 정답이 바뀜, 손상 파일 제외 전 DXF가 재로딩·audit 오류 0, 정답의 모든 handle·insert_path가 DXF에 존재(100건 초과), 귀속 등식 성립, T-01 독립 INSERT 수 일치, T-02 공식(`2*(p+2q)` 등), T-03 경고 수, MINSERT 22, 동적 블록 해석이 정답과 일치, T-01~T-21 커버, 생성기의 auto_bim/takeoff/parsing import 0, D-014 단위 경고 코드.
주의: 생성기 작성자와 정답 계산자가 같으므로 D-012 4항에 따라 `estimate-verifier`의 정답 계산 독립 검토가 필요하다. 테스트의 일부(INSERT 수, 공식)는 독립 계산이지만 대부분은 자기 일관성이다.

## 4. Gate 2 ADR에 넣을 사실

1. ezdxf 1.4.5는 Python 3.14.4에서 설치·동작·audit 통과.
2. 파서는 `virtual_entities()`가 아니라 INSERT 직접 재귀 순회로 구현한다(handle 없음). 식별 키는 insert_path + handle (+ MINSERT 격자 인덱스). 재조회는 `entitydb.get`.
3. 유효 레이어(레이어 `0` 상속), 부모 경로 기반 숨김 판정, 엔티티 `invisible`은 ezdxf가 제공하지 않으므로 파서 책임.
4. MINSERT는 `mcount`/`multi_insert` 사용. spacing 0 동작은 실제 CAD 확인 전까지 `unsupported`/경고로 다룬다.
5. 동적 블록은 `dynblkhelper`로 원본 이름 판별 시도, 실패 시 `DYNAMIC_UNRESOLVED`. 실제 파일 검증 전까지 "판별 가능"을 보장하지 않는다.
6. 빈 ACIS 엔티티는 ezdxf가 저장하지 않는다(읽기 측 영향 없음, 합성 시에만 해당). 미지 엔티티는 `DXFTagStorage`로 읽히므로 `UNKNOWN_ENTITY` 집계 가능. 프록시는 `ACAD_PROXY_ENTITY` 유형으로 구분 가능.
7. 블록 BLOCK_RECORD의 `units` 속성으로 `BLOCK_UNIT_DIFF` 판정 가능(합성 확인). `$INSUNITS` 누락은 헤더 키 부재로 구분된다.
8. 결정적 합성을 위해 `ezdxf.options.write_fixed_meta_data_for_testing`을 쓴다.

## 5. 위험·명세 공백 (기획/CEO 질의 후보)

- 귀속 등식(F-009)의 분모에 컨테이너 INSERT(내려간 래퍼)와 XREF INSERT를 어떻게 넣을지 미정. 지금은 컨테이너는 별도 집계, XREF INSERT는 `unclassified_by_spec`.
- 자체 도형이 있는 래퍼 블록이 UNMAPPED도 되는지 미정.
- F-006 `LAYER_OFF`는 "유효 레이어가 꺼짐"으로만 적혀 있어, 꺼진 레이어의 부모 INSERT 안 자식(자식 레이어는 켜짐)은 규칙 문구로는 포함되고 AutoCAD 표시로는 숨김이다. 문구 보완 필요.
- 실제 AutoCAD의 동적 블록 마커·동결/끔 표시 규칙·MINSERT spacing 0은 이 환경에서 검증 불가 → 사용자 실도면/CAD 확인 단계 필요.
- ezdxf 저장소 예제 DXF 스모크는 미수행.
- 합성 DXF는 ezdxf로만 만들어 ezdxf로 읽으므로 "다른 CAD가 쓴 파일"의 문법 차이는 검증하지 못한다.

질의 필요: estimate-verifier — 합성 정답(`data/drawings/samples/synth/*.expected.json`)과 `spikes/synth/generate.py`의 정답 계산 독립 검토 (D-012 4항).
질의 필요: bim-planner — 위 5절의 귀속 등식 분모(컨테이너·XREF INSERT), 자체 도형 래퍼, LAYER_OFF 부모 경로 문구.
