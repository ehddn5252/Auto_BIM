# 도면 입력(DWG/DXF/IFC/RVT/PDF) 로컬 읽기 수단 비교 조사 (2026-11-09)

## 질문
적산 담당자가 받는 도면을 **로컬에서** 읽어 엔티티·레이어·블록(INSERT)·ATTRIB·텍스트·치수·단위를 뽑는 수단은 무엇이 있고, 라이선스·자동화·Python 3.14/Windows 호환성은 어떤가?
하위 질문: (1) DWG 읽기 경로 (2) ezdxf (3) IfcOpenShell/RVT (4) 한국 실무 입력 형식 (5) PDF 대안

## 결론 요약
1. **DWG는 "DWG -> DXF 변환 후 ezdxf"가 가장 현실적인 경로**이나, 변환기로 쓰는 ODA File Converter의 **상업적 사용 허용 여부가 불확실**하다. ODA 공식 FAQ: 비회원은 "non-commercial applications only". 회사 업무(적산)에서의 내부 사용이 이에 해당하는지는 약관 원문을 확인하지 못함. (확신도: 불확실 - 법무/사용자 확인 필요)
2. **ezdxf는 MIT, 최신 1.4.5(2026-10-16), Python 3.14 classifier 명시** -> DXF 파싱 기반으로 적합 (확인됨). 단 XREF·ACIS·ACAD_TABLE·UNDERLAY는 분해/bbox 미지원, 블록 단위는 자동 변환 없음(직접 스케일 계산), 동적 블록 유효이름(EffectiveName) 지원 근거는 못 찾음.
3. **IfcOpenShell 0.9.0.post1(2026-10-15): LGPL-3.0-or-later, py314 win_amd64 휠 있음** (확인됨). 수량은 IFC에 Qto가 들어 있으면 읽고, 없으면 ifc5d(기하 기반)로 계산 가능(유력; 공식 문서 직접 확인은 못 함).
4. RVT는 Revit 없이 직접 읽는 검증된 수단이 없음. 현실적 경로는 "사용자가 IFC로 내보내기". 오픈소스 rvt-rs가 있으나 부분 지원·출처 불일치로 MVP 의존 불가(불확실).
5. 한국 실무의 도면 형식 비율을 보여주는 **1차 근거는 못 찾음**. 2차 정황: DWG+PDF 병행 전달이 일반적.

