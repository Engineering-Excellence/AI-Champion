# AGENTS.md — AI-Champion Codebase Guide

## Project Overview

**AI-Champion** is a hands-on workshop project for the AI Champion(블루) program, covering three daily tracks plus a certification-assessment practice area:

- **Day 1** (`champion_blue/day1/`) — 생성형AI를 활용한 콘텐츠 및 문서자동화
- **Day 2** (`champion_blue/day2/analysis/`, `champion_blue/day2/agent/`) — 생성형AI를 활용한 데이터분석 + 에이전트·GUI 앱
- **Day 3** (`champion_blue/day3/`) — 외부 Open API·MCP 연동 (서울 지하철 실시간, 나라장터 입찰공고 MCP 서버)
- **인증평가 (`champion_blue/set1/`)** — 3과목 예제문제 풀이(연습세트01); **실전 문제 세트는 `test_blue/`** (git 미추적 작업 공간)

The `python_exercise/` directory contains standalone Jupyter notebook exercises that run independently of the daily tracks.

Primary environment: Python on Windows, using Jupyter notebooks and **conda** (`base` environment). Korean language data is pervasive throughout.

---

## Directory Layout

```
AI-Champion/
├── champion_blue/
│   ├── day1/                         # Day 1: 콘텐츠 및 문서자동화
│   │   ├── input/
│   │   │   ├── 사업자등록신청서.gif         # 이미지→HTML 변환 실습 원본
│   │   │   └── public_sector_analysis_dataset_3000x20.xlsx
│   │   ├── output/
│   │   │   ├── 성실납세.jpg / ai_cafe.png   # 이미지 생성 결과물
│   │   │   ├── 사업자등록신청서_*.html      # 이미지→HTML 변환 결과물
│   │   │   ├── statistics.xlsx             # 엑셀 분석 통계표
│   │   │   ├── chart_01.png … chart_10.png # 분석 차트
│   │   │   ├── analysis.docx               # 영문 분석 보고서
│   │   │   └── 분석_보고서.docx            # 한글 분석 보고서
│   │   ├── analysis_claude.py          # Streamlit 대화형 대시보드
│   │   ├── analysis_chatgpt.py         # 배치 분석 스크립트
│   │   └── snake_game.py               # Tkinter 지렁이 게임
│   │
│   ├── day2/                         # Day 2: 데이터분석 + 에이전트·GUI
│   │   ├── analysis/                   # Day 2-A/B: 기초 분석 + 머신러닝 (구 day2 + day2_analysis 통합)
│   │   │   ├── input/
│   │   │   │   ├── 국토교통부_전국 버스정류장 위치정보_20251031.csv
│   │   │   │   ├── excel_100_files/        # 가상 월별 보고서 100개
│   │   │   │   ├── 2025 지방세통계연감.pdf
│   │   │   │   └── public_sector_analysis_dataset_3000x20.xlsx
│   │   │   ├── output/
│   │   │   │   ├── merged_all.xlsx         # 100개 파일 병합 결과
│   │   │   │   ├── bus_stop_heatmap.html   # 전국 버스정류장 히트맵
│   │   │   │   ├── 전국_버스정류장_분석_보고서.pdf  # 8페이지 A4 보고서
│   │   │   │   ├── images/                 # 그래프01~06 (지방세 분석)
│   │   │   │   ├── tables/                 # 표01~10 (지방세 집계)
│   │   │   │   └── urgency_model_report.png  # 4알고리즘 비교 분석 보고서
│   │   │   ├── blue_exercise.ipynb         # 엑셀 생성·병합 실습
│   │   │   ├── dataAnalysis_exercise.ipynb # CSV 분석·히트맵·보고서 실습
│   │   │   ├── generate_report.py          # PDF 보고서 생성 스크립트
│   │   │   ├── supervisedLearning.ipynb        # 지도학습: 분류+회귀
│   │   │   ├── urgency_classification_model.ipynb  # 4알고리즘 F1 비교
│   │   │   └── 지방세통계연감_analysis.ipynb   # PDF 통계연감 분석
│   │   │
│   │   └── agent/                     # Day 2-C: 에이전트·GUI 앱 (구 day2_agent)
│   │       ├── dashboard/
│   │       │   ├── generate_dashboard.py   # 민원 데이터 HTML 대시보드 생성
│   │       │   └── dashboard.html          # 출력 HTML (폐쇄망 완전 자체 포함)
│   │       ├── file_manager/
│   │       │   ├── file_manager.py         # Tkinter 파일 관리자 (탐색기 스타일)
│   │       │   └── build_exe.bat           # PyInstaller 빌드 스크립트 (build/·dist/ 는 gitignore)
│   │       └── news_reader/
│   │           ├── news_gui.py             # Tkinter RSS 뉴스 리더
│   │           ├── news_web.html           # 동일 기능 웹 버전
│   │           └── build_exe.bat           # PyInstaller 빌드 스크립트 (build/·dist/ 는 gitignore)
│   │
│   ├── day3/                         # Day 3: 외부 Open API·MCP 연동
│   │   ├── api/seoulmetro/
│   │   │   ├── generate_metro_html.py  # 서울 지하철 실시간 도착 HTML 생성기
│   │   │   ├── seoul-metro-schematic.svg  # 노선도 SVG (인라인 임베드)
│   │   │   ├── seoul_metro_realtime.html  # 출력 HTML (서버리스, API키 클라이언트 입력)
│   │   │   └── Open API 샘플가이드_20220406.pdf
│   │   ├── mcp/mcp-narajangter/       # 나라장터 입찰공고 MCP 서버 (TypeScript/Node)
│   │   │   ├── src/index.ts            # MCP 서버 구현 (도구 5종)
│   │   │   ├── dist/index.js           # 빌드 산출물 (gitignore)
│   │   │   ├── node_modules/           # (gitignore)
│   │   │   ├── package.json / tsconfig.json / .env.example
│   │   │   └── README.md               # 설치·인증키·Claude Desktop 연동 가이드
│   │   ├── hwpx/                      # (placeholder, 비어있음)
│   │   └── word/                      # (placeholder, 비어있음)
│   │
│   └── set1/                         # 인증평가 예제문제 (연습세트01, 3과목)
│       ├── subj1/  # 1과목: 보도자료(md) 분석 — analyze.py, 문제지.pdf, 첨부/
│       ├── subj2/  # 2과목: 데이터분석 보고서 — generate_report.py, 분석_보고서.docx, images/
│       └── subj3/  # 3과목: 정적 페이지 + 자동화 — index.html, solution.py, 제출물.md
│
├── test_blue/                        # ★ 실전 문제 세트 (git 미추적 작업 공간)
│   └── set1/                          # set1과 동일한 3과목 구조 (subj1~3)
│
├── python_exercise/                  # 독립 실습 노트북
│   ├── python_exercise.ipynb
│   ├── 2026년 예산 사업설명자료.pdf
│   ├── 행정안전부_지역별(행정동) 성별 연령별 주민등록 인구수_20260531.csv
│   ├── extracted_tables_page100_150.xlsx
│   └── fake_excels/merged_data.xlsx
├── .editorconfig                     # 에디터 코딩 스타일 통일
├── .gitattributes                    # 줄 끝 정규화, 바이너리 지정
├── .gitignore
├── AI챔피언_제도_요약.docx           # 워크샵 제도 참고 자료
├── AGENTS.md                         # AI 코딩 어시스턴트용 코드베이스 가이드
├── CLAUDE.md                         # Claude Code 시작 시 로드되는 프로젝트 지침
├── README.md
├── environment.yml                   # conda 환경 명세 (단일 소스)
└── requirements.txt                  # pip 폴백 패키지 목록
```

