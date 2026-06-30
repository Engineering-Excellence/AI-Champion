"""(가상) 행정정보 통합관리 기본법 조항 검색 도구.

사용법:
    python solution.py "기본계획"

→ 같은 폴더에 결과_기본계획.csv 가 생성됩니다.
  본문(또는 제목)에 키워드가 포함된 조항만 골라 UTF-8 CSV로 저장하고,
  화면에 결과 건수를 출력합니다.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "첨부" / "조항데이터.json"


def main():
    if len(sys.argv) < 2:
        print("사용법: python solution.py <키워드>")
        sys.exit(1)
    keyword = sys.argv[1]

    # 1) 조항데이터.json 읽기
    articles = json.loads(DATA.read_text(encoding="utf-8"))

    # 2) 본문 또는 제목에 키워드가 포함된 조항만 필터
    filtered = [a for a in articles if keyword in a["본문"] or keyword in a["제목"]]

    # 3) 결과를 CSV로 저장 (UTF-8, 헤더: 조,제목,본문)
    out = HERE / f"결과_{keyword}.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["조", "제목", "본문"])
        for a in filtered:
            w.writerow([a["조"], a["제목"], a["본문"]])

    print(f"[OK] {len(filtered)}건 저장 → {out.name}")


if __name__ == "__main__":
    main()