## 근거
| 주장 | 출처(기관/문서명) | URL | 기준일·버전 | 1차/2차 |
|---|---|---|---|---|
| ezdxf 최신 1.4.5, MIT, Python >=3.10(메타) / 문서는 3.11 이상 표기(불일치), classifier 3.11~3.15 | PyPI ezdxf | https://pypi.org/project/ezdxf/ , https://pypi.org/pypi/ezdxf/json | 1.4.5, 2026-10-16 (조회 2026-11-09) | 1차 |
| $INSUNITS는 모델스페이스 단위, 블록/페이퍼스페이스는 layout units, 암묵적 단위 변환 없음(INSERT 스케일 직접 계산, units.conversion_factor 제공) | ezdxf docs, Units | https://ezdxf.readthedocs.io/en/stable/concepts/units.html | stable (조회 2026-11-09) | 1차 |
| bbox: extents/multi_flat/multi_recursive; XREF·UNDERLAY·ACIS(3DSOLID 등)·RAY 미지원 및 조용히 무시, 텍스트 bbox 부정확 | ezdxf docs, bbox | https://ezdxf.readthedocs.io/en/stable/bbox.html | stable (2026-11-09) | 1차 |
| INSERT.virtual_entities()/explode(); XREF 분해 미지원, 미지원 엔티티는 무시 | ezdxf docs, insert/disassemble (검색 요약) | https://ezdxf.readthedocs.io/en/stable/blocks/insert.html , https://ezdxf.readthedocs.io/en/stable/disassemble.html | stable | 1차(요약 경유) |
| 동적 블록은 익명 `*U` 블록으로 저장됨. ezdxf에 EffectiveName 동등 기능이 있는지는 문서로 못 찾음 | ezdxf blocks 문서 / Autodesk 포럼 | https://ezdxf.readthedocs.io/en/stable/sections/blocks.html | - | 1차+2차 |
| odafc 애드온: 외부 ODA File Converter 설치 필요, R12~R2018(AC1032) 지원, Windows 기본 경로 `C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe`, 외부 실행파일 보안 주의 | ezdxf docs, odafc | https://ezdxf.readthedocs.io/en/stable/addons/odafc.html | stable (2026-11-09) | 1차 |
| ODA File Converter: GUI+CLI, 입력 폴더/출력 폴더/필터(기본 *.dwg;*.dxf)/출력 버전/재귀/Audit 인자, Windows 10+ x64 MSI | ODA 배포 페이지 | https://www.opendesign.com/guestfiles/oda_file_converter | 조회 2026-11-09 (버전·날짜 미표기) | 1차 |
| ODA File Converter는 "example project", 비회원은 **non-commercial 용도만**, 최신 버전만 공개(구버전은 회원만) | ODA FAQ | https://www.opendesign.com/node/3218 | 조회 2026-11-09 | 1차 |
| ODA Community User Agreement(2025-09): 무료 Community Application은 의도된 기능 한정 라이선스, 상용 앱의 일부로 재배포/재판매 금지. **내부 업무 사용 범위 조항은 PDF 판독 실패로 미확인** | ODA | https://www.opendesign.com/files/2025-09/ODA%20Community%20User%20Agreement%2009-2025.pdf | 2025-09 | 1차(원문 미판독, 검색 요약 경유) |
| ODA 멤버십: Commercial $3,000 초기/$2,250 연(제한적 상업 배포, Drawings/IFC 등 SDK 포함), Sustaining $7,500/$4,500, Founding $37,500/$18,000; 구독 종료 시 배포권 상실 | ODA Pricing | https://www.opendesign.com/pricing.md | 2026-09 추정(페이지 날짜 미표기) | 1차 |
| LibreDWG: GPLv3+, 베타, 읽기는 "done"이나 R2010+ 고급 엔티티 일부 스킵, 쓰기는 R2000까지; 릴리스 0.13.4/0.14 (ftp.gnu.org 목록 날짜 2026-08-31, 페이지 설명 없음) | GNU LibreDWG | https://www.gnu.org/software/libredwg/ , https://ftp.gnu.org/gnu/libredwg/ | 페이지 2024-02-04 갱신, 릴리스 목록 조회 2026-11-09 | 1차 |
| IfcOpenShell 0.9.0.post1: LGPL-3.0-or-later, requires_python >=3.10,<3.16, py314 win_amd64/win_arm64/linux/mac 휠 존재, 업로드 2026-10-15 | PyPI ifcopenshell | https://pypi.org/project/ifcopenshell/ , https://pypi.org/pypi/ifcopenshell/json | 0.9.0.post1 | 1차 |
| ifc5d: 기하 기반 수량 계산 규칙(IFC4QtoBaseQuantities.json 등) 및 `ifc5d.qto.quantify` 호출 패턴. 일부 수량(예: IfcWall footprint)이 null로 매핑된 이력, Blender 쪽과 계산 방식 불일치 사례 -> 결과는 검증 필수 | IfcOpenShell 저장소 미러 커밋(원 저장소 아님) | https://dev.glassvision.dedyn.io/Glassvision/IfcOpenShell/src/be56984e12eea42426e60719863fe1e169f96f6a/src/ifc5d | 미상 | 2차 |
| Qto_WallBaseQuantities 정의(Length는 중심선 기준 등) | buildingSMART IFC4.3 | https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Qto_WallBaseQuantities.htm | IFC4.3 ADD2(개발중 표기) | 1차 |
| RVT -> IFC: APS Model Derivative(클라우드, 기본 IFC2x3, 커스텀 pset 미지원) / Revit Automation API(클라우드). ODA BimRv는 Revit 없이 IFC 생성(SDK, 유료 멤버십) | Autodesk APS 블로그 / ODA | https://aps.autodesk.com/blog/export-ifc-rvt-using-model-derivative-api , https://www.opendesign.com/node/4080 | 2025 | 1차(요약 경유) |
| rvt-rs: Apache-2.0 클린룸 RVT 리더, 요소 단위 IFC는 Revit 2024/2025 프로젝트만 검증, "not yet a full Revit model reader"; 저장소/버전 표기 상충(docs.rs v0.3.0 vs 0.4.0) | GitHub DrunkOnJava/rvt-rs, docs.rs | https://github.com/DrunkOnJava/rvt-rs , https://docs.rs/crate/rvt/latest | 조회 2026-11-09 | 1차이나 직접 열람 못함(검색 요약) |
| Aspose.CAD for Python via .NET: Developer Small Business $783.02/1인, Site Small Business $3,915.10(10인), 재판매업체 가격, 버전 25.12 | ComponentSource (재판매) | https://www.componentsource.com/product/aspose-cad-for-python-via-net/prices | 2025-12-14 갱신 표기 | 2차 |
| AutoCAD Core Console(accoreconsole.exe): `/i` 도면, `/s` 스크립트, GUI 없음, 스크립트 내에서 DXF 저장 가능, ActiveX(COM) 미지원 | Autodesk Help 2026 / 커뮤니티 | https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core-Console/files/AUTOCAD_CORE_CONSOLE.html | 2026 | 1차+2차 |
| BricsCAD `/automation` 스위치(UI 숨김, COM 자동화/배치용), DXFOUT 명령 | Bricsys Help | https://help.bricsys.com/en-us/document/bricscad/customization/startup-options | 조회 2026-11-09 | 1차(요약 경유) |
| PyMuPDF `Page.get_drawings()`로 벡터 경로(선 "l", 사각형 "re") 추출; 라이선스 AGPL 또는 상용(Artifex) 이중 | PyMuPDF docs / Artifex | https://pymupdf.readthedocs.io/en/latest/recipes-drawing-and-graphics.html , https://pymupdf.readthedocs.io/en/latest/about.html | 조회 2026-11-09 | 1차 |
| 한국 실무: 외주 도면 서비스가 DXF/DWG/PDF 동시 전달, 마이다스캐드 DWG/DXF 호환 2000~2021 명시. 해외 업체는 "PDF보다 DWG가 속도·정확도 우위, PDF는 레이어 포함 벡터 PDF 권장" | Kmong 외주 상품, MIDAS CAD, Vertigraph 블로그 | https://www.midascad.com/mcad/archidesign , https://www.vertigraph.com/blog/architects-and-engineers-optimize-site-excavation-takeoff-by-creating-autocad-dwg-files-with-proper-layers-polylines-and-elevations-for-speed-and-accuracy | 조회 2026-11-09 | **2차(근거 약함)** |