---

## Day 1 — 생성형AI를 활용한 콘텐츠 및 문서자동화

| 실습 | 산출물 |
|------|--------|
| NotebookLM Infographic | `output/성실납세.jpg`, `output/ai_cafe.png` |
| 이미지(GIF) → HTML 변환 | `output/사업자등록신청서_*.html` |
| 지렁이 게임 생성 | `snake_game.py` |
| 엑셀 데이터 분석 보고서 | `statistics.xlsx`, `chart_01~10.png`, `*.docx` |

### 엑셀 분석 스크립트 (`analysis_claude.py` vs `analysis_chatgpt.py`)

Day 1의 엑셀 분석 보고서 실습 예시로, 같은 입력 파일에 대해 두 가지 구현 방식을 보여준다.

| | `analysis_claude.py` | `analysis_chatgpt.py` |
|---|---|---|
| **UI** | Streamlit 웹 앱 (대화형) | CLI 배치 스크립트 |
| **출력** | 브라우저 대시보드 + `.docx` 다운로드 | `output/` 폴더에 xlsx·png·docx |
| **차트 선택** | 사이드바 체크박스로 사용자 선택 | 고정 10종 자동 생성 |
| **실행** | `streamlit run champion_blue/day1/analysis_claude.py` | `python champion_blue/day1/analysis_chatgpt.py` |

