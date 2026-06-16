# CLAUDE.md

전체 코드베이스 가이드는 **AGENTS.md**를 참조하라.

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

### 환경

- **런타임:** conda base (Python 3.13)
- **활성화:** `conda activate base`
- **환경 생성:** `conda env create -f environment.yml`
- **패키지 설치:** `conda install --file requirements.txt` (pip은 conda에 없는 패키지에만 사용)

### 실행 명령

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

### 핵심 규칙

- 모든 데이터는 한국어; CSV 인코딩은 EUC-KR 또는 CP949
- matplotlib 한글 레이블: `plt.rcParams["font.family"] = "Malgun Gothic"` 필수
- PyInstaller 빌드 산출물(`build/`, `dist/`, `*.pyc`)은 `.gitignore`로 제외됨
- 노트북(`.ipynb`)은 셀이 상태를 공유하므로 항상 처음부터 재실행
