# -*- coding: utf-8 -*-
"""
공공부문 민원 데이터 대시보드 생성기
15개 통계표 + 10개 그래프 | 폐쇄망 완전 자체 포함 HTML
"""
import pandas as pd
import numpy as np
import json
import os

INPUT  = r'C:\Users\user\Documents\Study\AI-Champion\champion_blue\day2_analysis\input\public_sector_analysis_dataset_3000x20.xlsx'
OUTPUT = r'C:\Users\user\Documents\Study\AI-Champion\champion_blue\day2_analysis\output\dashboard.html'

# ── 데이터 로드 ───────────────────────────────────────────
df = pd.read_excel(INPUT)
df['접수일자'] = pd.to_datetime(df['접수일자'])
df['월'] = df['접수일자'].dt.month
N = len(df)

def pct(v, t): return round(float(v)/t*100, 1)
def r2(v):     return round(float(v), 2)
def r1(v):     return round(float(v), 1)

# ══════════════════════════════════════════════════════════
# 15개 통계표 계산
# ══════════════════════════════════════════════════════════

# 표01 기술통계 요약
num_map = {
    '민원복잡도':'민원복잡도', '담당인력수':'담당인력수', '첨부서류수':'첨부서류수',
    '예산관련금액_만원':'예산관련금액(만원)', '처리기준일수':'처리기준일수',
    '실제처리일수':'실제처리일수', '재문의횟수':'재문의횟수',
    '만족도점수':'만족도점수', '행정비용추정_만원':'행정비용추정(만원)'
}
t01 = []
for col, lbl in num_map.items():
    s = df[col]
    t01.append({'항목':lbl,'건수':int(s.count()),'평균':r2(s.mean()),
                '표준편차':r2(s.std()),'최솟값':r2(s.min()),
                'Q1':r2(s.quantile(.25)),'중앙값':r2(s.median()),
                'Q3':r2(s.quantile(.75)),'최댓값':r2(s.max())})

# 표02 기관유형별
t02 = []
for k, v in df.groupby('기관유형'):
    t02.append({'기관유형':k,'건수':len(v),'비율(%)':pct(len(v),N),
                '평균만족도':r2(v['만족도점수'].mean()),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                '평균처리일수':r1(v['실제처리일수'].mean()),
                '평균행정비용(만원)':r1(v['행정비용추정_만원'].mean())})
t02.sort(key=lambda x:-x['건수'])

# 표03 지역별
t03 = []
for k, v in df.groupby('지역'):
    t03.append({'지역':k,'건수':len(v),'비율(%)':pct(len(v),N),
                '평균만족도':r2(v['만족도점수'].mean()),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                '평균처리일수':r1(v['실제처리일수'].mean()),
                '평균복잡도':r2(v['민원복잡도'].mean())})
t03.sort(key=lambda x:-x['건수'])

# 표04 서비스분야별
t04 = []
for k, v in df.groupby('서비스분야'):
    t04.append({'서비스분야':k,'건수':len(v),'비율(%)':pct(len(v),N),
                '평균만족도':r2(v['만족도점수'].mean()),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                '평균복잡도':r2(v['민원복잡도'].mean()),
                '평균행정비용(만원)':r1(v['행정비용추정_만원'].mean())})
t04.sort(key=lambda x:-x['건수'])

# 표05 민원채널별
t05 = []
for k, v in df.groupby('민원채널'):
    t05.append({'민원채널':k,'건수':len(v),'비율(%)':pct(len(v),N),
                '평균만족도':r2(v['만족도점수'].mean()),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                '평균재문의횟수':r2(v['재문의횟수'].mean()),
                '평균처리일수':r1(v['실제처리일수'].mean())})
t05.sort(key=lambda x:-x['건수'])