`analysis_claude.py` 핵심 구조:
- `load_data(file)` — `@st.cache_data`; 수치/범주/날짜 컬럼 자동 분류 (datetime 변환 80% 임계값)
- `STAT_TABLE_REGISTRY` — `name → lambda(df, ...)` 형태의 5개 통계표
- `CHART_REGISTRY` — `name → fn(df, ...)` 형태의 11개 차트 함수; `Figure` 또는 `None` 반환
- `build_report(...)` — `python-docx` 문서 조립 후 `io.BytesIO` 반환 (Streamlit 다운로드용)

---

## Day 2-A — 기초 데이터분석 (`champion_blue/day2/analysis/`)

### 실습 1: 가상 엑셀 100개 생성·병합 (`blue_exercise.ipynb`)

- `excel_100_files/` 에 `monthly_report_001.xlsx` … `_100.xlsx` 생성
- 각 파일: 시트 3개 (직원명단 9열 / 급여내역 8열 / 부서요약 4열), 행 수 10~30 랜덤
- `openpyxl`로 헤더 스타일 적용 (파란색 배경, 흰색 굵은 글씨)
- 병합: 출처파일 컬럼 추가 후 시트별 `pd.concat()` → `output/merged_all.xlsx`

### 실습 2: CSV 버스정류장 분석·히트맵·PDF 보고서 (`dataAnalysis_exercise.ipynb`)

- 데이터: 국토교통부 전국 버스정류장 227,065행 × 9열 (EUC-KR 인코딩)
- 유효 좌표 필터링 (위도 33~39, 경도 124~132); 12개 이상치 제거
- `folium` + `HeatMap` → `output/bus_stop_heatmap.html`
- `generate_report.py`로 8페이지 A4 PDF 보고서 생성:
  표지/목차 · 데이터 개요 · 광역단체 분포 · 상위 25개 도시 · 전국 산포도 · 밀도 분포 · BIS 현황 · 결론

---

## Day 2-B — 머신러닝 예측 모델 (`champion_blue/day2/analysis/`)

공통 입력 데이터: `public_sector_analysis_dataset_3000x20.xlsx` (공공 부문 민원 3,000건 × 20개 변수)

### `supervisedLearning.ipynb` — 지도학습 3종

| 태스크 | 타깃 | 모델 | 주요 성능 |
|--------|------|------|-----------|
| 분류 | 지연여부 (0/1) | Gradient Boosting Classifier | AUC 기준 |
| 회귀 A | 만족도점수 | Gradient Boosting Regressor | R² 기준 |
| 회귀 B | 행정비용추정(만원) | Lasso 회귀 + StandardScaler | R² 기준 |

공통 피처 15개: 수치형(민원복잡도·담당인력수 등) + 인코딩된 범주형(기관유형·지역·서비스분야 등) + 파생변수(접수월·분기)

### `urgency_classification_model.ipynb` — 비지도학습 4알고리즘 F1 비교

- 타깃: `긴급처리여부` (긴급·높음=1, 보통·낮음=0; 불균형 26.4% : 73.6%)
- 4가지 알고리즘 비교: 로지스틱회귀 · 의사결정트리 · 랜덤포레스트 · 그래디언트부스팅
- 평가 지표: F1(weighted), F1(긴급), AUC, CV-F1(5-fold), Accuracy
- 최우수 모델 자동 선정 → `output/urgency_model_report.png` (9패널 시각화)

### `지방세통계연감_analysis.ipynb` — PDF 통계 분석

- 입력: `2025 지방세통계연감.pdf`
- 출력: 그래프 6종 (`output/images/`), 집계 테이블 10종 (`output/tables/`)

---

## Day 2-C — 에이전트·GUI 앱 (`champion_blue/day2/agent/`)

### `dashboard/generate_dashboard.py` — 민원 데이터 HTML 대시보드

- 입력: `public_sector_analysis_dataset_3000x20.xlsx`
- 출력: `dashboard.html` — 15개 통계표 + 10개 그래프, Chart.js 완전 자체 포함 (폐쇄망 배포 가능)
- 주요 통계표: 기술통계 요약, 기관유형별/지역별/서비스분야별/민원채널별 집계 등

