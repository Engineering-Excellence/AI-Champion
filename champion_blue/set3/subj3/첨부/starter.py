"""(가상) 행정정보 통합관리 기본법 조항 검색 도구 — 스타터.

사용법:
    python starter.py "기본계획"

→ 같은 폴더에 결과_기본계획.csv 가 생성됩니다.

채워야 할 곳:
1) 조항데이터.json 을 읽어들이세요
2) 명령행 인자로 받은 키워드가 본문에 포함된 조만 골라내세요
3) 결과를 CSV로 저장하세요 (헤더: 조,제목,본문)
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "조항데이터.json"


def main():
    if len(sys.argv) < 2:
        print("사용법: python solution.py <키워드>")
        sys.exit(1)
    keyword = sys.argv[1]

    # TODO: 조항데이터.json 읽어들이기
    articles = json.loads(DATA.read_text(encoding="utf-8"))

    # TODO: 키워드 포함 조만 필터
    filtered = [a for a in articles if keyword in a["본문"]]

    # TODO: 결과 CSV 저장
    out = HERE / f"결과_{keyword}.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["조", "제목", "본문"])
        for a in filtered:
            w.writerow([a["조"], a["제목"], a["본문"]])
    print(f"[OK] {len(filtered)}건 저장 → {out.name}")


if __name__ == "__main__":
    main()
