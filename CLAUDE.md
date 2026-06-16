# CLAUDE.md

전체 코드베이스 가이드는 **AGENTS.md**를 참조하라.

## 환경

- **런타임:** conda base (Python 3.13)
- **활성화:** `conda activate base`
- **환경 생성:** `conda env create -f environment.yml`
- **패키지 설치:** `conda install --file requirements.txt` (pip은 conda에 없는 패키지에만 사용)

## 실행 명령

```powershell
# Streamlit 대화형 대시보드 (Day 1)
streamlit run champion_blue/day1/analysis_claude.py

# 배치 분석 스크립트 (Day 1)
python champion_blue/day1/analysis_chatgpt.py

# 버스정류장 PDF 보고서 생성 (Day 2-A)
python champion_blue/day2/generate_report.py

# 민원 데이터 HTML 대시보드 생성 (Day 2-C)
python champion_blue/day2_agent/dashboard/generate_dashboard.py
```

## 핵심 규칙

- 모든 데이터는 한국어; CSV 인코딩은 EUC-KR 또는 CP949
- matplotlib 한글 레이블: `plt.rcParams["font.family"] = "Malgun Gothic"` 필수
- PyInstaller 빌드 산출물(`build/`, `dist/`, `*.pyc`)은 `.gitignore`로 제외됨
- 노트북(`.ipynb`)은 셀이 상태를 공유하므로 항상 처음부터 재실행
