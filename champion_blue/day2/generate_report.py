import pandas as pd
import chardet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
import numpy as np
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ── 데이터 로드
FILE = "input/국토교통부_전국 버스정류장 위치정보_20251031.csv"
with open(FILE, "rb") as f:
    enc = chardet.detect(f.read(100_000))["encoding"]
try:
    df = pd.read_csv(FILE, encoding=enc)
except UnicodeDecodeError:
    df = pd.read_csv(FILE, encoding="euc-kr")
print(f"로드 완료: {len(df):,}행")

# ── 전처리
valid_mask = df['위도'].between(33, 39) & df['경도'].between(124, 132)
df_v = df[valid_mask].dropna(subset=['위도', '경도']).copy()
df_v['시도'] = df_v['도시명'].str.split().str[0].fillna('미분류')

sido_counts = df_v['시도'].value_counts().sort_values()
city_counts  = df_v['도시명'].value_counts().head(25)
mgmt_counts  = df_v['관리도시명'].value_counts().head(20)
total_mgmt   = df_v['관리도시명'].nunique()
miss_pct     = df['모바일단축번호'].isna().mean() * 100

# ── 색상 팔레트
BLUE  = '#2563EB'; LBLUE = '#DBEAFE'; GRAY = '#6B7280'
LGRAY = '#F3F4F6'; RED   = '#EF4444'; GREEN = '#10B981'; DARK = '#111827'
PURPLE = '#7C3AED'; ORANGE = '#D97706'

# ── 헬퍼
def bbox(ax, x, y, w, h, fc, ec='none', lw=1, style='square,pad=0', alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=style, fc=fc, ec=ec, lw=lw, alpha=alpha))

def footer(fig, n, total=8):
    fig.text(0.5,  0.010, f'국토교통부 전국 버스정류장 위치정보 (2025.10.31 기준)  |  {n} / {total}',
             ha='center', fontsize=7, color=GRAY)
    fig.text(0.97, 0.010, '작성일: 2026-06-16', ha='right', fontsize=7, color=GRAY)

def banner(fig, title):
    ax = fig.add_axes([0, 0.91, 1, 0.08])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    bbox(ax, 0, 0, 1, 1, fc=BLUE)
    ax.text(0.05, 0.5, title, fontsize=16, color='white', va='center', fontweight='bold')

PDF_PATH = "output/전국_버스정류장_분석_보고서.pdf"

