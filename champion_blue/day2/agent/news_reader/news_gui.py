# -*- coding: utf-8 -*-
"""
대한민국 정책브리핑 뉴스 리더 (Python tkinter GUI)
RSS 출처: https://www.korea.kr/rss/policy.xml 외
"""
import tkinter as tk
from tkinter import ttk
import urllib.request
import ssl
import xml.etree.ElementTree as ET
import webbrowser
import threading
import os
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from html import unescape
import re

# ── 로그 파일 (홈 디렉터리) ────────────────────────────────────────
LOG_PATH = os.path.join(os.path.expanduser('~'), 'news_reader.log')
logging.basicConfig(
    filename=LOG_PATH, level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
LOG = logging.getLogger(__name__)

# ── RSS 피드 ──────────────────────────────────────────────────────
RSS_FEEDS = {
    '정책뉴스': 'https://www.korea.kr/rss/policy.xml',
    '보도자료': 'https://www.korea.kr/rss/pressrelease.xml',
    '오피니언': 'https://www.korea.kr/rss/reporter.xml',
    '칼럼':    'https://www.korea.kr/rss/column.xml',
}

# ── 색상 ──────────────────────────────────────────────────────────
BG      = '#0d1117'
SURFACE = '#161b22'
CARD    = '#1c2128'
HOVER   = '#252d38'
BORDER  = '#30363d'
TEXT    = '#e6edf3'
MUTED   = '#8b949e'
DIM     = '#3d444d'
ACCENT  = '#2f81f7'

CAT_COLOR = {
    '정책뉴스': '#2f81f7',
    '보도자료': '#3fb950',
    '오피니언': '#bc8cff',
    '칼럼':    '#d29922',
}

BATCH_SIZE = 20   # 한 번에 렌더링할 카드 수


# ── 유틸 ─────────────────────────────────────────────────────────
def clean(text: str) -> str:
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()

def fmt_date(s: str) -> str:
    if not s:
        return ''
    for fmt in ('%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S GMT',
                '%a, %d %b %Y %H:%M:%S +0000'):
        try:
            return datetime.strptime(s.strip(), fmt).strftime('%Y.%m.%d %H:%M')
        except ValueError:
            pass
    return s[:16]

def ssl_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def fetch_rss(url: str, label: str) -> list:
    LOG.info('fetch_rss 시작: %s', label)
    req = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0 (compatible; NewsReader/1.0)'}
    )
    with urllib.request.urlopen(req, context=ssl_ctx(), timeout=8) as r:
        data = r.read()
    LOG.info('fetch_rss 데이터 수신: %s  %d bytes', label, len(data))
    root = ET.fromstring(data)
    ch = root.find('channel')
    items = []
    for it in (ch.findall('item') if ch is not None else []):
        def g(t, _it=it):
            e = _it.find(t)
            return (e.text or '') if e is not None else ''
        desc = clean(g('description'))
        items.append({
            'title':    clean(g('title')),
            'link':     g('link').strip(),
            'desc':     desc[:130] + '…' if len(desc) > 130 else desc,
            'date':     fmt_date(g('pubDate')),
            'raw_date': g('pubDate'),
            'category': label,
        })
    LOG.info('fetch_rss 파싱 완료: %s  %d개', label, len(items))
    return items