### `file_manager/file_manager.py` — Tkinter 파일 관리자

- 탐색기 스타일 2패널 레이아웃 (왼쪽 원본 / 오른쪽 대상)
- 기능: 복사·잘라내기·붙여넣기·삭제·이름변경·새 폴더·파일 열기·속성 보기
- 드라이브 선택, 주소 표시줄 직접 입력, 이모지 아이콘 매핑
- 고해상도 DPI 지원 (`ctypes.windll.shcore.SetProcessDpiAwareness(1)`)
- `build_exe.bat` → PyInstaller로 `dist/파일관리자.exe` 단일 파일 배포

### `news_reader/news_gui.py` — 정책뉴스 RSS 리더

- RSS 피드 4종: 정책뉴스 / 보도자료 / 오피니언 / 칼럼 (korea.kr)
- 다크 테마 Tkinter GUI; 멀티스레드(`ThreadPoolExecutor`)로 병렬 피드 수집
- `news_web.html` — 동일 기능의 웹 버전 (오프라인 동작)
- `build_exe.bat` → PyInstaller로 `dist/정책뉴스리더.exe` 단일 파일 배포

---

## Day 3 — 외부 Open API·MCP 연동 (`champion_blue/day3/`)

### `api/seoulmetro/generate_metro_html.py` — 서울 지하철 실시간 도착 정보

- 서울열린데이터광장 실시간 지하철 도착 API(OA-12601)를 사용하는 **단일 HTML** 생성기
- `seoul-metro-schematic.svg` 노선도를 HTML에 인라인 임베드 → `seoul_metro_realtime.html` 출력
- **서버리스 제약**: 별도 백엔드 없이 브라우저에서 직접 API 호출; API 키는 실행 시 사용자가 입력
- 실행: `python champion_blue/day3/api/seoulmetro/generate_metro_html.py`

### `mcp/mcp-narajangter/` — 나라장터 입찰공고 MCP 서버 (TypeScript/Node)

- 조달청 "나라장터 입찰공고정보서비스" REST API를 Claude Desktop/Code에서 자연어로 검색·조회
- 스택: TypeScript + `@modelcontextprotocol/sdk` **1.28.0 고정** (1.29.0은 self-import 배포 버그로 기동 실패)
- 제공 도구 5종: `search_it_bids` · `get_bid_detail` · `get_recent_it_bids` · `search_bids_by_org` · `list_closing_soon_bids`
- 인증키는 `.env`(`NARA_SERVICE_KEY`) 또는 Claude Desktop `env` 블록으로 주입 (Encoding/Decoding 키 자동 판별)
- 빌드/실행: `npm install` → `npm run build` → `dist/index.js` (stdio 통신). 상세는 해당 폴더 `README.md` 참조
- `node_modules/`, `dist/` 는 gitignore

### `hwpx/`, `word/` — 문서 자동화 placeholder (현재 비어있음)

---

## 인증평가 — 3과목 실무 수행평가

블루 인증평가는 3개 과목의 실무 과제로 구성된다. 각 과목은 문제지(`문제지.pdf` 또는 `prob*.jpg`)와 첨부 데이터가 주어지고, AI 도구로 산출물을 작성해 제출한다.

| 과목 | 유형 | 대표 산출물 |
|------|------|-------------|
| **1과목** | 문서/보도자료 분석 자동화 | `analyze.py` (md 파싱·집계) |
| **2과목** | 데이터분석 + 보고서 | 차트 5종(`images/`) + `분석_보고서.docx` |
| **3과목** | 정적 웹페이지 + 자동화 스크립트 + 배포 | `index.html`, `solution.py`, `결과_요약.csv`, `제출물.md` |

### `champion_blue/set1/` — 예제문제 풀이 (연습세트01, git 추적)

3과목 형식을 익히기 위한 **모범 풀이 예시**. 실행 스크립트와 산출물이 함께 커밋되어 있다.

- `subj1/analyze.py` — 표준 라이브러리(`re`·`csv`)만으로 보도자료 md 헤더 파싱: 부서 종류 수, 최장 본문 부서, "N억 원" 합계, 최초 발표일 부서 산출
- `subj2/generate_report.py` — CSV 병합 → 결측/IQR 이상치 제거 → 분류 4종(LogReg·DT·RF·KNN) F1 비교 → 차트 5종 + `분석_보고서.docx`
- `subj3/` — CSV 500건을 임베드한 정적 검색·필터 `index.html` + RSS(korea.kr) 임베드; 표준 라이브러리만 쓰는 `solution.py`가 요약 통계를 `결과_요약.csv`로 출력

