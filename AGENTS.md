# AGENTS.md — AI-Champion Codebase Guide

## Project Overview

**AI-Champion** is a Python study project with two tracks:

1. **`python_exercise/`** — Jupyter notebook exercises covering PDF extraction, Excel processing, and CSV analysis with Korean government data.
2. **`champion_blue/`** — Side-by-side comparison of Claude vs ChatGPT approaches to the same automated data analysis task (Excel → charts + Word report).

Primary environment: Jupyter notebooks on Windows with a `.venv` virtualenv. Korean language data is pervasive.

---

## Directory Layout

```
AI-Champion/
├── champion_blue/
│   ├── analysis_claude.py          # Streamlit interactive dashboard (Claude's approach)
│   ├── analysis_chatgpt.py         # Batch script approach (ChatGPT's approach)
│   ├── input.xlsx                  # Shared input for both scripts
│   └── public_sector_analysis_dataset_3000x20 - 복사본.xlsx
├── python_exercise/
│   ├── python_exercise.ipynb       # Main notebook (7 exercises)
│   ├── snake_game.py               # Standalone Tkinter demo, unrelated to exercises
│   ├── 2026년 예산 사업설명자료.pdf  # Korean budget PDF used in exercises
│   ├── 행정안전부_...csv            # Korean population CSV used in exercises
│   ├── extracted_tables_page100_150.xlsx  # Output of PDF→Excel exercise
│   └── fake_excels/
│       └── merged_data.xlsx        # Output of Excel-merge exercise
└── requirements.txt
```

---

## champion_blue — Claude vs ChatGPT Analysis

Both scripts consume `input.xlsx` and produce statistical tables and charts, but differ in style:

| | `analysis_claude.py` | `analysis_chatgpt.py` |
|---|---|---|
| **UI** | Streamlit web app (interactive) | CLI batch script |
| **Output** | In-browser dashboard + downloadable `.docx` | `output/statistics.xlsx` + `output/chart_NN.png` + `output/analysis.docx` |
| **Chart selection** | User picks via sidebar checkboxes | Fixed set of 10 chart types |
| **Run command** | `streamlit run champion_blue/analysis_claude.py` | `python champion_blue/analysis_chatgpt.py` |

### Shared chart types (both scripts)
Histogram, boxplot, correlation heatmap, category bar/pie, scatter, timeseries, group-by bar, pairplot, violin, missing-value bar.

### `analysis_claude.py` architecture
- `load_data(file)` — `@st.cache_data`; auto-detects numeric/categorical/datetime columns, tries `pd.to_datetime` on object columns (>80% parse rate threshold).
- `STAT_TABLE_REGISTRY` — dict of `name → lambda(df, num, cat, dt, target_cat)` for the 5 stat tables.
- `CHART_REGISTRY` — dict of `name → fn(df, numeric_cols, **kwargs)` for the 11 chart functions; each returns a `matplotlib.figure.Figure` or `None`.
- `build_report(...)` — assembles a `python-docx` `Document` with stat tables and embedded PNG charts; returns an `io.BytesIO` buffer for Streamlit download.
- Font: `Malgun Gothic` (Windows Korean font) set globally in `plt.rcParams`.

### `analysis_chatgpt.py` architecture
- Flat script; reads `input.xlsx`, classifies columns, writes all stat tables to `output/statistics.xlsx` via `pd.ExcelWriter`.
- Saves charts as numbered PNGs (`chart_01.png` … `chart_10.png`) in `output/`.
- Builds a `.docx` report by inserting stat table strings and chart images.
- Uses IQR method for outlier detection (stored in `tables["이상치"]`).

---

## python_exercise — Notebook Exercises

`python_exercise.ipynb` uses `#%%` cell markers. Cells are stateful; variables persist across cells. **Always re-run from the top** if upstream variables are needed.

### Exercise sequence
1. **PDF baseline** — raw regex parsing of PDF bytes; no external library.
2. **PyMuPDF extraction** — `fitz.open()`, `page.get_text()`, `page.find_tables()`. Tables marked with "□" (U+25A1) are targeted for extraction.
3. **Batch PDF→Excel** — pages 100–150 extracted; output: `extracted_tables_page100_150.xlsx`.
4. **Excel merge** — 100 generated files in `fake_excels/` merged via `pd.concat()`; output: `fake_excels/merged_data.xlsx`. Uses `PERFORM_DELETE` flag to guard against accidental deletion.
5. **CSV inspection** — multi-encoding fallback loop (UTF-8 → CP949 → EUC-KR → Latin1), chunked reading, `summarize_df()` preview.
6. **Snake game** — `snake_game.py` launched via `subprocess`; Arrow keys to move, R to restart.
7. *(Additional exercises may follow.)*

### Key helper patterns

```python
# Auto-install missing packages inside the notebook
def ensure_package(pkg, import_name=None):
    try:
        __import__(import_name or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Summarize any DataFrame
def summarize_df(df):
    # prints dtype, null count/%, numeric describe, categorical value_counts
```

---

## Korean Language Handling

This project's data is predominantly Korean.

- **CSV encoding**: explicitly pass `encoding="cp949"` or `encoding="euc-kr"`; never assume UTF-8.
- **File paths**: use `pathlib.Path` or raw strings — Korean characters in paths are common.
- **PDF symbol**: "□" (U+25A1) marks sections to extract.
- **Fonts**: `Malgun Gothic` (Windows) must be set for matplotlib to render Korean labels correctly.

---

## Dependencies

```
PyMuPDF      # fitz — PDF parsing and table detection
pandas       # DataFrames, Excel I/O
numpy        # Numerical operations, random data generation
streamlit    # Web UI (champion_blue/analysis_claude.py)
seaborn      # Statistical plots
matplotlib   # Base plotting
python-docx  # Word report generation
openpyxl     # xlsx read/write (implicit pandas dependency)
tkinter      # Snake game GUI (stdlib, no install needed)
```

Install:
```powershell
pip install -r requirements.txt
```

Python 3.7+ required. The notebook installs missing packages inline via `ensure_package()`.

---

## Common Pitfalls

| Issue | Fix |
|---|---|
| PDF text extraction returns empty string | PDF may be image-based or encrypted; check with `page.get_text()` length before processing |
| Excel merge column mismatch | Capture `first_cols` from the first file; `df.reindex(columns=first_cols)` on all subsequent frames |
| CSV `UnicodeDecodeError` | Wrap `pd.read_csv()` in a loop trying CP949, then EUC-KR, then Latin1 |
| Memory error on large CSV | Pass `chunksize=` to `pd.read_csv()` and iterate |
| Accidental file deletion | Default `PERFORM_DELETE = False`; only flip to `True` after dry-run confirms correct targets |
| Korean labels garbled in charts | Set `plt.rcParams["font.family"] = "Malgun Gothic"` before any plot call |
| Streamlit app hangs | Run from repo root: `streamlit run champion_blue/analysis_claude.py` |
