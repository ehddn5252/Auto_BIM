# Data Sources

> `bim-researcher`가 확인한 출처를 한 줄씩 **추가**한다. 각 줄은 실제로 접속·확인한 날짜가 있어야 한다.
> 상태: 후보(미확인) / 확인됨 / 유료·로그인 필요(사용 전 CEO→사용자 확인) / 폐기

## 포맷·라이브러리

| 이름 | 용도 | URL | 라이선스/비용 | 상태 | 확인일 |
|---|---|---|---|---|---|
| ezdxf | Python DXF 읽기/쓰기. 1.4.5(2026-10-16), py3.14 classifier | https://ezdxf.readthedocs.io | MIT | 확인됨 | 2026-11-09 |
| ODA File Converter | DWG ↔ DXF 로컬 변환(GUI+CLI, Win10+ x64) | https://www.opendesign.com/guestfiles/oda_file_converter | 무료 다운로드, 단 FAQ상 비회원 non-commercial 한정(내부 업무 사용 여부 미확인) | 확인됨(약관 리스크 있음) | 2026-11-09 |
| ODA FAQ (File Converter 용도) | non-commercial 문구 근거 | https://www.opendesign.com/node/3218 | — | 확인됨 | 2026-11-09 |
| ODA Pricing | SDK 멤버십 $3,000~/년 | https://www.opendesign.com/pricing.md | 유료 | 유료·사용자 확인 필요 | 2026-11-09 |
| IfcOpenShell | Python IFC 읽기·수량. 0.9.0.post1, py314 win_amd64 휠 | https://pypi.org/project/ifcopenshell/ | LGPL-3.0-or-later | 확인됨 | 2026-11-09 |
| LibreDWG | 오픈소스 DWG 라이브러리, 베타, R2010+ 일부 엔티티 스킵 | https://www.gnu.org/software/libredwg/ | GPLv3+ | 확인됨 | 2026-11-09 |
| ezdxf odafc 애드온 | ODA FC 래퍼(R12~R2018) | https://ezdxf.readthedocs.io/en/stable/addons/odafc.html | MIT(애드온) | 확인됨 | 2026-11-09 |
| PyMuPDF | 벡터 PDF 경로 추출 get_drawings | https://pymupdf.readthedocs.io/en/latest/about.html | AGPL/상용 이중 | 확인됨 | 2026-11-09 |
| Aspose.CAD (Python via .NET) | 상용 CAD 읽기 | https://www.componentsource.com/product/aspose-cad-for-python-via-net/prices | 유료(약 $783/개발자, 재판매가) | 유료·사용자 확인 필요 | 2026-11-09 |
| AutoCAD Core Console | accoreconsole DWG→DXF 스크립트 | https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core-Console/files/AUTOCAD_CORE_CONSOLE.html | AutoCAD 라이선스 필요 | 확인됨 | 2026-11-09 |
| rvt-rs | 오픈소스 RVT 리더(부분 지원) | https://github.com/DrunkOnJava/rvt-rs | Apache-2.0(검색 요약) | 후보(직접 미열람) | 2026-11-09 |

## 적산 기준·단가

| 이름 | 내용 | URL | 비용 | 상태 | 확인일 |
|---|---|---|---|---|---|
| 건설공사 표준품셈 | 공종별 투입량 기준 | (조사 필요) | — | 후보 | — |
| 조달청 가격정보 | 공공 자재 가격 | (조사 필요) | — | 후보 | — |
| 대한건설협회 시중노임단가 | 직종별 노임 | (조사 필요) | — | 후보 | — |
| 물가정보지(종합물가정보·물가자료) | 자재 시중 가격 | (조사 필요) | 유료 가능성 | 후보 | — |
| 표준시장단가 | 공종별 단가 | (조사 필요) | — | 후보 | — |

## 유사 제품·참고

| 이름 | 메모 | URL | 상태 | 확인일 |
|---|---|---|---|---|
| 포비콘 오토적산 (국내) | DWG 직접 분석 AI 물량산출, 골조 사례 중심, 가격 미공개, 정확도 99%는 회사 주장 | https://view.asiae.co.kr/article/2026032013582809566 | 확인됨(2차 기사) | 2026-11-09 |
| 달파 AI 스마트 견적 (국내) | 빈 물량내역서에 단가 추천, 도면 인식 아님 | https://www.asiae.co.kr/en/article/2025070808325330224 | 확인됨(2차 기사) | 2026-11-09 |
| Togal.AI | PDF 기반 AI 면적·길이·카운트, $299/월/사용자(연 결제, 벤더) | https://www.togal.ai/llms.txt | 확인됨(1차 벤더) | 2026-11-09 |
| RIB CostX | DWG/DWFx/RVT/IFC 2D·3D 물량, 블록/레이어 활용, 가격 미확인 | https://www.rib-software.com/en/2d-3d-takeoff-estimating | 후보(검색 요약만) | 2026-11-09 |
| PlanSwift / Bluebeam / Drawer AI / Kreo / STACK | 해외 PDF 기반 takeoff, 가격은 2차 글만 | https://www.constructconnect.com/blog/ai-powered-takeoff-and-estimating-software-a-contractors-guide-to-the-top-players-in-2026 | 후보(2차) | 2026-11-09 |

## 공개 샘플 도면 출처
| 이름 | 포맷 | URL | 라이선스 | 로그인 | 상태 | 확인일 |
|---|---|---|---|---|---|---|
| buildingSMART Sample-Test-Files | IFC 2x3/4/4.3 | https://github.com/buildingSMART/Sample-Test-Files | CC BY 4.0 | 불필요 | 확인됨 | 2026-11-09 |
| IfcOpenShell/files | IFC(이슈 재현용) | https://github.com/IfcOpenShell/files | 미확인 | 불필요 | 확인됨(라이선스 불명) | 2026-11-09 |
| OSArch AEC Open Data directory | 링크 모음 | https://wiki.osarch.org/aec-open-data-directory/ | 각 항목별 | 불필요 | 확인됨(2차) | 2026-11-09 |
| OpeningDesign | 오픈 건축 프로젝트 | https://openingdesign.com/ | CC-BY-SA 4.0(위키 기재) | 불필요 추정 | 후보 | 2026-11-09 |
| WBDG Duplex Apartment | IFC 등 | https://www.wbdg.org/node/9165 | 미확인 | 미확인 | 후보 | 2026-11-09 |
| 나라장터 입찰공고 설계서 전자열람 | 공고별(도면+물량내역서 가능) | https://www.koscaj.com/news/articleView.html?idxno=92417 | 미확인 | 미확인 | 후보(2016 기사, 현행 확인 필요) | 2026-11-09 |
| FloorPlanCAD | CAD 도면 데이터셋 | https://floorplancad.github.io | 주석 CC BY-NC, 도면 저작권 미보유 | 불명 | 사용 제한(비상업) | 2026-11-09 |
