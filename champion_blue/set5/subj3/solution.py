"""안전점검 보고서 키워드 추출 도구.

사용법: python solution.py "점검"
동작:   장데이터.json 을 읽어 본문에 키워드가 포함된 장만 골라
        결과_<키워드>.csv (헤더 장·제목·본문) 로 저장한다.
표준 라이브러리(csv·json·sys·pathlib)만 사용한다.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "장데이터.json"


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('사용법: python solution.py "<키워드>"')
        sys.exit(1)

    keyword = sys.argv[1].strip()
    articles = json.loads(DATA.read_text(encoding="utf-8"))
    filtered = [a for a in articles if keyword in a["본문"]]

    out = HERE / f"결과_{keyword}.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["장", "제목", "본문"])
        for a in filtered:
            w.writerow([a["장"], a["제목"], a["본문"]])

    print(f"[OK] {len(filtered)}건 저장 → {out.name}")


if __name__ == "__main__":
    main()
