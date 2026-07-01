# -*- coding: utf-8 -*-
"""
과목 3 산출물 ② - Python 자동화 도구
지역균형발전 사업 데이터와 재정자립도 현황을 분석해
콘솔과 결과_요약.csv 로 통계 요약을 출력한다.

실행:
    python solution.py
"""
import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict

# 콘솔 한글 출력 보장
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "3과목_자료묶음"
PROJECT_CSV = DATA_DIR / "지역균형발전_사업.csv"
FINANCE_CSV = DATA_DIR / "재정자립도_현황.csv"
OUT_CSV = BASE / "결과_요약.csv"


def read_csv(path):
    """UTF-8(BOM) CSV 를 dict 리스트로 읽는다."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    projects = read_csv(PROJECT_CSV)
    finance = read_csv(FINANCE_CSV)

    # 1) 총 사업 수
    total = len(projects)

    # 2) 완료된 사업 수 (완료여부 == Y)
    completed = sum(1 for r in projects if r["완료여부"].strip().upper() == "Y")

    # 3) 평균 총사업비 (억 원, 정수)
    costs = [float(r["총사업비_억원"]) for r in projects if r["총사업비_억원"].strip()]
    avg_cost = round(sum(costs) / len(costs)) if costs else 0

    # 4) 사업분야별 사업 수
    field_counts = Counter(r["사업분야"].strip() for r in projects)

    # 5) 지역별 평균 재정자립도 상위 3
    region_rates = defaultdict(list)
    for r in finance:
        try:
            region_rates[r["지역명"].strip()].append(float(r["재정자립도_퍼센트"]))
        except (ValueError, KeyError):
            continue
    region_avg = {k: sum(v) / len(v) for k, v in region_rates.items()}
    top3 = sorted(region_avg.items(), key=lambda x: x[1], reverse=True)[:3]

    # ---- 콘솔 출력 ----
    print(f"[OK] 사업 {total}건 분석 -> {OUT_CSV.name}")
    print(f"총 사업: {total}건 / 완료: {completed}건 / 평균 사업비: {avg_cost}억 원")
    print()
    print("[사업분야별 사업 수]")
    for field, cnt in field_counts.most_common():
        print(f"  - {field}: {cnt}건")
    print()
    print("[지역별 평균 재정자립도 상위 3]")
    for rank, (region, rate) in enumerate(top3, start=1):
        print(f"  {rank}. {region}: {rate:.1f}%")

    # ---- 결과_요약.csv 저장 ----
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["항목", "값"])
        w.writerow(["총 사업 수", total])
        w.writerow(["완료된 사업 수", completed])
        w.writerow(["평균 총사업비(억원)", avg_cost])
        w.writerow([])
        w.writerow(["사업분야별 사업 수", ""])
        w.writerow(["사업분야", "사업 수"])
        for field, cnt in field_counts.most_common():
            w.writerow([field, cnt])
        w.writerow([])
        w.writerow(["지역별 평균 재정자립도 상위 3", ""])
        w.writerow(["순위", "지역명", "재정자립도_퍼센트"])
        for rank, (region, rate) in enumerate(top3, start=1):
            w.writerow([rank, region, round(rate, 1)])


if __name__ == "__main__":
    main()
