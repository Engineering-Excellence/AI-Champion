# -*- coding: utf-8 -*-
"""[연습세트01·블루] 1과목 보도자료 분석 스크립트"""
import re
import csv
from pathlib import Path

BASE = Path(__file__).parent / "첨부" / "자료묶음" / "보도자료"
files = sorted(BASE.rglob("*.md"))

records = []
for f in files:
    raw = f.read_text(encoding="utf-8")
    # 메타 헤더 파싱
    m = re.search(r"<!--(.*?)-->", raw, re.S)
    header = m.group(1)
    dept = re.search(r"부서:\s*([^\|]+?)\s*\|", header).group(1).strip()
    date = re.search(r"발표일:\s*([\d-]+)", header).group(1).strip()
    # 본문 = 헤더 주석 제거 후 나머지 (선행 공백 제거; 예시 평균본문길이 767과 일치)
    body = raw[m.end():].lstrip()
    records.append({"file": f.name, "dept": dept, "date": date, "body": body})

# 문항 1: 부서 종류 수
depts = {r["dept"] for r in records}
q1 = len(depts)

# 문항 2: 본문 글자 수 최대 파일의 부서
for r in records:
    r["len"] = len(r["body"])
q2_rec = max(records, key=lambda r: r["len"])
q2 = q2_rec["dept"]

# 문항 3: (숫자)억\s*원 합계
all_body = "".join(r["body"] for r in records)
eok = [int(x) for x in re.findall(r"(\d+)\s*억\s*원", all_body)]
q3 = sum(eok)

# 문항 4: 발표일 가장 빠른 파일의 부서
q4_rec = min(records, key=lambda r: r["date"])
q4 = q4_rec["dept"]

# 문항 5: (숫자)개 패턴 최댓값
gae = [int(x) for x in re.findall(r"(\d+)\s*개", all_body)]
q5 = max(gae)

print("=== 단답 ===")
print(f"문항1 (부서 종류 수): {q1}")
print(f"문항2 (본문 최다 파일 부서): {q2}  [{q2_rec['file']} / {q2_rec['len']}자]")
print(f"문항3 (억원 합계): {q3}  ({eok})")
print(f"문항4 (발표일 최조 부서): {q4}  [{q4_rec['file']} / {q4_rec['date']}]")
print(f"문항5 ((숫자)개 최댓값): {q5}  ({sorted(gae)})")

print("\n파일별 본문 길이:")
for r in records:
    print(f"  {r['file']}: {r['dept']} / {r['date']} / {r['len']}자")

# 제출파일: 부서별_자료수.csv
# 청렴횟수합 = 본문 내 '청렴' 등장 횟수 합
dept_stats = {}
for r in records:
    d = r["dept"]
    s = dept_stats.setdefault(d, {"count": 0, "cheong": 0, "lens": []})
    s["count"] += 1
    # '청렴' 출현 횟수 (직책명 '청렴담당관'은 제외 → 예시값 일치)
    s["cheong"] += len(re.findall(r"청렴(?!담당관)", r["body"]))
    s["lens"].append(r["len"])

rows = []
for d, s in dept_stats.items():
    avg = round(sum(s["lens"]) / len(s["lens"]))
    rows.append((d, s["count"], s["cheong"], avg))
rows.sort(key=lambda x: -x[1])  # 자료수 내림차순

print("\n=== 부서별 통계 ===")
for row in rows:
    print(" ", row)

out = Path(__file__).parent / "부서별_자료수.csv"
with out.open("w", encoding="utf-8-sig", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(["담당부서", "자료수", "청렴횟수합", "평균본문길이"])
    w.writerows(rows)
print(f"\n저장: {out}")