## 선택지 비교 (DWG 읽기)
| 경로 | 비용/라이선스 | 자동화 | 품질 | 리스크 |
|---|---|---|---|---|
| A. ODA File Converter + ezdxf(odafc) | 무료 다운로드, 단 비회원 non-commercial 한정 문구 | CLI 일괄 변환, ezdxf가 래핑 | R2018(AC1032)까지 지원(odafc 문서); 최신 DWG 2018+ 계열 표기는 확인 못 함 | **상업 사용 약관 불명확**, 재배포 금지(제품에 번들 불가, 사용자가 직접 설치), 외부 exe 실행 |
| B. LibreDWG(dwg2dxf 등) | GPLv3+ (별도 프로세스 호출이면 번들 없이 사용 가능하나 배포 시 GPL 고지 필요 - 법적 판단은 CEO/사용자) | CLI | R2010+ 일부 엔티티 누락 가능, 베타 | 누락이 곧 물량 누락. 검증 장치 필요 |
| C. ODA SDK(Drawings/Teigha) | 멤버십 $3,000~/년(Commercial, 한도 있음) | 라이브러리 | 최고(원 제작 엔진) | **돈이 나가는 결정 -> 사용자** |
| D. Aspose.CAD | 약 $783/개발자(재판매가 기준) | Python(.NET) | 미검증 | 유료, 사용자 승인 필요 |
| E. AutoCAD/BricsCAD 설치 PC | 사용자가 이미 보유 시 추가비용 없음 | accoreconsole 스크립트(DXFOUT), BricsCAD /automation | 원본 엔진 | 설치 의존, 라이선스 확인, 자동화 범위 한정 |
| F. 사용자가 DXF/IFC로 직접 저장해 제공 | 무료 | 수동 1단계 | 원본 엔진 | 사용자 부담, 신뢰 가능한 폴백 |

