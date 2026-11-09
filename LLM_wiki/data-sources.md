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
| 건설공사 표준품셈 | 공종별 투입량·재료 할증(공통부문 제1장 "재료 및 노임의 할증"). 2026-01-01 적용판(국토부 2025-12-23 공고). 원문 파일 경로는 미확인 | https://cost.kict.re.kr (KICT 공사비원가관리센터) / 국토부 누리집 | 무료 열람(약관 미확인) | 확인됨(사이트)/파일 경로 미확인 | 2026-11-09 |
| 전기·정보통신·소방 표준품셈 | 별도 발행본(2026판 존재 보도) | https://04noti.com/2026%EB%85%84-%EC%A0%84%EA%B8%B0%EA%B3%B5%EC%82%AC-%ED%91%9C%EC%A4%80%ED%92%88%EC%85%88/ (2차) | 확인 필요 | 후보 | 2026-11-09 |
| 전기부문 표준품셈 (대한전기협회 표준품셈 관리시스템) | 국토부 고시 아님, 대한전기협회 유지·공표. 자료실에 전문·제개정 이력. 이용약관 본문·재가공 허용 여부 미확인, ALL RIGHTS RESERVED 표기 | https://sec.kea.kr | 열람 로그인 여부 미확인 | 확인됨(위치)/이용조건 미확인 → 사용 금지 유지 | 2026-11-09 |
| 2026 하반기 전기부문 표준품셈 제·개정 (2026-07-01 발표) | 제3자(한국표준품셈정보원) 재게시, PDF 첨부, PDF 본문 미확인 | https://www.kseis.co.kr/bbs/data/dataDetail.do?bbs_seq=39103500740142 | 미확인 | 확인됨(2차) | 2026-11-09 |
| 예정가격작성기준 (계약예규) | law.go.kr 제목상 재정경제부계약예규 제171호, 2026-08-25 시행(이전 제785호 표기와 불일치, 재확인 필요). 원 미만 절사 조문은 못 찾음 | https://www.law.go.kr (행정규칙) | 무료 | 위치만 확인, 본문 미확인 | 2026-11-09 |
| 조달청_나라장터 가격정보현황서비스 (OpenAPI) | 시설공통자재·시장시공가격·표준시장단가 등 11개 오퍼레이션, Base `https://apis.data.go.kr/1230000/ao/PriceInfoService` | https://www.data.go.kr/data/15129415/openapi.do | 무료, data.go.kr 키 필요(가입·신청은 사용자 확인) | 확인됨 | 2026-11-09 |
| 조달청 시설공통자재 가격정보 내역 (CSV) | 13컬럼, 수정 2025-08-18 | https://www.data.go.kr/data/15083244/fileData.do | 무료, 로그인 불필요 여부 미확인 | 확인됨 | 2026-11-09 |
| 조달청_공사원가_표준시장단가 (CSV) | 세부공종코드·재료/노무/경비/합계, 2025-11-05 | https://www.data.go.kr/data/15151298/fileData.do | 무료 | 확인됨 | 2026-11-09 |
| 조달청 표준공사코드(세부공종코드·자원코드) | 내역서 품명·규격·단위 코드 체계(출처 npccs.g2b.go.kr) | https://www.data.go.kr/data/15151273/fileData.do , https://www.data.go.kr/data/15151393/fileData.do | 무료 | 확인됨 | 2026-11-09 |
| 조달청 시설자재가격 발표 | 연 2회(최근 2026-10-01, 6,584품목). 공개: g2b.go.kr, npccs.g2b.go.kr | https://www.koscaj.com/news/articleView.html?idxno=326762 (2차) | 무료 | 확인됨(보도) | 2026-11-09 |
| 대한건설협회 시중노임단가(임금실태조사) | 반기 공표. 2026 하반기 2026-09-01 적용, 132직종, PDF | https://www.cak.or.kr/download.do?uuid=b7c2d717-6f9a-44aa-918e-a7e8900b8545.pdf | 무료, 로그인 불필요 | 확인됨(PDF 본문 숫자 미확인) | 2026-11-09 |
| 대한건설협회 건설임금 메뉴 | 경로: 지원·사업 → 건설적산기준 → 건설임금 (2026 상반기 공고문 기준) | https://info.cak.or.kr/lay1/bbs/S1T9C12/A/2/view.do?article_seq=153489&condition=&cpage=1&keyword=&rows=10 | 무료 | 확인됨 | 2026-11-09 |
| 물가정보지(종합물가정보·물가자료) | 월간 인쇄물로 유통(서점 약 27,000원/호, 지표용). 온라인 요금·API는 못 찾음 | https://www.11st.co.kr/products/5175436431 (2차) | 유료 | 유료·사용 전 CEO→사용자 확인 | 2026-11-09 |
| 표준시장단가 | 국토부·KICT 공고(상·하반기). 2026 상반기 2025-12-23 공고(+2.98%), 하반기 2026-05-08 공고 보도. 수치 미확인 | https://v.daum.net/v/20251222110205258 (2차) / cost.kict.re.kr | 무료 열람 | 확인됨(위치) | 2026-11-09 |
| 예정가격 작성기준 / 조달청 공사원가계산 제비율 | 원가계산 근거(계약예규 제785호, 2025-05-01 시행으로 해설됨). 2026 제비율 원문 미확인, 조달청 정책자료 게시판 | https://pps.go.kr/kor/bbs/list.do?key=00033 / law.go.kr | 무료 | 위치만 확인 | 2026-11-09 |
| 나라장터 공공데이터개방표준서비스 | 입찰·낙찰·계약 정보(가격표 아님) | https://www.data.go.kr/en/data/15058815/openapi.do | 무료, 키 | 확인됨(용도 부적합) | 2026-11-09 |

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