# ── 카드 위젯 (Frame 기반, Canvas 없이 빠른 렌더링) ───────────────
def make_card(parent, item: dict, scroll_cmd) -> tk.Frame:
    cat   = item['category']
    color = CAT_COLOR.get(cat, ACCENT)

    outer = tk.Frame(parent, bg=color, padx=0, pady=2)

    inner = tk.Frame(outer, bg=CARD, padx=14, pady=10, cursor='hand2')
    inner.pack(fill=tk.BOTH, expand=True)

    # 상단: 뱃지 + 날짜
    top = tk.Frame(inner, bg=CARD)
    top.pack(fill=tk.X)
    tk.Label(top, text=f'  {cat}  ',
             bg=color, fg='#000',
             font=('Malgun Gothic', 9, 'bold')).pack(side=tk.LEFT)
    tk.Label(top, text=item['date'],
             bg=CARD, fg=MUTED,
             font=('Malgun Gothic', 8)).pack(side=tk.RIGHT)

    # 제목
    title_lbl = tk.Label(inner, text=item['title'],
                          bg=CARD, fg=TEXT,
                          font=('Malgun Gothic', 11, 'bold'),
                          anchor='w', justify='left', wraplength=380)
    title_lbl.pack(fill=tk.X, pady=(6, 3))

    # 구분선
    tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X)

    # 본문
    tk.Label(inner, text=item['desc'],
             bg=CARD, fg=MUTED,
             font=('Malgun Gothic', 9),
             anchor='w', justify='left', wraplength=380).pack(fill=tk.X, pady=(5, 7))

    # 하단 버튼
    bot = tk.Frame(inner, bg=CARD)
    bot.pack(fill=tk.X)
    tk.Button(bot, text='기사 보기  ↗',
              bg=color, fg='#000', relief='flat',
              font=('Malgun Gothic', 9, 'bold'),
              cursor='hand2', padx=10, pady=3,
              activebackground=color,
              command=lambda: webbrowser.open(item['link'])
              ).pack(side=tk.RIGHT)

    # 호버 효과
    bg_widgets = [inner, top, title_lbl, bot]
    def on_enter(_):
        for w in bg_widgets:
            try: w.config(bg=HOVER)
            except Exception: pass
    def on_leave(_):
        for w in bg_widgets:
            try: w.config(bg=CARD)
            except Exception: pass

    for w in [outer, inner, top, title_lbl, bot]:
        w.bind('<Enter>', on_enter)
        w.bind('<Leave>', on_leave)
        w.bind('<MouseWheel>', scroll_cmd)

    return outer