# 표06 신청자연령대별
age_order = ['20대 이하','30대','40대','50대','60대 이상']
t06 = []
grp6 = df.groupby('신청자연령대')
for k in age_order:
    if k in grp6.groups:
        v = grp6.get_group(k)
        t06.append({'신청자연령대':k,'건수':len(v),'비율(%)':pct(len(v),N),
                    '취약계층비율(%)':pct(v['취약계층여부'].sum(),len(v)),
                    '평균만족도':r2(v['만족도점수'].mean()),
                    '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                    '평균재문의횟수':r2(v['재문의횟수'].mean())})

# 표07 긴급도별
urg_order = ['낮음','보통','높음','긴급']
t07 = []
grp7 = df.groupby('긴급도')
for k in urg_order:
    if k in grp7.groups:
        v = grp7.get_group(k)
        t07.append({'긴급도':k,'건수':len(v),'비율(%)':pct(len(v),N),
                    '평균기준일수':r1(v['처리기준일수'].mean()),
                    '평균실제일수':r1(v['실제처리일수'].mean()),
                    '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                    '평균복잡도':r2(v['민원복잡도'].mean())})

# 표08 취약계층 비교
t08 = []
for k, lbl in [(0,'일반'),(1,'취약계층')]:
    v = df[df['취약계층여부']==k]
    t08.append({'구분':lbl,'건수':len(v),'비율(%)':pct(len(v),N),
                '평균만족도':r2(v['만족도점수'].mean()),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                '평균재문의횟수':r2(v['재문의횟수'].mean()),
                '평균처리일수':r1(v['실제처리일수'].mean()),
                '평균행정비용(만원)':r1(v['행정비용추정_만원'].mean())})

# 표09 월별
mlbl = {i:f'{i}월' for i in range(1,13)}
cum, prev = 0, None
t09 = []
grp9 = df.groupby('월')
for m in range(1,13):
    if m in grp9.groups:
        v = grp9.get_group(m)
        cnt = len(v)
        cum += cnt
        chg = cnt - prev if prev is not None else 0
        t09.append({'월':mlbl[m],'건수':cnt,'누적건수':cum,
                    '전월대비':f'+{chg}' if chg>=0 else str(chg),
                    '지연율(%)':pct(v['지연여부'].sum(),cnt),
                    '평균만족도':r2(v['만족도점수'].mean())})
        prev = cnt

# 표10 처리기간 분석
t10 = []
for k, v in df.groupby('기관유형'):
    a = r1(v['처리기준일수'].mean())
    b = r1(v['실제처리일수'].mean())
    t10.append({'기관유형':k,'건수':len(v),
                '평균기준일수':a,'평균실제일수':b,
                '평균초과일수':r1(b-a),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                '최대실제일수':int(v['실제처리일수'].max())})
t10.sort(key=lambda x:-x['지연율(%)'])

# 표11 만족도 구간별
t11 = []
for lo,hi,lbl in [(1,2,'1.0~2.0'),(2,3,'2.0~3.0'),(3,4,'3.0~4.0'),(4,5.01,'4.0~5.0')]:
    v = df[(df['만족도점수']>=lo)&(df['만족도점수']<hi)]
    t11.append({'만족도구간':lbl,'건수':len(v),'비율(%)':pct(len(v),N),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)) if len(v) else 0,
                '평균재문의횟수':r2(v['재문의횟수'].mean()) if len(v) else 0,
                '평균행정비용(만원)':r1(v['행정비용추정_만원'].mean()) if len(v) else 0})

# 표12 재문의 횟수별
t12 = []
for k, v in df.groupby('재문의횟수'):
    t12.append({'재문의횟수':int(k),'건수':len(v),'비율(%)':pct(len(v),N),
                '평균만족도':r2(v['만족도점수'].mean()),
                '지연율(%)':pct(v['지연여부'].sum(),len(v)),
                '평균처리일수':r1(v['실제처리일수'].mean())})

# 표13 기관유형×서비스분야 교차표
cross = pd.crosstab(df['기관유형'], df['서비스분야'])
svc_cols = sorted(df['서비스분야'].unique().tolist())
t13_hdr = ['기관유형'] + svc_cols + ['합계']
t13 = []
for idx, row in cross.iterrows():
    r = {'기관유형':idx}
    for c in svc_cols: r[c] = int(row.get(c,0))
    r['합계'] = int(row.sum())
    t13.append(r)
t13.sort(key=lambda x:-x['합계'])

# 표14 지연/비지연 집단 요인 분석
t14 = []
for k, lbl in [(0,'비지연'),(1,'지연')]:
    v = df[df['지연여부']==k]
    t14.append({'구분':lbl,'건수':len(v),'비율(%)':pct(len(v),N),
                '평균복잡도':r2(v['민원복잡도'].mean()),
                '평균인력수':r2(v['담당인력수'].mean()),
                '평균서류수':r2(v['첨부서류수'].mean()),
                '평균재문의횟수':r2(v['재문의횟수'].mean()),
                '평균만족도':r2(v['만족도점수'].mean()),
                '평균행정비용(만원)':r1(v['행정비용추정_만원'].mean()),
                '평균처리일수':r1(v['실제처리일수'].mean())})

# 표15 행정비용 분석
tot_cost = df['행정비용추정_만원'].sum()
t15 = []
for k, v in df.groupby('서비스분야'):
    t15.append({'서비스분야':k,'건수':len(v),
                '평균비용(만원)':r1(v['행정비용추정_만원'].mean()),
                '최솟값(만원)':r1(v['행정비용추정_만원'].min()),
                '최댓값(만원)':r1(v['행정비용추정_만원'].max()),
                '합계비용(만원)':r1(v['행정비용추정_만원'].sum()),
                '비율(%)':pct(v['행정비용추정_만원'].sum(),tot_cost)})
t15.sort(key=lambda x:-x['합계비용(만원)'])

# ══════════════════════════════════════════════════════════
# 10개 차트 데이터
# ══════════════════════════════════════════════════════════
vc2 = df.groupby('기관유형').size().sort_values(ascending=False)
chart1 = {'labels':vc2.index.tolist(), 'values':vc2.values.tolist()}

vc3 = df.groupby('지역').size().sort_values()
chart2 = {'labels':vc3.index.tolist(), 'values':vc3.values.tolist()}

vc4 = df.groupby('서비스분야').size().sort_values(ascending=False)
chart3 = {'labels':vc4.index.tolist(), 'values':vc4.values.tolist()}

vc5 = df.groupby('민원채널').size().sort_values(ascending=False)
chart4 = {'labels':vc5.index.tolist(), 'values':vc5.values.tolist()}

vc6 = df.groupby('신청자연령대').size().reindex(age_order)
chart5 = {'labels':vc6.index.tolist(), 'values':[int(x) for x in vc6.values]}

mnth_cnt = [int(df[df['월']==m].shape[0]) for m in range(1,13)]
chart6 = {'labels':[f'{i}월' for i in range(1,13)], 'values':mnth_cnt}

sat_vals = [len(df[(df['만족도점수']>=lo)&(df['만족도점수']<hi)])
            for lo,hi in [(1,2),(2,3),(3,4),(4,5.01)]]
chart7 = {'labels':['1.0~2.0','2.0~3.0','3.0~4.0','4.0~5.0'],
          'values':sat_vals}

std_v = [r1(df[df['기관유형']==k]['처리기준일수'].mean()) for k in vc2.index]
act_v = [r1(df[df['기관유형']==k]['실제처리일수'].mean()) for k in vc2.index]
chart8 = {'labels':vc2.index.tolist(),
          'datasets':[{'label':'기준일수','values':std_v},
                      {'label':'실제일수','values':act_v}]}

dc = df['지연여부'].value_counts().sort_index()
chart9 = {'labels':['비지연','지연'],
          'values':[int(dc.get(0,0)), int(dc.get(1,0))]}

chart10 = {'labels':urg_order,
           'datasets':[
               {'label':'비지연','values':[int(df[(df['긴급도']==k)&(df['지연여부']==0)].shape[0]) for k in urg_order]},
               {'label':'지연',  'values':[int(df[(df['긴급도']==k)&(df['지연여부']==1)].shape[0]) for k in urg_order]}
           ]}

kpi = {
    'total': N,
    'delay_rate': pct(df['지연여부'].sum(), N),
    'avg_sat': r2(df['만족도점수'].mean()),
    'avg_cost': r1(df['행정비용추정_만원'].mean()),
    'avg_proc': r1(df['실제처리일수'].mean()),
    'vuln_rate': pct(df['취약계층여부'].sum(), N),
}
CHARTS_JSON = json.dumps({
    'c1':chart1,'c2':chart2,'c3':chart3,'c4':chart4,'c5':chart5,
    'c6':chart6,'c7':chart7,'c8':chart8,'c9':chart9,'c10':chart10
}, ensure_ascii=False)
KPI_JSON = json.dumps(kpi, ensure_ascii=False)

# ══════════════════════════════════════════════════════════
# HTML 테이블 빌더
# ══════════════════════════════════════════════════════════
def tbl(rows, title, note=''):
    keys = list(rows[0].keys())
    hdr = ''.join(f'<th>{k}</th>' for k in keys)
    bdy = ''.join('<tr>'+''.join(f'<td>{r[k]}</td>' for k in keys)+'</tr>' for r in rows)
    nt = f'<p class="tnote">{note}</p>' if note else ''
    return (f'<div class="tw"><div class="tt">{title}</div>{nt}'
            f'<div class="ts"><table><thead><tr>{hdr}</tr></thead>'
            f'<tbody>{bdy}</tbody></table></div></div>')

def cross_tbl(rows, headers, title):
    hdr = ''.join(f'<th>{h}</th>' for h in headers)
    bdy = ''.join('<tr>'+''.join(f'<td>{r.get(h,"")}</td>' for h in headers)+'</tr>' for r in rows)
    return (f'<div class="tw"><div class="tt">{title}</div>'
            f'<div class="ts"><table><thead><tr>{hdr}</tr></thead>'
            f'<tbody>{bdy}</tbody></table></div></div>')

# 표01~08 (1섹션)
S1 = (tbl(t01,'표01. 주요 수치형 변수 기술통계 요약','총 3,000건 기준')
    + tbl(t02,'표02. 기관유형별 민원 처리 현황')
    + tbl(t03,'표03. 지역별 민원 현황')
    + tbl(t04,'표04. 서비스분야별 민원 현황')
    + tbl(t05,'표05. 민원채널별 현황')
    + tbl(t06,'표06. 신청자연령대별 현황')
    + tbl(t07,'표07. 긴급도별 민원 현황')
    + tbl(t08,'표08. 취약계층 여부별 비교 분석'))

# 표09~15 (2섹션)
S2 = (tbl(t09,'표09. 월별 민원 접수 현황 (2025년)')
    + tbl(t10,'표10. 기관유형별 처리기간 분석')
    + tbl(t11,'표11. 만족도 구간별 분포')
    + tbl(t12,'표12. 재문의 횟수별 현황 분석')
    + cross_tbl(t13, t13_hdr,'표13. 기관유형 × 서비스분야 교차표')
    + tbl(t14,'표14. 지연/비지연 집단 요인 비교 분석')
    + tbl(t15,'표15. 서비스분야별 행정비용 분석'))

# ══════════════════════════════════════════════════════════
# HTML 조립
# ══════════════════════════════════════════════════════════
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:'Malgun Gothic','맑은 고딕','나눔고딕',NanumGothic,
    AppleGothic,'Apple SD Gothic Neo',sans-serif;
  background:#f0f2f5;color:#1a1a2e;font-size:14px;line-height:1.6;
}
.hdr{
  background:linear-gradient(135deg,#1a1a2e 0%,#16213e 55%,#0f3460 100%);
  color:#fff;padding:22px 32px;position:sticky;top:0;z-index:100;
  box-shadow:0 2px 12px rgba(0,0,0,.4);
}
.hdr h1{font-size:20px;font-weight:700;letter-spacing:-.3px}
.hdr p{font-size:12px;opacity:.7;margin-top:3px}
.tab-nav{
  background:#fff;border-bottom:2px solid #e2e8f0;
  display:flex;gap:0;padding:0 20px;position:sticky;top:68px;z-index:99;
  box-shadow:0 1px 4px rgba(0,0,0,.06);overflow-x:auto;
}
.tab-btn{
  padding:13px 18px;border:none;background:none;cursor:pointer;
  font-family:inherit;font-size:13px;font-weight:600;color:#64748b;
  border-bottom:3px solid transparent;margin-bottom:-2px;
  transition:all .2s;white-space:nowrap;
}
.tab-btn:hover{color:#1a1a2e}
.tab-btn.active{color:#0f3460;border-bottom-color:#0f3460}
.page{display:none;padding:22px 22px 48px}
.page.active{display:block}
/* KPI */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:14px;margin-bottom:24px}
.kc{background:#fff;border-radius:12px;padding:18px 14px;
  box-shadow:0 1px 6px rgba(0,0,0,.08);text-align:center;
  border-top:4px solid var(--c);transition:transform .15s}
.kc:hover{transform:translateY(-2px)}
.kc .val{font-size:26px;font-weight:800;color:var(--c);line-height:1.1}
.kc .lbl{font-size:11px;color:#64748b;margin-top:5px}
/* Summary */
.sg{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-bottom:20px}
.sc{background:#fff;border-radius:10px;padding:14px 18px;
  box-shadow:0 1px 6px rgba(0,0,0,.08);border-left:4px solid var(--c)}
.sc h3{font-size:11px;color:#64748b;font-weight:600;margin-bottom:6px}
.sc p{font-size:13px;color:#1a1a2e;line-height:1.7}
/* Charts */
.cg{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
@media(max-width:860px){.cg{grid-template-columns:1fr}}
.cc{background:#fff;border-radius:12px;box-shadow:0 1px 6px rgba(0,0,0,.08);padding:18px}
.cc.wide{grid-column:1/-1}
.cc canvas{width:100%!important;display:block}
.ct{font-size:13px;font-weight:700;color:#1a1a2e;margin-bottom:10px;
  padding-bottom:8px;border-bottom:1px solid #f1f5f9}
.leg{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;justify-content:center}
.li{display:flex;align-items:center;gap:5px;font-size:11px;color:#555}
.lb{width:13px;height:13px;border-radius:3px;flex-shrink:0}
/* Tables */
.tw{background:#fff;border-radius:12px;box-shadow:0 1px 6px rgba(0,0,0,.08);
  margin-bottom:18px;overflow:hidden}
.tt{font-size:13px;font-weight:700;color:#1a1a2e;padding:14px 18px 0}
.tnote{font-size:11px;color:#94a3b8;padding:3px 18px 0}
.ts{overflow-x:auto;padding:10px 0 4px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
thead tr{background:#0f3460;color:#fff}
thead th{padding:9px 11px;text-align:center;font-weight:600;white-space:nowrap}
tbody tr{border-bottom:1px solid #f1f5f9;transition:background .1s}
tbody tr:hover{background:#f8fafc}
tbody td{padding:8px 11px;text-align:center;color:#374151}
tbody tr:first-child td{font-weight:600}
"""

JS = r"""
const KPI    = """ + KPI_JSON + r""";
const CHARTS = """ + CHARTS_JSON + r""";

// ── 탭 전환 ─────────────────────────────────────────────
function showTab(id,btn){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
  if(id==='ch1')drawCharts1();
  if(id==='ch2')drawCharts2();
}

// ── KPI 초기화 ──────────────────────────────────────────
(function(){
  const items=[
    {l:'총 민원 건수',    v:KPI.total.toLocaleString()+'건', c:'#0f3460'},
    {l:'평균 만족도',     v:KPI.avg_sat.toFixed(2)+'점',    c:'#e94560'},
    {l:'지연율',         v:KPI.delay_rate+'%',              c:'#f5a623'},
    {l:'평균 처리일수',   v:KPI.avg_proc+'일',               c:'#28a745'},
    {l:'평균 행정비용',   v:KPI.avg_cost.toLocaleString()+'만원',c:'#6f42c1'},
    {l:'취약계층 비율',   v:KPI.vuln_rate+'%',              c:'#17a2b8'},
  ];
  document.getElementById('kpi').innerHTML=items.map(i=>
    `<div class="kc" style="--c:${i.c}"><div class="val">${i.v}</div><div class="lbl">${i.l}</div></div>`
  ).join('');
  document.getElementById('sg').innerHTML=`
    <div class="sc" style="--c:#0f3460"><h3>데이터 개요</h3>
      <p>총 3,000건 공공기관 민원 데이터(20개 변수). 5개 기관유형, 5개 지역, 10개 서비스분야 포함.</p></div>
    <div class="sc" style="--c:#e94560"><h3>만족도 현황</h3>
      <p>전체 평균 만족도 <strong>${KPI.avg_sat}점</strong>. 서비스분야·채널별 편차 존재.</p></div>
    <div class="sc" style="--c:#f5a623"><h3>지연 현황</h3>
      <p>전체 지연율 <strong>${KPI.delay_rate}%</strong>. 처리기준일수 초과 건 다수 발생.</p></div>
    <div class="sc" style="--c:#28a745"><h3>처리기간</h3>
      <p>평균 실제 처리일수 <strong>${KPI.avg_proc}일</strong>. 기관유형·긴급도별 차이 발생.</p></div>
    <div class="sc" style="--c:#6f42c1"><h3>행정비용</h3>
      <p>평균 행정비용 <strong>${KPI.avg_cost}만원</strong>. 서비스분야별 비용 구조 상이.</p></div>
    <div class="sc" style="--c:#17a2b8"><h3>취약계층</h3>
      <p>취약계층 비율 <strong>${KPI.vuln_rate}%</strong>. 일반 대비 지연율·재문의 비교 필요.</p></div>`;
})();

// ── 색상 ─────────────────────────────────────────────────
const C1=['#0f3460','#e94560','#f5a623','#28a745','#6f42c1','#17a2b8','#fd7e14','#20c997','#dc3545','#6c757d'];
const C2=['#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f','#edc948','#b07aa1','#ff9da7','#9c755f','#bab0ac'];

// ── Canvas 설정 ──────────────────────────────────────────
function cvSetup(id){
  const c=document.getElementById(id);
  const dpr=window.devicePixelRatio||1;
  const pw=c.parentElement.clientWidth-36;
  const ph=parseInt(c.getAttribute('height')||300);
  c.width=pw*dpr; c.height=ph*dpr;
  c.style.width=pw+'px'; c.style.height=ph+'px';
  const ctx=c.getContext('2d');
  ctx.scale(dpr,dpr);
  return {ctx,w:pw,h:ph};
}

// ── 둥근 사각형 ──────────────────────────────────────────
function rr(ctx,x,y,w,h,r){
  if(h<0){y+=h;h=-h;}
  if(w<0){x+=w;w=-w;}
  r=Math.min(r,w/2,h/2);
  ctx.beginPath();
  ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);
  ctx.quadraticCurveTo(x+w,y,x+w,y+r);
  ctx.lineTo(x+w,y+h-r);ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  ctx.lineTo(x+r,y+h);ctx.quadraticCurveTo(x,y+h,x,y+h-r);
  ctx.lineTo(x,y+r);ctx.quadraticCurveTo(x,y,x+r,y);
  ctx.closePath();ctx.fill();
}

// ── 수직 막대 ────────────────────────────────────────────
function drawBar(id,labels,vals,cols){
  const {ctx,w,h}=cvSetup(id);
  const p={t:30,r:16,b:68,l:56};
  const cw=w-p.l-p.r, ch=h-p.t-p.b;
  const mx=Math.max(...vals)*1.18||1;
  const gap=cw/labels.length, bw=gap*0.62;
  ctx.font='11px "Malgun Gothic",sans-serif';
  for(let i=0;i<=5;i++){
    const yv=mx/5*i, yp=p.t+ch*(1-yv/mx);
    ctx.strokeStyle=i===0?'#999':'#eaeaea'; ctx.lineWidth=i===0?1.5:1;
    ctx.beginPath();ctx.moveTo(p.l,yp);ctx.lineTo(p.l+cw,yp);ctx.stroke();
    ctx.fillStyle='#777';ctx.textAlign='right';
    ctx.fillText(Math.round(yv).toLocaleString(),p.l-5,yp+4);
  }
  ctx.strokeStyle='#999';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(p.l,p.t);ctx.lineTo(p.l,p.t+ch);ctx.stroke();
  labels.forEach((lbl,i)=>{
    const x=p.l+gap*i+(gap-bw)/2;
    const bh=ch*vals[i]/mx;
    ctx.fillStyle=cols[i%cols.length];
    rr(ctx,x,p.t+ch-bh,bw,bh,4);
    ctx.fillStyle='#222';ctx.textAlign='center';ctx.font='bold 11px "Malgun Gothic",sans-serif';
    ctx.fillText(vals[i].toLocaleString(),x+bw/2,p.t+ch-bh-5);
    ctx.save();
    ctx.translate(x+bw/2,p.t+ch+10);ctx.rotate(-0.42);
    ctx.textAlign='right';ctx.fillStyle='#444';ctx.font='11px "Malgun Gothic",sans-serif';
    ctx.fillText(lbl,0,0);ctx.restore();
  });
}

// ── 수평 막대 ────────────────────────────────────────────
function drawHBar(id,labels,vals,cols){
  const {ctx,w,h}=cvSetup(id);
  const p={t:14,r:70,b:14,l:78};
  const cw=w-p.l-p.r, ch=h-p.t-p.b;
  const mx=Math.max(...vals)*1.15||1;
  const gap=ch/labels.length, bh=gap*0.62;
  ctx.strokeStyle='#999';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(p.l,p.t);ctx.lineTo(p.l,p.t+ch);ctx.stroke();
  labels.forEach((lbl,i)=>{
    const y=p.t+gap*i+(gap-bh)/2;
    const bw=cw*vals[i]/mx;
    ctx.fillStyle=cols[i%cols.length];
    rr(ctx,p.l,y,bw,bh,4);
    ctx.fillStyle='#333';ctx.textAlign='right';
    ctx.font='12px "Malgun Gothic",sans-serif';
    ctx.fillText(lbl,p.l-7,y+bh/2+4);
    ctx.fillStyle='#111';ctx.textAlign='left';ctx.font='bold 11px "Malgun Gothic",sans-serif';
    ctx.fillText(vals[i].toLocaleString(),p.l+bw+5,y+bh/2+4);
  });
}

// ── 파이 ─────────────────────────────────────────────────
function drawPie(id,labels,vals,cols,legId){
  const {ctx,w,h}=cvSetup(id);
  const tot=vals.reduce((a,b)=>a+b,0);
  const cx=w/2,cy=h/2,r=Math.min(w,h)/2-18;
  let s=-Math.PI/2;
  vals.forEach((v,i)=>{
    const sw=2*Math.PI*v/tot;
    ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,s,s+sw);ctx.closePath();
    ctx.fillStyle=cols[i%cols.length];ctx.fill();
    ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();
    if(sw>0.18){
      const m=s+sw/2;
      ctx.fillStyle='#fff';ctx.textAlign='center';ctx.font='bold 11px "Malgun Gothic",sans-serif';
      ctx.fillText((v/tot*100).toFixed(1)+'%',cx+Math.cos(m)*r*.65,cy+Math.sin(m)*r*.65+4);
    }
    s+=sw;
  });
  if(legId)mkLeg(legId,labels,cols);
}

// ── 도넛 ─────────────────────────────────────────────────
function drawDnt(id,labels,vals,cols,legId){
  const {ctx,w,h}=cvSetup(id);
  const tot=vals.reduce((a,b)=>a+b,0);
  const cx=w/2,cy=h/2,r=Math.min(w,h)/2-18,ir=r*.52;
  let s=-Math.PI/2;
  vals.forEach((v,i)=>{
    const sw=2*Math.PI*v/tot;
    ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,s,s+sw);ctx.closePath();
    ctx.fillStyle=cols[i%cols.length];ctx.fill();
    ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();
    if(sw>0.22){
      const m=s+sw/2;
      ctx.fillStyle='#fff';ctx.textAlign='center';ctx.font='bold 11px "Malgun Gothic",sans-serif';
      ctx.fillText((v/tot*100).toFixed(1)+'%',cx+Math.cos(m)*r*.73,cy+Math.sin(m)*r*.73+4);
    }
    s+=sw;
  });
  ctx.beginPath();ctx.arc(cx,cy,ir,0,2*Math.PI);
  ctx.fillStyle='#fff';ctx.fill();
  ctx.fillStyle='#1a1a2e';ctx.textAlign='center';
  ctx.font='bold 15px "Malgun Gothic",sans-serif';
  ctx.fillText(tot.toLocaleString(),cx,cy-2);
  ctx.font='11px "Malgun Gothic",sans-serif';ctx.fillStyle='#64748b';
  ctx.fillText('총 건수',cx,cy+16);
  if(legId)mkLeg(legId,labels,cols);
}

// ── 꺾은선 ──────────────────────────────────────────────
function drawLine(id,labels,vals){
  const {ctx,w,h}=cvSetup(id);
  const p={t:30,r:20,b:50,l:58};
  const cw=w-p.l-p.r, ch=h-p.t-p.b;
  const mn=Math.min(...vals)*.88, mx=Math.max(...vals)*1.14||1;
  const rng=mx-mn||1;
  const yp=v=>p.t+ch*(1-(v-mn)/rng);
  for(let i=0;i<=5;i++){
    const v=mn+rng/5*i, y=yp(v);
    ctx.strokeStyle=i===0?'#999':'#eaeaea';ctx.lineWidth=i===0?1.5:1;
    ctx.beginPath();ctx.moveTo(p.l,y);ctx.lineTo(p.l+cw,y);ctx.stroke();
    ctx.fillStyle='#777';ctx.textAlign='right';ctx.font='11px "Malgun Gothic",sans-serif';
    ctx.fillText(Math.round(v),p.l-5,y+4);
  }
  ctx.strokeStyle='#999';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(p.l,p.t);ctx.lineTo(p.l,p.t+ch);ctx.stroke();
  const pts=labels.map((_,i)=>({x:p.l+cw*i/(labels.length-1),y:yp(vals[i])}));
  // 채움
  ctx.beginPath();ctx.moveTo(pts[0].x,p.t+ch);
  pts.forEach(pt=>ctx.lineTo(pt.x,pt.y));
  ctx.lineTo(pts[pts.length-1].x,p.t+ch);ctx.closePath();
  ctx.fillStyle='rgba(15,52,96,.1)';ctx.fill();
  // 선
  ctx.beginPath();ctx.strokeStyle='#0f3460';ctx.lineWidth=2.5;ctx.lineJoin='round';
  pts.forEach((pt,i)=>i===0?ctx.moveTo(pt.x,pt.y):ctx.lineTo(pt.x,pt.y));
  ctx.stroke();
  // 점·값·라벨
  pts.forEach((pt,i)=>{
    ctx.beginPath();ctx.arc(pt.x,pt.y,4,0,2*Math.PI);
    ctx.fillStyle='#0f3460';ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.stroke();
    ctx.fillStyle='#222';ctx.textAlign='center';ctx.font='bold 10px "Malgun Gothic",sans-serif';
    ctx.fillText(vals[i],pt.x,pt.y-9);
    ctx.fillStyle='#555';ctx.font='11px "Malgun Gothic",sans-serif';
    ctx.fillText(labels[i],pt.x,p.t+ch+17);
  });
}

// ── 묶음 막대 ────────────────────────────────────────────
function drawGrp(id,labels,datasets,cols,legId){
  const {ctx,w,h}=cvSetup(id);
  const p={t:30,r:16,b:68,l:56};
  const cw=w-p.l-p.r, ch=h-p.t-p.b;
  const all=datasets.flatMap(d=>d.values);
  const mx=Math.max(...all)*1.18||1;
  const n=datasets.length, gap=cw/labels.length, grpW=gap*.72, bw=grpW/n;
  for(let i=0;i<=5;i++){
    const v=mx/5*i, y=p.t+ch*(1-v/mx);
    ctx.strokeStyle=i===0?'#999':'#eaeaea';ctx.lineWidth=i===0?1.5:1;
    ctx.beginPath();ctx.moveTo(p.l,y);ctx.lineTo(p.l+cw,y);ctx.stroke();
    ctx.fillStyle='#777';ctx.textAlign='right';ctx.font='11px "Malgun Gothic",sans-serif';
    ctx.fillText(v.toFixed(1),p.l-5,y+4);
  }
  ctx.strokeStyle='#999';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(p.l,p.t);ctx.lineTo(p.l,p.t+ch);ctx.stroke();
  labels.forEach((lbl,i)=>{
    const gx=p.l+gap*i+(gap-grpW)/2;
    datasets.forEach((ds,j)=>{
      const x=gx+bw*j, bh=ch*ds.values[i]/mx;
      ctx.fillStyle=cols[j%cols.length];
      rr(ctx,x+1,p.t+ch-bh,bw-2,bh,3);
      ctx.fillStyle='#222';ctx.textAlign='center';ctx.font='10px "Malgun Gothic",sans-serif';
      ctx.fillText(ds.values[i],x+bw/2,p.t+ch-bh-5);
    });
    ctx.save();
    ctx.translate(p.l+gap*i+gap/2,p.t+ch+10);ctx.rotate(-0.42);
    ctx.textAlign='right';ctx.fillStyle='#444';ctx.font='11px "Malgun Gothic",sans-serif';
    ctx.fillText(lbl,0,0);ctx.restore();
  });
  if(legId)mkLeg(legId,datasets.map(d=>d.label),cols);
}

// ── 누적 막대 ────────────────────────────────────────────
function drawStk(id,labels,datasets,cols,legId){
  const {ctx,w,h}=cvSetup(id);
  const p={t:30,r:16,b:60,l:56};
  const cw=w-p.l-p.r, ch=h-p.t-p.b;
  const tots=labels.map((_,i)=>datasets.reduce((s,d)=>s+d.values[i],0));
  const mx=Math.max(...tots)*1.12||1;
  const gap=cw/labels.length, bw=gap*.62;
  for(let i=0;i<=5;i++){
    const v=mx/5*i, y=p.t+ch*(1-v/mx);
    ctx.strokeStyle=i===0?'#999':'#eaeaea';ctx.lineWidth=i===0?1.5:1;
    ctx.beginPath();ctx.moveTo(p.l,y);ctx.lineTo(p.l+cw,y);ctx.stroke();
    ctx.fillStyle='#777';ctx.textAlign='right';ctx.font='11px "Malgun Gothic",sans-serif';
    ctx.fillText(Math.round(v),p.l-5,y+4);
  }
  ctx.strokeStyle='#999';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(p.l,p.t);ctx.lineTo(p.l,p.t+ch);ctx.stroke();
  labels.forEach((lbl,i)=>{
    const x=p.l+gap*i+(gap-bw)/2;
    let cum=0;
    datasets.forEach((ds,j)=>{
      const v=ds.values[i], bh=ch*v/mx, y=p.t+ch*(1-(cum+v)/mx);
      ctx.fillStyle=cols[j%cols.length];
      ctx.fillRect(x,y,bw,bh);
      if(bh>14){
        ctx.fillStyle='#fff';ctx.textAlign='center';ctx.font='bold 10px "Malgun Gothic",sans-serif';
        ctx.fillText(v,x+bw/2,y+bh/2+4);
      }
      cum+=v;
    });
    const ty=p.t+ch*(1-tots[i]/mx);
    ctx.fillStyle='#222';ctx.textAlign='center';ctx.font='bold 10px "Malgun Gothic",sans-serif';
    ctx.fillText(tots[i],x+bw/2,ty-5);
    ctx.save();
    ctx.translate(x+bw/2,p.t+ch+10);ctx.rotate(-0.35);
    ctx.textAlign='right';ctx.fillStyle='#444';ctx.font='11px "Malgun Gothic",sans-serif';
    ctx.fillText(lbl,0,0);ctx.restore();
  });
  if(legId)mkLeg(legId,datasets.map(d=>d.label),cols);
}

// ── 범례 ─────────────────────────────────────────────────
function mkLeg(id,labels,cols){
  const el=document.getElementById(id);
  if(!el)return;
  el.innerHTML=labels.map((l,i)=>
    `<div class="li"><div class="lb" style="background:${cols[i%cols.length]}"></div>${l}</div>`
  ).join('');
}

// ── 차트 렌더 ────────────────────────────────────────────
let d1=false,d2=false;
function drawCharts1(){
  if(d1)return;d1=true;
  setTimeout(()=>{
    drawBar('cv1',CHARTS.c1.labels,CHARTS.c1.values,C1);
    drawHBar('cv2',CHARTS.c2.labels,CHARTS.c2.values,C2);
    drawPie('cv3',CHARTS.c3.labels,CHARTS.c3.values,C1,'leg3');
    drawDnt('cv4',CHARTS.c4.labels,CHARTS.c4.values,C2,'leg4');
    drawBar('cv5',CHARTS.c5.labels,CHARTS.c5.values,C1);
  },60);
}
function drawCharts2(){
  if(d2)return;d2=true;
  setTimeout(()=>{
    drawLine('cv6',CHARTS.c6.labels,CHARTS.c6.values);
    drawBar('cv7',CHARTS.c7.labels,CHARTS.c7.values,C2);
    drawGrp('cv8',CHARTS.c8.labels,CHARTS.c8.datasets,[C1[0],C1[1]],'leg8');
    drawDnt('cv9',CHARTS.c9.labels,CHARTS.c9.values,['#28a745','#e94560'],'leg9');
    drawStk('cv10',CHARTS.c10.labels,CHARTS.c10.datasets,['#28a745','#e94560'],'leg10');
  },60);
}
"""

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>공공부문 민원 데이터 분석 대시보드</title>
<style>{CSS}</style>
</head>
<body>

<header class="hdr">
  <h1>공공부문 민원 데이터 분석 대시보드</h1>
  <p>데이터 기준 : 2025년 공공기관 민원 접수 현황 &nbsp;|&nbsp; 총 3,000건 &nbsp;|&nbsp; 20개 변수</p>
</header>

<nav class="tab-nav">
  <button class="tab-btn active"  onclick="showTab('ov',this)">개요</button>
  <button class="tab-btn"         onclick="showTab('ch1',this)">그래프 01~05</button>
  <button class="tab-btn"         onclick="showTab('ch2',this)">그래프 06~10</button>
  <button class="tab-btn"         onclick="showTab('tb1',this)">통계표 01~08</button>
  <button class="tab-btn"         onclick="showTab('tb2',this)">통계표 09~15</button>
</nav>

<!-- 개요 -->
<section id="ov" class="page active">
  <div class="kpi-grid" id="kpi"></div>
  <div class="sg" id="sg"></div>
</section>

<!-- 그래프 01~05 -->
<section id="ch1" class="page">
  <div class="cg">
    <div class="cc"><div class="ct">그래프 01. 기관유형별 민원 건수</div>
      <canvas id="cv1" height="280"></canvas></div>
    <div class="cc"><div class="ct">그래프 02. 지역별 민원 건수 (수평 막대)</div>
      <canvas id="cv2" height="280"></canvas></div>
    <div class="cc"><div class="ct">그래프 03. 서비스분야별 분포 (파이차트)</div>
      <canvas id="cv3" height="300"></canvas><div class="leg" id="leg3"></div></div>
    <div class="cc"><div class="ct">그래프 04. 민원채널별 분포 (도넛차트)</div>
      <canvas id="cv4" height="300"></canvas><div class="leg" id="leg4"></div></div>
    <div class="cc wide"><div class="ct">그래프 05. 신청자연령대별 분포</div>
      <canvas id="cv5" height="260"></canvas></div>
  </div>
</section>

<!-- 그래프 06~10 -->
<section id="ch2" class="page">
  <div class="cg">
    <div class="cc wide"><div class="ct">그래프 06. 월별 민원 접수 추이 (꺾은선)</div>
      <canvas id="cv6" height="260"></canvas></div>
    <div class="cc"><div class="ct">그래프 07. 만족도 점수 구간별 분포</div>
      <canvas id="cv7" height="280"></canvas></div>
    <div class="cc"><div class="ct">그래프 08. 기관유형별 처리기간 비교 (묶음 막대)</div>
      <canvas id="cv8" height="280"></canvas><div class="leg" id="leg8"></div></div>
    <div class="cc"><div class="ct">그래프 09. 지연여부 분포 (도넛차트)</div>
      <canvas id="cv9" height="300"></canvas><div class="leg" id="leg9"></div></div>
    <div class="cc"><div class="ct">그래프 10. 긴급도별 지연 현황 (누적 막대)</div>
      <canvas id="cv10" height="280"></canvas><div class="leg" id="leg10"></div></div>
  </div>
</section>

<!-- 통계표 01~08 -->
<section id="tb1" class="page">
{S1}
</section>

<!-- 통계표 09~15 -->
<section id="tb2" class="page">
{S2}
</section>

<script>
{JS}
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

sz = os.path.getsize(OUTPUT)
print(f"완료: {OUTPUT}")
print(f"크기: {sz/1024:.1f} KB")
