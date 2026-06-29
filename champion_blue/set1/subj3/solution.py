# -*- coding: utf-8 -*-
"""산출물 ② - 청렴 신고/교육 CSV 통계 요약 자동화 도구.

첨부 CSV 두 개를 읽어 콘솔과 결과_요약.csv 에 통계를 출력한다.
표준 라이브러리(csv, pathlib)만 사용한다.
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
CASE_CSV = BASE / "첨부" / "청렴신고_사건데이터.csv"
EDU_CSV = BASE / "첨부" / "청렴교육_현황.csv"
OUT_CSV = BASE / "결과_요약.csv"


def read_csv(path):
    """BOM 포함 UTF-8 CSV를 dict 리스트로 읽는다."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    cases = read_csv(CASE_CSV)
    edus = read_csv(EDU_CSV)

    # --- 신고 사건 통계 ---
    total = len(cases)
    done = sum(1 for r in cases if r["처리상태"] == "처리완료")

    durations = [int(r["처리기간_일"]) for r in cases if r["처리기간_일"].strip()]
    avg_duration = round(sum(durations) / len(durations)) if durations else 0

    by_type = Counter(r["신고유형"] for r in cases)

    # --- 교육 통계: 기관유형별 평균 이수율 ---
    rate_sum = defaultdict(float)
    rate_cnt = defaultdict(int)
    for r in edus:
        v = r["교육이수율"].strip()
        if v:
            rate_sum[r["기관유형"]] += float(v)
            rate_cnt[r["기관유형"]] += 1
    avg_rate = {k: round(rate_sum[k] / rate_cnt[k], 1) for k in rate_sum}

    # --- 결과_요약.csv 작성 ---
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["구분", "항목", "값"])
        w.writerow(["요약", "총 신고 사건 수", total])
        w.writerow(["요약", "처리 완료 사건 수", done])
        w.writerow(["요약", "평균 처리기간(일)", avg_duration])
        for name, cnt in by_type.most_common():
            w.writerow(["신고유형별 사건 수", name, cnt])
        for name in sorted(avg_rate):
            w.writerow(["기관유형별 평균 이수율(%)", name, avg_rate[name]])

    # --- 콘솔 출력 ---
    print(f"[OK] 신고 {total}건 분석 → {OUT_CSV.name}")
    print(f"  총 신고: {total}건 / 처리 완료: {done}건 / 평균 처리: {avg_duration}일")
    print("\n[신고유형별 사건 수]")
    for name, cnt in by_type.most_common():
        print(f"  {name:<8} {cnt:>4}건")
    print("\n[기관유형별 평균 이수율]")
    for name in sorted(avg_rate):
        print(f"  {name:<10} {avg_rate[name]:>5}%")


if __name__ == "__main__":
    main()