### `test_blue/` — ★ 실전 문제 세트 (git 미추적 작업 공간)

`set1/`과 **동일한 3과목 구조**(`set1/subj1~3`)의 실전 연습 문제. `.gitignore`에는 없지만 저장소에 커밋하지 않는 작업 공간으로 운영한다 — 여기에 자신의 풀이·산출물을 작성한다.

- `subj1/` — 보도자료 md(1·2차분) + `부서_사전.json`·`정책영역_사전.json`, `부서별_자료수.csv`
- `subj2/` — `사업성과_현황.csv`·`정책사업_현황.csv` → `분석_보고서.docx`
- `subj3/` — `재정자립도_현황.csv`·`지역균형발전_사업.csv` + 카드뉴스 이미지 → `산출물1_정적페이지/`(index.html·data.js·rss.js) + `solution.py`

---

## python_exercise — 독립 실습 노트북

`python_exercise.ipynb`는 `#%%` 셀 마커 사용. **변수 의존 시 처음부터 재실행 필요.**

| 실습 | 내용 |
|------|------|
| PDF 기초 | `fitz.open()`, `page.get_text()`, 정규식 파싱 |
| PyMuPDF 추출 | `page.find_tables()`, "□"(U+25A1) 표시 섹션 타깃 |
| 배치 PDF→Excel | 100~150페이지 추출 → `extracted_tables_page100_150.xlsx` |
| Excel 병합 | 100개 파일 `pd.concat()` → `fake_excels/merged_data.xlsx` (`PERFORM_DELETE` 가드) |
| CSV 분석 | 다중 인코딩 fallback(UTF-8→CP949→EUC-KR→Latin1), `summarize_df()` |
| 지렁이 게임 | `subprocess`로 `snake_game.py` 실행 |

---

## Korean Language Handling

- **CSV 인코딩**: `encoding="cp949"` 또는 `"euc-kr"` 명시; UTF-8 가정 금지
- **자동 감지**: `chardet.detect()`로 앞 100KB 샘플링 후 결정 (신뢰도 99% 확인)
- **파일 경로**: `pathlib.Path` 또는 raw string 사용; 경로 내 한글 문자 흔함
- **PDF 기호**: "□"(U+25A1)이 추출 대상 섹션 표시
- **폰트**: matplotlib 한글 레이블을 위해 `plt.rcParams["font.family"] = "Malgun Gothic"` 필수

---

## Dependencies

| 패키지 | 용도 | 설치 |
|--------|------|------|
| `pymupdf` | PDF 파싱, 표 감지 | conda |
| `pandas` | DataFrame, Excel I/O | conda |
| `numpy` | 수치 연산, 난수 생성 | conda |
| `streamlit` | 웹 UI (day1/analysis_claude.py) | conda |
| `seaborn` | 통계 차트 | conda |
| `matplotlib` | 기본 플로팅 | conda |
| `python-docx` | Word 보고서 생성 | conda |
| `openpyxl` | xlsx 읽기/쓰기 | conda |
| `scikit-learn` | 머신러닝 (지도학습, 모델 평가) | conda |
| `folium` | 지도 시각화 (히트맵) | conda |
| `chardet` | 파일 인코딩 자동 감지 | conda |
| `faker` | 가상 데이터 생성 (`Faker('ko_KR')`) | conda |
| `pyinstaller` | GUI 앱 EXE 배포 | conda |
| `tkinter` | GUI 앱 (stdlib, 별도 설치 불필요) | — |

> **Day 3 MCP 서버(`mcp-narajangter`)는 Python이 아닌 Node.js 18+/TypeScript 스택**이다. conda/pip와 무관하게 해당 폴더에서 `npm install`로 의존성을 설치한다 (`@modelcontextprotocol/sdk` 1.28.0 고정).

### 환경 파일 역할 구분

| 파일 | 형식 | 읽는 도구 | 역할 |
|------|------|-----------|------|
| `environment.yml` | YAML | conda | **단일 소스** — 환경 생성·재현의 기준 |
| `requirements.txt` | 텍스트 | pip | **폴백** — conda 없이 pip만 사용하는 환경 전용 |