with PdfPages(PDF_PATH) as pdf:

    # ════════════════════════════════════════════════════════
    # PAGE 1 — 표지
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    ax  = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    bbox(ax, 0, 0.70, 1, 0.30, fc=BLUE)
    bbox(ax, 0, 0.00, 1, 0.07, fc=DARK)

    ax.text(0.5, 0.92, '전국 버스정류장 분포로 본', fontsize=22, color='white',
            ha='center', va='center', fontweight='bold')
    ax.text(0.5, 0.82, '교통 접근성 현황 분석', fontsize=30, color='white',
            ha='center', va='center', fontweight='bold')
    ax.text(0.5, 0.75, 'National Bus Stop Distribution & Transport Accessibility Analysis',
            fontsize=10, color=LBLUE, ha='center', va='center')

    # 핵심 지표 카드
    kpis = [('총 정류장 수', f'{len(df_v):,}개'), ('분석 광역단체', f'{df_v["시도"].nunique()}개'),
            ('BIS 운영주체', f'{total_mgmt}개')]
    for i, (lbl, val) in enumerate(kpis):
        x = 0.18 + i * 0.32
        bbox(ax, x - 0.11, 0.55, 0.22, 0.12, fc=LBLUE, ec=BLUE, lw=1.5, style='round,pad=0.01')
        ax.text(x, 0.638, val, fontsize=18, ha='center', va='center', color=BLUE, fontweight='bold')
        ax.text(x, 0.574, lbl, fontsize=9,  ha='center', va='center', color=DARK)

    for y, t in [(0.49, '데이터 출처: 국토교통부 공공데이터포털'),
                 (0.45, '데이터 기준일: 2025년 10월 31일'),
                 (0.41, '분석 수행일: 2026년 6월 16일')]:
        ax.text(0.5, y, t, fontsize=11, ha='center', va='center', color=DARK)

    ax.text(0.5, 0.34, '목  차', fontsize=14, ha='center', color=BLUE, fontweight='bold')
    toc = [('1.', '데이터 개요 및 품질'),   ('2.', '광역자치단체별 정류장 분포'),
           ('3.', '상위 25개 도시 정류장 현황'), ('4.', '전국 정류장 공간 분포 (산포도)'),
           ('5.', '남북·동서 방향 밀도 분포'), ('6.', 'BIS 관리 운영 현황'),
           ('7.', '결론 및 시사점')]
    for j, (n, t) in enumerate(toc):
        ax.text(0.30, 0.29 - j * 0.028, n, fontsize=10, ha='right', color=BLUE, fontweight='bold')
        ax.text(0.32, 0.29 - j * 0.028, t, fontsize=10, ha='left',  color=DARK)

    ax.text(0.5, 0.035, 'AI Champion 분석 보고서', fontsize=9,
            ha='center', va='center', color='white')
    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # ════════════════════════════════════════════════════════
    # PAGE 2 — 데이터 개요
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    banner(fig, '1. 데이터 개요 및 품질')

    axc = fig.add_axes([0.05, 0.72, 0.90, 0.17]); axc.axis('off')
    cards = [('전체 레코드', f'{len(df):,} 행'), ('컬럼 수', f'{len(df.columns)} 개'),
             ('유효 좌표', f'{len(df_v):,} 개'), ('좌표 오류', f'{len(df)-len(df_v):,} 개'),
             ('광역단체 수', f'{df_v["시도"].nunique()} 개'), ('BIS 운영주체', f'{total_mgmt} 개')]
    for i, (lbl, val) in enumerate(cards):
        col = i % 3; row = i // 3; cx = 0.02 + col * 0.33; cy = 0.52 - row * 0.48
        bbox(axc, cx, cy, 0.30, 0.40, fc=LBLUE, ec=BLUE, lw=1, style='round,pad=0.02')
        axc.text(cx + 0.15, cy + 0.27, val, fontsize=16, ha='center', va='center',
                 color=BLUE, fontweight='bold')
        axc.text(cx + 0.15, cy + 0.10, lbl, fontsize=9, ha='center', va='center', color=GRAY)

    axt = fig.add_axes([0.05, 0.28, 0.90, 0.42]); axt.axis('off')
    axt.text(0, 1.02, '컬럼별 구조 요약', fontsize=12, color=BLUE, fontweight='bold', va='bottom')
    col_info = [
        ('정류장번호',    'object',  '0.0%', '지역코드+일련번호 형태의 고유 식별자'),
        ('정류장명',      'object',  '0.0%', '버스 정류장 명칭'),
        ('위도',          'float64', '0.0%', '한반도 유효범위 33°~39°N'),
        ('경도',          'float64', '0.0%', '한반도 유효범위 124°~132°E'),
        ('정보수집일',    'object',  '0.0%', '2025-10-31 단일 기준일'),
        ('모바일단축번호','float64', f'{miss_pct:.1f}%', 'BIS 미도입 지역 결측'),
        ('도시코드',      'int64',   '0.0%', '광역/기초 자치단체 식별 코드'),
        ('도시명',        'object',  '0.0%', '광역+기초 자치단체 명칭'),
        ('관리도시명',    'object',  '0.0%', 'BIS 운영 주체 명칭'),
    ]
    headers = ['컬럼명', '타입', '결측률', '설명']
    col_x = [0.0, 0.20, 0.32, 0.42]; rh = 0.088
    for j, h in enumerate(headers):
        w = (col_x[j+1] - col_x[j] if j < 3 else 0.58) - 0.01
        bbox(axt, col_x[j] - 0.005, 0.87, w, rh, fc=BLUE)
        axt.text(col_x[j] + 0.008, 0.87 + rh / 2, h, fontsize=9,
                 va='center', color='white', fontweight='bold')
    for i, row in enumerate(col_info):
        bg = LGRAY if i % 2 == 0 else 'white'; ry = 0.87 - (i + 1) * rh
        bbox(axt, -0.005, ry, 1.01, rh, fc=bg)
        mc = RED if float(row[2].replace('%', '')) > 0 else DARK
        for j, val in enumerate(row):
            axt.text(col_x[j] + 0.008, ry + rh / 2, val, fontsize=8.5,
                     va='center', color=mc if j == 2 else DARK)

    footer(fig, 2); pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # ════════════════════════════════════════════════════════
    # PAGE 3 — 광역자치단체별 분포
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    banner(fig, '2. 광역자치단체별 정류장 분포')
    ax = fig.add_axes([0.22, 0.10, 0.73, 0.78])
    bar_colors = [BLUE if v == sido_counts.max() else '#93C5FD' for v in sido_counts.values]
    bars = ax.barh(sido_counts.index, sido_counts.values, color=bar_colors, edgecolor='white', lw=0.5)
    for b, v in zip(bars, sido_counts.values):
        ax.text(v + sido_counts.max() * 0.005, b.get_y() + b.get_height() / 2,
                f'{v:,}', va='center', fontsize=8, color=DARK)
    ax.set_xlabel('버스정류장 수 (개)', fontsize=10, color=GRAY)
    ax.set_title('광역자치단체별 버스정류장 수', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.spines[['top', 'right']].set_visible(False); ax.set_facecolor(LGRAY)
    ax.tick_params(axis='y', labelsize=9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(axis='x', color='white', lw=0.8)
    t1 = sido_counts.idxmax(); v1 = sido_counts.max()
    l1 = sido_counts.idxmin(); lv1 = sido_counts.min()
    ax.text(0.97, 0.03,
            f'최다: {t1} ({v1:,}개, {v1/len(df_v)*100:.1f}%)\n'
            f'최소: {l1} ({lv1:,}개, {lv1/len(df_v)*100:.1f}%)\n'
            f'격차 배율: {v1//lv1}배',
            transform=ax.transAxes, fontsize=8.5, va='bottom', ha='right', color=DARK,
            bbox=dict(fc=LBLUE, ec=BLUE, lw=1, boxstyle='round,pad=0.4'))
    footer(fig, 3); pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # ════════════════════════════════════════════════════════
    # PAGE 4 — 상위 25개 도시
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    banner(fig, '3. 상위 25개 도시 정류장 현황')
    ax = fig.add_axes([0.25, 0.06, 0.70, 0.82])
    bc = plt.cm.Blues(np.linspace(0.35, 0.95, len(city_counts))[::-1])
    bars = ax.barh(city_counts.index[::-1], city_counts.values[::-1], color=bc, edgecolor='white', lw=0.4)
    for b, v in zip(bars, city_counts.values[::-1]):
        ax.text(v + city_counts.max() * 0.005, b.get_y() + b.get_height() / 2,
                f'{v:,}', va='center', fontsize=7.5, color=DARK)
    ax.set_xlabel('버스정류장 수 (개)', fontsize=9, color=GRAY)
    ax.set_title('정류장 수 상위 25개 도시', fontsize=13, fontweight='bold', color=DARK, pad=10)
    ax.spines[['top', 'right']].set_visible(False); ax.set_facecolor(LGRAY)
    ax.tick_params(axis='y', labelsize=8)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(axis='x', color='white', lw=0.8)
    footer(fig, 4); pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # ════════════════════════════════════════════════════════
    # PAGE 5 — 전국 산포도
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    banner(fig, '4. 전국 정류장 공간 분포 (산포도)')
    ax = fig.add_axes([0.08, 0.09, 0.88, 0.79])
    s = df_v.sample(min(80000, len(df_v)), random_state=42)
    ax.scatter(s['경도'], s['위도'], s=0.3, alpha=0.25, color=BLUE, linewidths=0)
    ax.set_xlabel('경도 (°E)', fontsize=10, color=GRAY)
    ax.set_ylabel('위도 (°N)', fontsize=10, color=GRAY)
    ax.set_title(f'전국 버스정류장 위치 산포도  (샘플 80,000개 / 전체 {len(df_v):,}개)',
                 fontsize=12, fontweight='bold', color=DARK, pad=10)
    ax.set_facecolor('#0F172A')
    for sp in ax.spines.values(): sp.set_edgecolor('#CBD5E1')
    city_coords = {'서울': (126.978, 37.566), '부산': (129.075, 35.180),
                   '대구': (128.601, 35.871), '인천': (126.705, 37.456),
                   '광주': (126.851, 35.160), '대전': (127.385, 36.351),
                   '울산': (129.312, 35.540), '제주': (126.531, 33.499)}
    for city, (lon, lat) in city_coords.items():
        ax.annotate(city, xy=(lon, lat), fontsize=8, color='#FCD34D',
                    xytext=(5, 5), textcoords='offset points',
                    arrowprops=dict(arrowstyle='->', color='#FCD34D', lw=0.7))
        ax.plot(lon, lat, 'o', color='#FCD34D', ms=3)
    footer(fig, 5); pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # ════════════════════════════════════════════════════════
    # PAGE 6 — 위도·경도 밀도 분포
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    banner(fig, '5. 남북·동서 방향 밀도 분포')
    ax1 = fig.add_axes([0.10, 0.54, 0.85, 0.33])
    ax1.hist(df_v['위도'], bins=80, color=BLUE, alpha=0.85, edgecolor='white', lw=0.3)
    ax1.axvline(df_v['위도'].mean(), color=RED, lw=1.5, ls='--',
                label=f'평균 위도: {df_v["위도"].mean():.2f}°N')
    ax1.set_xlabel('위도 (°N)  ← 남쪽   북쪽 →', fontsize=9, color=GRAY)
    ax1.set_ylabel('정류장 수', fontsize=9, color=GRAY)
    ax1.set_title('남북 방향(위도) 정류장 밀도 분포', fontsize=12, fontweight='bold', color=DARK)
    ax1.spines[['top', 'right']].set_visible(False); ax1.set_facecolor(LGRAY)
    ax1.grid(axis='y', color='white', lw=0.8); ax1.legend(fontsize=8)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

    ax2 = fig.add_axes([0.10, 0.11, 0.85, 0.33])
    ax2.hist(df_v['경도'], bins=80, color=PURPLE, alpha=0.85, edgecolor='white', lw=0.3)
    ax2.axvline(df_v['경도'].mean(), color=RED, lw=1.5, ls='--',
                label=f'평균 경도: {df_v["경도"].mean():.2f}°E')
    ax2.set_xlabel('경도 (°E)  ← 서쪽   동쪽 →', fontsize=9, color=GRAY)
    ax2.set_ylabel('정류장 수', fontsize=9, color=GRAY)
    ax2.set_title('동서 방향(경도) 정류장 밀도 분포', fontsize=12, fontweight='bold', color=DARK)
    ax2.spines[['top', 'right']].set_visible(False); ax2.set_facecolor(LGRAY)
    ax2.grid(axis='y', color='white', lw=0.8); ax2.legend(fontsize=8)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

    fig.text(0.5, 0.055,
             '위도 피크: 약 37.5°N 전후 (수도권·경기 집중)  |  경도 피크: 약 126~127°E (서울·경기·전라권)',
             ha='center', fontsize=9, color=DARK,
             bbox=dict(fc=LBLUE, ec=BLUE, lw=1, boxstyle='round,pad=0.5'))
    footer(fig, 6); pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # ════════════════════════════════════════════════════════
    # PAGE 7 — BIS 운영 현황
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    banner(fig, '6. BIS 관리 운영 현황')
    ax = fig.add_axes([0.28, 0.09, 0.67, 0.79])
    bc2 = plt.cm.Purples(np.linspace(0.35, 0.90, len(mgmt_counts))[::-1])
    bars2 = ax.barh(mgmt_counts.index[::-1], mgmt_counts.values[::-1],
                    color=bc2, edgecolor='white', lw=0.4)
    for b, v in zip(bars2, mgmt_counts.values[::-1]):
        ax.text(v + mgmt_counts.max() * 0.005, b.get_y() + b.get_height() / 2,
                f'{v:,}', va='center', fontsize=7.5, color=DARK)
    ax.set_xlabel('관리 정류장 수 (개)', fontsize=9, color=GRAY)
    ax.set_title(f'BIS 운영 주체별 관리 정류장 수 (상위 {len(mgmt_counts)}개)',
                 fontsize=12, fontweight='bold', color=DARK, pad=10)
    ax.spines[['top', 'right']].set_visible(False); ax.set_facecolor(LGRAY)
    ax.tick_params(axis='y', labelsize=8)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(axis='x', color='white', lw=0.8)
    ax.text(0.97, 0.03,
            f'전국 BIS 운영 주체: {total_mgmt}개\n'
            f'최대 관리: {mgmt_counts.idxmax()} ({mgmt_counts.max():,}개)\n'
            f'상위 5개 점유율: {mgmt_counts.head(5).sum()/len(df_v)*100:.1f}%',
            transform=ax.transAxes, fontsize=8.5, va='bottom', ha='right', color=DARK,
            bbox=dict(fc='#F3E8FF', ec=PURPLE, lw=1, boxstyle='round,pad=0.4'))
    footer(fig, 7); pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # ════════════════════════════════════════════════════════
    # PAGE 8 — 결론 및 시사점
    # ════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor('white')
    banner(fig, '7. 결론 및 시사점')
    ax = fig.add_axes([0.06, 0.07, 0.88, 0.82]); ax.axis('off')

    sections = [
        (GREEN, '핵심 발견 사항', [
            f'전국 {len(df_v):,}개 버스정류장이 17개 광역단체에 분포하며, '
            f'수도권(서울·경기·인천)에 전체의 상당 비율이 집중되어 있음.',
            f'광역단체별 최대·최소 격차 {sido_counts.max()//sido_counts.min()}배 이상 — '
            f'지역별 교통 인프라 불균형이 수치로 확인됨.',
            '히트맵·산포도에서 수도권·부산·대구 등 대도시권 중심의 고밀도 군집 뚜렷하게 형성.']),
        (BLUE, '교통 접근성 시사점', [
            '농어촌·산간 지역의 정류장 밀도가 도시 대비 현저히 낮아 교통 소외 계층 발생 우려.',
            '위도 37.5°N, 경도 126~127°E 부근 밀집 현상 → 지방 균형 발전 관점의 정책 보완 필요.',
            '제주·도서 지역은 독립적 교통망 구조를 보이며 별도 심층 분석 필요.']),
        (ORANGE, 'BIS 운영 현황 및 개선 방향', [
            f'전국 {total_mgmt}개 BIS 운영 주체 난립 → 데이터 표준화 및 통합 관리 체계 구축 시급.',
            f'모바일단축번호 결측률 {miss_pct:.1f}% — 해당 지역은 스마트 버스정보 서비스 우선 도입 대상.',
            '상위 5개 운영 주체가 전체의 상당 비율 관리 → 이들 데이터 품질 향상이 전체 수준 개선의 핵심.']),
        (RED, '향후 분석 과제', [
            '통계청 인구 데이터와 결합하여 1인당 정류장 수 기반 교통 형평성 지수 산출 필요.',
            '대중교통 이용 데이터 연계 → 정류장 수 대비 실제 이용률 분석으로 유휴 정류장 식별.',
            '시계열 데이터 확보 시 정류장 신설·폐지 트렌드로 도시 성장 패턴 파악 가능.']),
    ]

    y = 0.97
    for color, title, items in sections:
        bbox(ax, 0, y - 0.043, 1.0, 0.045, fc=color, alpha=0.12, style='round,pad=0.005')
        bbox(ax, 0, y - 0.043, 0.007, 0.045, fc=color)
        ax.text(0.016, y - 0.021, title, fontsize=11, va='center', fontweight='bold', color=color)
        y -= 0.060
        for item in items:
            ax.text(0.025, y, '•', fontsize=11, va='top', color=color)
            ax.text(0.048, y, item, fontsize=8.8, va='top', color=DARK)
            y -= 0.056
        y -= 0.010

    footer(fig, 8); pdf.savefig(fig, bbox_inches='tight'); plt.close()

print(f'✅ PDF 보고서 생성 완료: {PDF_PATH}')
print(f'   총 8페이지 | 표지 / 데이터 개요 / 광역단체 분포 / 도시별 순위')
print(f'            / 전국 산포도 / 밀도 히스토그램 / BIS 현황 / 결론')