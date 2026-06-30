# -*- coding: utf-8 -*-
"""
산출물 ② — 신청서 자동 분류 도구

첨부 신청서/ 폴더의 .md 파일을 메타 헤더(<!-- 지자체: ___ -->)의 지자체 값으로
읽어 출력_지자체별/<지자체명>/ 하위 폴더로 복사하고, 분류 현황을 콘솔과
결과_분류현황.csv 로 출력한다.

    $ python solution.py
"""
import csv
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
# 신청서 폴더 위치: 첨부/신청서 우선, 없으면 신청서/
INPUT_DIR = next(
    (p for p in (BASE / "첨부" / "신청서", BASE / "신청서") if p.is_dir()),
    None,
)
OUTPUT_DIR = BASE / "출력_지자체별"
CSV_PATH = BASE / "결과_분류현황.csv"

HEADER_RE = re.compile(r"<!--\s*지자체:\s*(?P<name>.+?)\s*-->")


def read_region(md_path: Path) -> str | None:
    """마크다운 파일의 메타 헤더에서 지자체명을 추출한다."""
    text = md_path.read_text(encoding="utf-8")
    m = HEADER_RE.search(text)
    return m.group("name").strip() if m else None


def main() -> int:
    if INPUT_DIR is None:
        print("[ERROR] 신청서 폴더를 찾을 수 없습니다 (첨부/신청서 또는 신청서).")
        return 1

    md_files = sorted(INPUT_DIR.glob("*.md"))
    if not md_files:
        print(f"[ERROR] {INPUT_DIR} 에 .md 파일이 없습니다.")
        return 1

    counts: Counter[str] = Counter()
    skipped: list[str] = []

    for md in md_files:
        region = read_region(md)
        if not region:
            skipped.append(md.name)
            continue
        dest_dir = OUTPUT_DIR / region
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(md, dest_dir / md.name)
        counts[region] += 1

    total = sum(counts.values())
    print(f"[OK] 신청서 {total}건 지자체별 분류 → {OUTPUT_DIR.name}/")
    for region in sorted(counts):
        print(f" · {region} {counts[region]}건")
    if skipped:
        print(f"[WARN] 지자체 헤더 누락으로 건너뜀 {len(skipped)}건: {', '.join(skipped)}")

    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["지자체명", "파일수"])
        for region in sorted(counts):
            writer.writerow([region, counts[region]])
        writer.writerow(["합계", total])
    print(f"[OK] 분류 현황 저장 → {CSV_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