### 설치 방법

```powershell
# conda (권장): environment.yml을 단일 소스로 사용
conda env create -f environment.yml
conda activate ai-champion

# pip (폴백): conda를 사용할 수 없는 경우에 한함
pip install -r requirements.txt
```

Python 3.13 사용. 노트북 내 누락 패키지는 `ensure_package()`로 인라인 설치.

---

## Common Pitfalls

| 증상 | 해결책 |
|------|--------|
| PDF 텍스트 추출 빈 문자열 | 이미지 기반 또는 암호화 PDF; `page.get_text()` 길이로 사전 확인 |
| Excel 병합 컬럼 불일치 | 첫 파일의 `first_cols`를 기준으로 `df.reindex(columns=first_cols)` 적용 |
| CSV `UnicodeDecodeError` | CP949 → EUC-KR → Latin1 순서로 fallback 루프 |
| 대용량 CSV 메모리 오류 | `pd.read_csv(chunksize=...)` 청크 읽기 |
| 실수로 파일 삭제 | 기본값 `PERFORM_DELETE = False`; dry-run 확인 후 `True`로 변경 |
| 차트 한글 깨짐 | 플롯 호출 전 `plt.rcParams["font.family"] = "Malgun Gothic"` 설정 |
| Streamlit 앱 오류 | 저장소 루트에서 실행: `streamlit run champion_blue/day1/analysis_claude.py` |
| EXE 빌드 후 한글 경로 오류 | PyInstaller spec 파일에서 `datas`, `hiddenimports` 한글 경로 처리 확인 |

---

## Git 규칙 — 커밋 메시지·버전 태그

### 커밋 메시지: Conventional Commits

모든 커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/) 형식을 따른다.

```
<type>(<scope>): <설명>

[본문 — 선택]

[꼬리말 — 선택, BREAKING CHANGE 등]
```

- **type** (필수, 영문 소문자): `feat` 기능 추가 · `fix` 버그 수정 · `docs` 문서 · `refactor` 리팩터링 · `test` 테스트 · `chore` 잡무·설정 · `build` 빌드/의존성 · `ci` CI · `style` 포매팅 · `perf` 성능
- **scope** (선택): 영향 범위. 이 저장소에서는 폴더 기준을 권장 — `day1` · `day2` · `day3` · `mcp` · `set1` 등
- **설명** (필수): 한글 사용 가능. 명령형·현재형, 마침표 없이 간결하게
- **BREAKING CHANGE**: 하위호환이 깨지면 꼬리말에 `BREAKING CHANGE: …` 명시 (SemVer MAJOR 증가 근거)

예시:
```
docs(day3): 나라장터 MCP 서버 설치 가이드 추가
feat(day2): 버스정류장 히트맵 생성 스크립트 추가
fix(mcp): sdk 1.29.0 self-import 오류로 1.28.0 고정
chore: git 커밋 인코딩 utf-8 고정
```

### 버전 태그: SemVer

릴리스 태그는 [Semantic Versioning](https://semver.org/) `vMAJOR.MINOR.PATCH` 형식을 사용한다 (`v` 접두사 포함).

- **MAJOR** — 하위호환이 깨지는 변경 (커밋의 `BREAKING CHANGE`와 대응)
- **MINOR** — 하위호환되는 기능 추가 (`feat`)
- **PATCH** — 하위호환되는 버그 수정 (`fix`)

```bash
git tag -a v1.2.0 -m "day3 MCP 서버 추가"
git push origin v1.2.0
```

### 인코딩: UTF-8 (한글 깨짐 방지)

커밋 메시지·문서·소스 파일은 모두 **UTF-8**로 저장한다. 저장소에 아래 git 설정이 적용되어 있다.

```bash
git config i18n.commitEncoding utf-8
git config i18n.logOutputEncoding utf-8
```

- **Windows PowerShell 주의**: `Out-File`/`Set-Content`의 기본 인코딩은 UTF-16(BOM)이라 한글이 깨질 수 있다. 파일 저장 시 반드시 `-Encoding utf8`을 지정한다.
- **커밋 메시지에 한글·여러 줄 사용 시**: `-m` 인라인 대신 파일(`git commit -F msg.txt`) 또는 heredoc을 사용해 셸의 따옴표/인코딩 처리로 메시지가 훼손되지 않게 한다.
