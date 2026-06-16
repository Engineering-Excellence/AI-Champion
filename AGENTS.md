# AGENTS.md — AI-Champion Codebase Guide

## Project Overview

**AI-Champion** is a hands-on workshop project for the AI Champion program, covering two themes across two days:

- **Day 1** (`champion_blue/day1/`) — 생성형AI를 활용한 콘텐츠 및 문서자동화
- **Day 2** (`champion_blue/day2/`, `day2_analysis/`, `day2_agent/`) — 생성형AI를 활용한 데이터분석

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
│   ├── day2/                         # Day 2-A: 기초 데이터분석
│   │   ├── input/
│   │   │   ├── 국토교통부_전국 버스정류장 위치정보_20251031.csv
│   │   │   └── excel_100_files/        # 가상 월별 보고서 100개
│   │   ├── output/
│   │   │   ├── merged_all.xlsx         # 100개 파일 병합 결과
│   │   │   ├── bus_stop_heatmap.html   # 전국 버스정류장 히트맵
│   │   │   └── 전국_버스정류장_분석_보고서.pdf  # 8페이지 A4 보고서
│   │   ├── blue_exercise.ipynb         # 엑셀 생성·병합 실습
│   │   ├── dataAnalysis_exercise.ipynb # CSV 분석·히트맵·보고서 실습
│   │   └── generate_report.py          # PDF 보고서 생성 스크립트
│   │
│   ├── day2_analysis/                # Day 2-B: 머신러닝 예측 모델
│   │   ├── input/
│   │   │   ├── 2025 지방세통계연감.pdf
│   │   │   └── public_sector_analysis_dataset_3000x20.xlsx
│   │   ├── output/
│   │   │   ├── images/                 # 그래프01~06 (지방세 분석)
│   │   │   ├── tables/                 # 표01~10 (지방세 집계)
│   │   │   └── urgency_model_report.png  # 4알고리즘 비교 분석 보고서
│   │   ├── supervisedLearning.ipynb        # 지도학습: 분류+회귀 2종
│   │   ├── urgency_classification_model.ipynb  # 4알고리즘 F1 비교
│   │   └── 지방세통계연감_analysis.ipynb   # PDF 통계연감 분석
│   │
│   └── day2_agent/                   # Day 2-C: 에이전트·GUI 앱
│       ├── dashboard/
│       │   ├── generate_dashboard.py   # 민원 데이터 HTML 대시보드 생성
│       │   └── dashboard.html          # 출력 HTML (폐쇄망 완전 자체 포함)
│       ├── file_manager/
│       │   ├── file_manager.py         # Tkinter 파일 관리자 (탐색기 스타일)
│       │   └── build_exe.bat           # PyInstaller 빌드 스크립트 (build/·dist/ 는 gitignore)
│       └── news_reader/
│           ├── news_gui.py             # Tkinter RSS 뉴스 리더
│           ├── news_web.html           # 동일 기능 웹 버전
│           └── build_exe.bat           # PyInstaller 빌드 스크립트 (build/·dist/ 는 gitignore)
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

## Day 2-A — 기초 데이터분석 (`champion_blue/day2/`)

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

## Day 2-B — 머신러닝 예측 모델 (`champion_blue/day2_analysis/`)

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

## Day 2-C — 에이전트·GUI 앱 (`champion_blue/day2_agent/`)

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
