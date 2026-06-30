# -*- coding: utf-8 -*-
"""안내서비스 CSV를 카테고리별로 분리하고 집계표를 생성하는 자동화 도구.

표준 라이브러리(csv · pathlib · collections)만 사용한다.

  입력 : 안내서비스.csv
  처리 : 카테고리별로 행을 분리 → 출력_카테고리별/<카테고리명>.csv
  출력 : 카테고리별 건수·대표 기관 집계 → 결과_카테고리집계.csv (+ 콘솔 출력)
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

CATEGORY_COL = "카테고리"
AGENCY_COL = "문의기관"

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "출력_카테고리별"
SUMMARY_CSV = BASE / "결과_카테고리집계.csv"


def find_input() -> Path:
    """안내서비스.csv를 스크립트 위치 또는 첨부 폴더에서 찾는다."""
    for candidate in (BASE / "안내서비스.csv", BASE / "첨부" / "안내서비스.csv"):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("안내서비스.csv를 찾을 수 없습니다.")


def read_rows(path: Path):
    # 정부 제공 CSV는 UTF-8(BOM 포함)이므로 utf-8-sig로 읽는다.
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def split_by_category(fieldnames, rows):
    """카테고리별로 행을 모아 출력_카테고리별/<카테고리명>.csv로 저장."""
    OUT_DIR.mkdir(exist_ok=True)
    groups = defaultdict(list)
    for row in rows:
        groups[row[CATEGORY_COL]].append(row)

    for category, items in groups.items():
        out_path = OUT_DIR / f"{category}.csv"
        with out_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items)
    return groups


def build_summary(groups):
    """카테고리별 건수와 대표(최빈) 문의기관을 집계한다."""
    summary = []
    for category, items in groups.items():
        agencies = Counter(row[AGENCY_COL] for row in items)
        top_agency, _ = agencies.most_common(1)[0]
        summary.append((category, len(items), top_agency))
    # 건수 내림차순, 동률 시 카테고리명 순으로 정렬
    summary.sort(key=lambda x: (-x[1], x[0]))
    return summary


def save_summary(summary):
    with SUMMARY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["카테고리", "건수", "대표기관"])
        writer.writerows(summary)


def main():
    src = find_input()
    fieldnames, rows = read_rows(src)
    groups = split_by_category(fieldnames, rows)

    print(f"[OK] 안내서비스 {len(rows)}건 카테고리별 분리 → 출력_카테고리별/")
    summary = build_summary(groups)
    for category, count, _ in summary:
        print(f" · {category} {count}건")

    save_summary(summary)
    print(f"[OK] 집계표 → {SUMMARY_CSV.name}")


if __name__ == "__main__":
    main()