# ══════════════════════════════════════════════════════════════════
class NewsApp(tk.Tk):
    COLS = 2

    def __init__(self):
        super().__init__()
        self.title('대한민국 정책브리핑 뉴스 리더')
        self.geometry('1160x780')
        self.minsize(900, 600)
        self.configure(bg=BG)

        # tkinter 콜백 예외도 로그에 기록
        self.report_callback_exception = self._on_tk_error

        try:
            self.state('zoomed')
        except Exception:
            pass

        self._all         : list = []
        self._shown       : list = []
        self._loading                = False
        self._current_cat            = '전체'
        self._search_after           = None
        self._render_pending         = False

        LOG.info('앱 초기화')
        self._build()
        self.after(300, self._fetch_all)

    def _on_tk_error(self, exc, val, tb):
        """tkinter 콜백 예외를 로그 파일에 기록"""
        msg = ''.join(traceback.format_exception(exc, val, tb))
        LOG.error('tkinter 콜백 오류:\n%s', msg)
        try:
            self._sv.set(f'  ❌ 오류 발생 (~/news_reader.log 확인)')
        except Exception:
            pass

    # ── UI 구성 ────────────────────────────────────────────────
    def _build(self):
        self._build_header()
        self._build_toolbar()
        self._build_filter()
        self._build_scroll_area()
        self._build_status()

    def _build_header(self):
        hf = tk.Frame(self, bg='#090d14', pady=16)
        hf.pack(fill=tk.X)
        tk.Label(hf, text='🇰🇷  대한민국 정책브리핑  뉴스 리더',
                 bg='#090d14', fg='#2f81f7',
                 font=('Malgun Gothic', 20, 'bold')).pack()
        tk.Label(hf, text='korea.kr 공식 RSS  |  정책뉴스 · 보도자료 · 오피니언 · 칼럼',
                 bg='#090d14', fg=DIM,
                 font=('Malgun Gothic', 10)).pack(pady=(3, 0))

    def _build_toolbar(self):
        tf = tk.Frame(self, bg=BG, pady=10)
        tf.pack(fill=tk.X, padx=20)

        sb = tk.Frame(tf, bg=SURFACE,
                      highlightthickness=1,
                      highlightbackground=BORDER,
                      highlightcolor=ACCENT)
        sb.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)

        tk.Label(sb, text=' 🔍 ', bg=SURFACE, fg=MUTED,
                 font=('', 11)).pack(side=tk.LEFT)

        self._sq = tk.StringVar()
        self._sq.trace_add('write', self._on_search)
        se = tk.Entry(sb, textvariable=self._sq,
                      bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                      relief='flat', font=('Malgun Gothic', 11), width=36)
        se.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
        se.bind('<FocusIn>',  lambda e: sb.config(highlightbackground=ACCENT))
        se.bind('<FocusOut>', lambda e: sb.config(highlightbackground=BORDER))

        tk.Button(sb, text='✕', bg=SURFACE, fg=MUTED, relief='flat',
                  font=('', 11), cursor='hand2',
                  activebackground=SURFACE, activeforeground=TEXT,
                  command=lambda: self._sq.set('')
                  ).pack(side=tk.RIGHT, padx=6)

        self._rbtn = tk.Button(tf, text='  🔄  새로고침  ',
                               bg=ACCENT, fg='#000', relief='flat',
                               font=('Malgun Gothic', 10, 'bold'),
                               cursor='hand2', padx=14, pady=10,
                               activebackground='#388bfd',
                               command=self._fetch_all)
        self._rbtn.pack(side=tk.RIGHT, padx=(12, 0))

    def _build_filter(self):
        self._ff = tk.Frame(self, bg=BG, pady=8)
        self._ff.pack(fill=tk.X, padx=20)

    def _refresh_filter(self):
        LOG.debug('_refresh_filter 시작')
        for w in self._ff.winfo_children():
            w.destroy()
        cats = ['전체'] + list(RSS_FEEDS.keys())
        for cat in cats:
            cnt = (len(self._all) if cat == '전체'
                   else sum(1 for n in self._all if n['category'] == cat))
            active = (cat == self._current_cat)
            color  = CAT_COLOR.get(cat, ACCENT)
            btn = tk.Button(
                self._ff,
                text=f'  {cat}  ({cnt})',
                bg=color if active else SURFACE,
                fg='#000' if active else MUTED,
                relief='flat',
                font=('Malgun Gothic', 10, 'bold' if active else 'normal'),
                cursor='hand2', padx=6, pady=6,
                activebackground=color, activeforeground='#000',
                command=lambda c=cat: self._set_cat(c))
            btn.pack(side=tk.LEFT, padx=4)
        LOG.debug('_refresh_filter 완료')

    def _set_cat(self, cat):
        self._current_cat = cat
        self._refresh_filter()
        self._render()

    def _build_scroll_area(self):
        cf = tk.Frame(self, bg=BG)
        cf.pack(fill=tk.BOTH, expand=True)

        self._loading_lbl = tk.Label(
            cf, text='⏳  RSS 피드에 연결 중…',
            bg=BG, fg=MUTED, font=('Malgun Gothic', 15))
        self._loading_lbl.place(relx=0.5, rely=0.45, anchor='center')

        self._canvas = tk.Canvas(cf, bg=BG, highlightthickness=0)
        self._vsb    = ttk.Scrollbar(cf, orient='vertical',
                                      command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._inner = tk.Frame(self._canvas, bg=BG)
        self._win   = self._canvas.create_window(
            (0, 0), window=self._inner, anchor='nw')

        self._inner.bind('<Configure>',
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox('all')))
        self._canvas.bind('<Configure>',
            lambda e: self._canvas.itemconfig(self._win, width=e.width))
        self._canvas.bind('<MouseWheel>', self._scroll)
        self._inner.bind('<MouseWheel>', self._scroll)

    def _scroll(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')

    def _build_status(self):
        sb = tk.Frame(self, bg='#090d14', pady=7)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        self._sv = tk.StringVar(value='  시작 중…')
        tk.Label(sb, textvariable=self._sv,
                 bg='#090d14', fg=MUTED,
                 font=('Malgun Gothic', 9), anchor='w').pack(side=tk.LEFT, padx=12)
        tk.Label(sb, text='출처: 대한민국 정책브리핑 korea.kr',
                 bg='#090d14', fg=DIM,
                 font=('Malgun Gothic', 9)).pack(side=tk.RIGHT, padx=12)

    # ── RSS 로드 ──────────────────────────────────────────────
    def _fetch_all(self):
        if self._loading:
            return
        LOG.info('_fetch_all 시작')
        self._loading = True
        self._rbtn.config(text='  ⏳  로딩 중…  ', state='disabled')
        self._loading_lbl.config(text='⏳  RSS 피드에 연결 중…')
        self._loading_lbl.place(relx=0.5, rely=0.45, anchor='center')
        self._vsb.pack_forget()
        self._canvas.pack_forget()
        self._sv.set('  연결 중…  (잠시만 기다려 주세요)')
        self.update_idletasks()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        LOG.info('_worker 스레드 시작')
        results, errors = [], []
        total = len(RSS_FEEDS)
        done  = [0]

        try:
            with ThreadPoolExecutor(max_workers=total) as pool:
                future_map = {
                    pool.submit(fetch_rss, url, label): label
                    for label, url in RSS_FEEDS.items()
                }
                for fut in as_completed(future_map):
                    label = future_map[fut]
                    done[0] += 1
                    try:
                        items = fut.result()
                        results.extend(items)
                        msg = (f'  로딩 중… ({done[0]}/{total})'
                               f'  {label} {len(items)}개 수신')
                        LOG.info(msg)
                    except Exception as ex:
                        errors.append(f'{label}: {ex}')
                        msg = f'  로딩 중… ({done[0]}/{total})  {label} 실패: {ex}'
                        LOG.warning(msg)
                    self.after(0, lambda m=msg: self._sv.set(m))

            results.sort(key=lambda x: x['raw_date'], reverse=True)
            LOG.info('_worker 완료: 총 %d개, 에러 %d건', len(results), len(errors))
        except Exception as ex:
            LOG.error('_worker 예외: %s\n%s', ex, traceback.format_exc())
            errors.append(str(ex))

        self.after(100, lambda: self._on_loaded(results, errors))

    def _on_loaded(self, items, errors):
        LOG.info('_on_loaded 호출: %d개', len(items))
        try:
            self._all     = items
            self._loading = False
            self._rbtn.config(text='  🔄  새로고침  ', state='normal')
            self._loading_lbl.place_forget()

            LOG.debug('_refresh_filter 호출')
            self._refresh_filter()

            LOG.debug('_render 호출')
            self._render()

            now = datetime.now().strftime('%H:%M:%S')
            warn = f'  |  ⚠ {len(errors)}건 실패' if errors else ''
            self._sv.set(f'  총 {len(items)}개 뉴스  |  {now}{warn}')
            LOG.info('_on_loaded 완료')
        except Exception as ex:
            LOG.error('_on_loaded 예외: %s\n%s', ex, traceback.format_exc())
            self._sv.set(f'  ❌ 오류: {ex}  (~/news_reader.log 확인)')

    # ── 렌더링 ────────────────────────────────────────────────
    def _on_search(self, *_):
        if self._search_after:
            self.after_cancel(self._search_after)
        self._search_after = self.after(300, self._render)

    def _render(self):
        LOG.debug('_render 시작')
        q   = self._sq.get().strip().lower()
        cat = self._current_cat

        self._shown = [
            n for n in self._all
            if (cat == '전체' or n['category'] == cat)
            and (not q or q in n['title'].lower() or q in n['desc'].lower())
        ]
        LOG.debug('_render 필터 결과: %d개', len(self._shown))

        # 기존 카드 제거
        for w in self._inner.winfo_children():
            w.destroy()

        if not self._shown:
            tk.Label(self._inner,
                     text='😕  검색 결과가 없습니다.',
                     bg=BG, fg=MUTED,
                     font=('Malgun Gothic', 14)
                     ).grid(row=0, column=0, columnspan=self.COLS, pady=80)
            self._show_canvas()
            return

        # 캔버스 먼저 표시 (카드가 들어올 공간 확보)
        self._show_canvas()
        self._sv.set(f'  카드 렌더링 중…  (0 / {len(self._shown)})')
        self.update_idletasks()

        # 배치 렌더링 시작
        self._render_batch(0)

    def _render_batch(self, start: int):
        """BATCH_SIZE 개씩 나눠서 렌더링 → UI 응답성 유지"""
        LOG.debug('_render_batch: start=%d', start)
        cols    = self.COLS
        try:
            card_w = max(340, (self.winfo_width() - 60) // cols - 20)
        except Exception:
            card_w = 340

        end = min(start + BATCH_SIZE, len(self._shown))
        for i in range(start, end):
            item = self._shown[i]
            row, col = divmod(i, cols)
            try:
                card = make_card(self._inner, item, self._scroll)
                card.grid(row=row, column=col,
                          padx=10, pady=8, sticky='nsew')
                self._inner.columnconfigure(col, weight=1)
            except Exception as ex:
                LOG.error('카드 생성 오류 [%d] %s: %s', i, item.get('title',''), ex)

        self._sv.set(f'  렌더링 중…  ({end} / {len(self._shown)})')

        if end < len(self._shown):
            # 다음 배치를 이벤트 루프에 양보한 뒤 처리
            self.after(20, lambda: self._render_batch(end))
        else:
            self._canvas.yview_moveto(0)
            q = self._sq.get().strip()
            label = f'  {len(self._shown)}개 표시'
            if q:
                label += f'  (검색: "{q}")'
            label += f'  |  전체 {len(self._all)}개'
            self._sv.set(label)
            LOG.info('_render_batch 완료: 총 %d개', len(self._shown))

    def _show_canvas(self):
        self._vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


# ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    LOG.info('===== 앱 시작 =====')
    try:
        app = NewsApp()
        app.mainloop()
    except Exception as ex:
        LOG.critical('앱 크래시: %s\n%s', ex, traceback.format_exc())
    LOG.info('===== 앱 종료 =====')