## 확인 못 한 것 / 추가 조사 필요
- ODA Community User Agreement 본문(내부 업무 사용 가능 여부). PDF가 판독되지 않아 미확인 -> 원문 수동 열람 또는 ODA 문의 필요.
- ODA File Converter 최신 버전 번호·릴리스일·정확한 CLI 인자 순서(공식 페이지에 예시 없음. 검색 결과 간접 언급으로 27.1 정도만 추정).
- LibreDWG 0.14의 지원 버전 변화(ftp 목록 날짜만 확인, 릴리스 노트 미열람).
- ezdxf: 동적 블록 유효이름 노출 여부, ATTRIB/MTEXT/DIMENSION 값 추출 API 상세, 폴리선 길이·면적 헬퍼(ezdxf.math)는 이번에 문서 직접 확인 못 함. 샘플 도면 실측 필요.
- ezdxf Python 3.14 실제 CI/휠 동작(classifier 명시만 확인; 순수 파이썬이라 위험은 낮음 - 추정).
- IfcOpenShell 공식 문서의 Qto/ifc5d 정식 설명, IFC 내 한국 BIM 가이드 요구 속성.
- **한국 실무 도면 형식 비율**: 공식 통계/설문 근거 못 찾음. 조달청 등 발주처의 성과품 제출 형식 조항도 원문을 열지 못함("없음"이 아니라 "못 찾음").
- PDF 도면: 축척 복원, 레이어(OCG) 보존 여부, 스캔 PDF 비중은 미조사(이번 범위 밖 간단 확인만).
- rvt-rs 저장소 실체·성숙도 직접 검증.

## PDF 도면 대안 (간단)
- 벡터 PDF면 PyMuPDF `get_drawings()`로 선·사각형을 얻을 수 있으나 레이어/블록/단위 정보는 대부분 소실되고 축척은 표제란 텍스트나 사용자 입력으로 보정해야 함. 숨김 요소도 반환될 수 있음(문서 언급). 스캔(래스터) PDF는 별도 비전 기술이 필요해 MVP 제외 권장. PyMuPDF는 AGPL/상용 이중 라이선스이므로 대안(pdfplumber 등, 라이선스 미확인) 검토 필요.

## 다음 결정자에게
- **bim-ceo (Gate 2 입력 포맷 범위)**: 아래 추천안 중 선택. ODA File Converter 사용 시 상업 약관 리스크를 수용할지, 아니면 "사용자가 DXF로 저장" 폴백을 1차로 할지.
- **사용자 (돈/사실 확인)**: (a) 실제로 받는 도면이 DWG/PDF/IFC 중 무엇이고 DWG 버전(예: 2018 이후인지)은? (b) 업무 PC에 AutoCAD/BricsCAD가 있는지 (c) ODA 멤버십/Aspose 구매는 사용자 승인 사항.
- **bim-planner**: 입력 어댑터 인터페이스를 "DXF 문서 모델" 단일 내부 표현으로 두고 DWG 변환은 교체 가능한 전처리 단계로 정의.
- **cad-parser(developer)**: 공개 샘플 DXF로 ezdxf 블록 중첩·ATTRIB·$INSUNITS·bbox 실측 스파이크를 먼저 수행.

## MVP 입력 처리 추천안
**1안 (추천): DXF/ezdxf 코어 + DWG는 "변환 전처리 어댑터" (변환기 교체 가능)**
- 내부 표현은 ezdxf DXF. 입력이 DXF면 바로 처리. DWG면 (1순위) 사용자가 설치해 둔 AutoCAD/BricsCAD 또는 ODA File Converter 중 사용자 환경에서 합법적으로 쓸 수 있는 것으로 DXF 변환, (2순위) 사용자가 직접 DXF로 저장. 변환 결과의 엔티티 수를 변환 전/후 비교해 누락 경고.
- 근거: ezdxf MIT·Python 3.14 명시로 코어 리스크 낮음; DWG 변환기는 약관·비용 불확실성이 있어 코어에서 분리하는 것이 안전. 도면 외부 업로드 금지 제약도 충족(전부 로컬).
- 약점: 사용자 변환 단계 또는 ODA 약관 확인 필요, 동적 블록·XREF는 별도 경고/수동 보정.

**2안: IFC 우선 (IfcOpenShell) + DXF는 후순위**
- IfcOpenShell(LGPL, py314 휠 확인)로 Qto 직접 읽기. 단 적산 담당자가 실제로 IFC를 받는지 불확실하고, 한국 일반 실무에서 DWG/PDF가 더 흔할 것이라는 정황(2차 근거 약함)과 어긋날 가능성. 사용자가 BIM(IFC/RVT) 중심 업무임을 확인하면 채택.

**비추천**: LibreDWG 단독(엔티티 누락 위험), 상용 SDK(비용 -> 사용자 승인 없이는 불가), PDF 단독(레이어·단위 소실).
