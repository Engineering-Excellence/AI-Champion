# -*- coding: utf-8 -*-
"""
파일 관리자 (File Manager)
- 탐색기 스타일 두 패널 레이아웃
- 복사/잘라내기/붙여넣기/삭제/이름변경
- 새 폴더 생성, 파일 열기, 속성 보기
- 드라이브 선택, 주소 표시줄 직접 입력
- EXE 배포 가능 (PyInstaller)
"""
import ctypes
import os
import shutil
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, messagebox, simpledialog

# ─── 고해상도 DPI 지원 (Windows) ──────────────────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ─── 아이콘 문자 매핑 ─────────────────────────────────────────────
ICON = {
    'folder':   '📁',
    'drive':    '💾',
    'file':     '📄',
    'image':    '🖼',
    'video':    '🎬',
    'audio':    '🎵',
    'pdf':      '📕',
    'excel':    '📊',
    'word':     '📝',
    'ppt':      '📑',
    'zip':      '🗜',
    'code':     '💻',
    'exe':      '⚙',
    'txt':      '📃',
    'back':     '←',
    'forward':  '→',
    'up':       '↑',
    'home':     '🏠',
    'refresh':  '🔄',
    'newfolder':'📁+',
    'copy':     '⎘',
    'cut':      '✂',
    'paste':    '📋',
    'delete':   '🗑',
    'rename':   '✏',
    'search':   '🔍',
    'props':    'ℹ',
    'open':     '↗',
}
# ext → icon key 매핑
EXT_MAP = {}
for ext in ['.jpg','.jpeg','.png','.gif','.bmp','.webp','.ico','.svg']: EXT_MAP[ext]='image'
for ext in ['.mp4','.avi','.mkv','.mov','.wmv','.flv']:                  EXT_MAP[ext]='video'
for ext in ['.mp3','.wav','.flac','.aac','.ogg','.m4a']:                 EXT_MAP[ext]='audio'
for ext in ['.pdf']:                                                       EXT_MAP[ext]='pdf'
for ext in ['.xlsx','.xls','.csv','.ods']:                                EXT_MAP[ext]='excel'
for ext in ['.docx','.doc','.odt']:                                       EXT_MAP[ext]='word'
for ext in ['.pptx','.ppt','.odp']:                                       EXT_MAP[ext]='ppt'
for ext in ['.zip','.rar','.7z','.tar','.gz','.bz2']:                    EXT_MAP[ext]='zip'
for ext in ['.py','.js','.ts','.html','.css','.java','.cpp','.c','.cs',
            '.json','.xml','.yaml','.yml','.sh','.bat']:                  EXT_MAP[ext]='code'
for ext in ['.exe','.msi','.com']:                                        EXT_MAP[ext]='exe'
for ext in ['.txt','.log','.ini','.cfg','.md','.rst']:                   EXT_MAP[ext]='txt'


def get_file_icon(path: Path) -> str:
    if path.is_dir():
        return ICON['folder']
    ext = path.suffix.lower()
    return ICON.get(EXT_MAP.get(ext, 'file'), ICON['file'])


def fmt_size(nbytes: int) -> str:
    for unit in ('B','KB','MB','GB','TB'):
        if nbytes < 1024:
            return f'{nbytes:.1f} {unit}' if unit != 'B' else f'{nbytes} B'
        nbytes /= 1024
    return f'{nbytes:.1f} PB'


def fmt_date(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')


def get_drives() -> list:
    drives = []
    if sys.platform == 'win32':
        import string
        for d in string.ascii_uppercase:
            p = f'{d}:\\'
            if os.path.exists(p):
                drives.append(p)
    else:
        drives = ['/']
    return drives


# ══════════════════════════════════════════════════════════════════
class FileManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('파일 관리자')
        self.geometry('1200x700')
        self.minsize(800, 500)
        self._set_icon()

        # 상태 변수
        self.current_path   = Path.home()
        self.history        = [self.current_path]
        self.hist_idx       = 0
        self.clipboard      = []        # (mode, [Path, ...])  mode='copy'|'cut'
        self.clipboard_mode = None
        self.sort_col       = '이름'
        self.sort_rev       = False
        self.show_hidden    = tk.BooleanVar(value=False)

        self._build_ui()
        self._bind_keys()
        self.navigate(self.current_path, add_history=False)

    # ── 아이콘 (없으면 무시) ─────────────────────────────────────
    def _set_icon(self):
        try:
            # 스크립트와 같은 폴더에 icon.ico 있으면 사용
            ico = Path(sys.executable).parent / 'icon.ico'
            if not ico.exists():
                ico = Path(__file__).parent / 'icon.ico'
            if ico.exists():
                self.iconbitmap(str(ico))
        except Exception:
            pass

    # ── UI 빌드 ──────────────────────────────────────────────────
    def _build_ui(self):
        self._build_menu()
        self._build_toolbar()
        self._build_addr_bar()
        self._build_panes()
        self._build_status()

    # ── 메뉴바 ───────────────────────────────────────────────────
    def _build_menu(self):
        mbar = tk.Menu(self)
        self.config(menu=mbar)

        # 파일
        fm = tk.Menu(mbar, tearoff=False)
        fm.add_command(label='새 폴더 (Ctrl+Shift+N)', command=self.new_folder)
        fm.add_separator()
        fm.add_command(label='종료',    command=self.quit)
        mbar.add_cascade(label='파일', menu=fm)

        # 편집
        em = tk.Menu(mbar, tearoff=False)
        em.add_command(label='복사 (Ctrl+C)',          command=self.copy_items)
        em.add_command(label='잘라내기 (Ctrl+X)',      command=self.cut_items)
        em.add_command(label='붙여넣기 (Ctrl+V)',      command=self.paste_items)
        em.add_separator()
        em.add_command(label='삭제 (Delete)',           command=self.delete_items)
        em.add_command(label='이름 변경 (F2)',          command=self.rename_item)
        em.add_separator()
        em.add_command(label='모두 선택 (Ctrl+A)',      command=self.select_all)
        mbar.add_cascade(label='편집', menu=em)

        # 보기
        vm = tk.Menu(mbar, tearoff=False)
        vm.add_checkbutton(label='숨김 파일 표시', variable=self.show_hidden,
                           command=self.refresh)
        vm.add_separator()
        vm.add_command(label='새로 고침 (F5)', command=self.refresh)
        mbar.add_cascade(label='보기', menu=vm)

        # 도움말
        hm = tk.Menu(mbar, tearoff=False)
        hm.add_command(label='단축키 안내', command=self._show_shortcuts)
        hm.add_separator()
        hm.add_command(label='정보', command=self._show_about)
        mbar.add_cascade(label='도움말', menu=hm)

    # ── 툴바 ─────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = tk.Frame(self, bg='#2c2c2c', height=44)
        tb.pack(fill=tk.X)
        tb.pack_propagate(False)

        btn_style = {'bg':'#2c2c2c','fg':'#ffffff','relief':'flat',
                     'font':('Malgun Gothic',11),'padx':8,'pady':4,
                     'cursor':'hand2','activebackground':'#404040',
                     'activeforeground':'#ffffff','bd':0}

        self.btn_back    = tk.Button(tb, text=ICON['back'],    **btn_style, command=self.go_back)
        self.btn_forward = tk.Button(tb, text=ICON['forward'], **btn_style, command=self.go_forward)
        self.btn_up      = tk.Button(tb, text=ICON['up'],      **btn_style, command=self.go_up)
        self.btn_home    = tk.Button(tb, text=ICON['home'],    **btn_style, command=self.go_home)

        sep1 = tk.Frame(tb, bg='#555', width=1); sep1.pack(side=tk.LEFT, fill=tk.Y, pady=6)

        self.btn_back.pack(side=tk.LEFT, padx=2, pady=4)
        self.btn_forward.pack(side=tk.LEFT, padx=2, pady=4)
        self.btn_up.pack(side=tk.LEFT, padx=2, pady=4)
        self.btn_home.pack(side=tk.LEFT, padx=2, pady=4)

        sep1 = tk.Frame(tb, bg='#555', width=1)
        sep1.pack(side=tk.LEFT, fill=tk.Y, pady=6, padx=4)

        tk.Button(tb, text='📁+ 새 폴더', **btn_style, command=self.new_folder).pack(side=tk.LEFT, padx=2)

        sep2 = tk.Frame(tb, bg='#555', width=1)
        sep2.pack(side=tk.LEFT, fill=tk.Y, pady=6, padx=4)

        tk.Button(tb, text=ICON['copy']+'복사',     **btn_style, command=self.copy_items).pack(side=tk.LEFT)
        tk.Button(tb, text=ICON['cut']+'잘라내기',  **btn_style, command=self.cut_items).pack(side=tk.LEFT)
        tk.Button(tb, text=ICON['paste']+'붙여넣기',**btn_style, command=self.paste_items).pack(side=tk.LEFT)

        sep3 = tk.Frame(tb, bg='#555', width=1)
        sep3.pack(side=tk.LEFT, fill=tk.Y, pady=6, padx=4)

        tk.Button(tb, text=ICON['delete']+'삭제',  **btn_style, command=self.delete_items).pack(side=tk.LEFT)
        tk.Button(tb, text=ICON['rename']+'이름변경',**btn_style,command=self.rename_item).pack(side=tk.LEFT)

        sep4 = tk.Frame(tb, bg='#555', width=1)
        sep4.pack(side=tk.LEFT, fill=tk.Y, pady=6, padx=4)

        tk.Button(tb, text=ICON['refresh']+'새로고침',**btn_style,command=self.refresh).pack(side=tk.LEFT)

        # 검색 (오른쪽)
        tk.Label(tb, text=ICON['search'], bg='#2c2c2c', fg='#aaa',
                 font=('Malgun Gothic',11)).pack(side=tk.RIGHT, padx=(0,4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *a: self._do_search())
        se = tk.Entry(tb, textvariable=self.search_var, width=20,
                      bg='#404040', fg='#fff', insertbackground='#fff',
                      relief='flat', font=('Malgun Gothic',10))
        se.pack(side=tk.RIGHT, padx=4, pady=8, ipady=3)
        tk.Label(tb, text='검색:', bg='#2c2c2c', fg='#aaa',
                 font=('Malgun Gothic',10)).pack(side=tk.RIGHT)

    # ── 주소 표시줄 ──────────────────────────────────────────────
    def _build_addr_bar(self):
        af = tk.Frame(self, bg='#f0f0f0', height=32)
        af.pack(fill=tk.X)
        af.pack_propagate(False)

        tk.Label(af, text=' 주소:', bg='#f0f0f0', fg='#333',
                 font=('Malgun Gothic',10,'bold')).pack(side=tk.LEFT, padx=(8,2))

        self.addr_var = tk.StringVar()
        addr_entry = tk.Entry(af, textvariable=self.addr_var, relief='flat',
                              font=('Malgun Gothic',10), bg='#fff',
                              highlightthickness=1, highlightcolor='#0078d4',
                              highlightbackground='#ccc')
        addr_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=5)
        addr_entry.bind('<Return>', self._addr_enter)

        # 드라이브 선택
        drives = get_drives()
        self.drive_var = tk.StringVar(value=drives[0] if drives else '/')
        drv_cb = ttk.Combobox(af, textvariable=self.drive_var,
                              values=drives, width=5, state='readonly',
                              font=('Malgun Gothic',10))
        drv_cb.pack(side=tk.RIGHT, padx=(0,8), pady=5)
        drv_cb.bind('<<ComboboxSelected>>', self._drive_selected)
        tk.Label(af, text='드라이브:', bg='#f0f0f0', fg='#555',
                 font=('Malgun Gothic',9)).pack(side=tk.RIGHT)

    # ── 두 패널 (트리 + 파일 목록) ──────────────────────────────
    def _build_panes(self):
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                               sashrelief='flat', sashwidth=5,
                               bg='#ddd')
        paned.pack(fill=tk.BOTH, expand=True)

        # ── 왼쪽: 폴더 트리 ─────────────────────────────────
        left = tk.Frame(paned, bg='#fafafa')
        paned.add(left, width=240, minsize=150)

        tk.Label(left, text=' 📂 폴더', bg='#e8e8e8', fg='#333',
                 font=('Malgun Gothic',10,'bold'), anchor='w',
                 pady=5).pack(fill=tk.X)

        tree_frame = tk.Frame(left)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.folder_tree = ttk.Treeview(tree_frame, selectmode='browse',
                                         show='tree')
        vsb = ttk.Scrollbar(tree_frame, orient='vertical',
                             command=self.folder_tree.yview)
        self.folder_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        self.folder_tree.bind('<<TreeviewSelect>>', self._tree_select)
        self.folder_tree.bind('<Button-1>',         self._tree_click)

        self._build_tree()

        # ── 오른쪽: 파일 목록 ────────────────────────────────
        right = tk.Frame(paned)
        paned.add(right, minsize=400)

        cols = ('이름', '크기', '수정일', '유형')
        self.file_list = ttk.Treeview(right, columns=cols,
                                       show='headings',
                                       selectmode='extended')
        for col in cols:
            self.file_list.heading(col, text=col,
                command=lambda c=col: self._sort_by(c))
        self.file_list.column('이름', width=340, minwidth=200)
        self.file_list.column('크기', width=90,  anchor='e', minwidth=70)
        self.file_list.column('수정일', width=150, minwidth=120)
        self.file_list.column('유형', width=120,  minwidth=80)

        vsb2 = ttk.Scrollbar(right, orient='vertical',
                              command=self.file_list.yview)
        hsb2 = ttk.Scrollbar(right, orient='horizontal',
                              command=self.file_list.xview)
        self.file_list.configure(yscrollcommand=vsb2.set,
                                  xscrollcommand=hsb2.set)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)
        hsb2.pack(side=tk.BOTTOM, fill=tk.X)
        self.file_list.pack(fill=tk.BOTH, expand=True)

        self.file_list.bind('<Double-Button-1>',   self._open_item)
        self.file_list.bind('<Return>',            self._open_item)
        self.file_list.bind('<Button-3>',          self._context_menu)
        self.file_list.bind('<<TreeviewSelect>>', self._update_status)

        self._build_context_menu()

        # 스타일
        style = ttk.Style()
        style.configure('Treeview', font=('Malgun Gothic', 10), rowheight=24)
        style.configure('Treeview.Heading', font=('Malgun Gothic', 10, 'bold'))

    # ── 상태 표시줄 ──────────────────────────────────────────────
    def _build_status(self):
        sb = tk.Frame(self, bg='#e0e0e0', height=24)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        sb.pack_propagate(False)
        self.status_var = tk.StringVar(value='준비')
        tk.Label(sb, textvariable=self.status_var, bg='#e0e0e0',
                 fg='#333', font=('Malgun Gothic', 9),
                 anchor='w').pack(side=tk.LEFT, padx=8)

    # ── 폴더 트리 초기화 ─────────────────────────────────────────
    def _build_tree(self):
        self.folder_tree.delete(*self.folder_tree.get_children())
        root_id = self.folder_tree.insert('', 'end',
                                           text=f'{ICON["drive"]} 내 PC',
                                           open=True)
        for drv in get_drives():
            node = self.folder_tree.insert(root_id, 'end',
                                            text=f'{ICON["drive"]} {drv}',
                                            values=[drv], open=False)
            self.folder_tree.insert(node, 'end', text='...')  # 더미

        self.folder_tree.bind('<<TreeviewOpen>>', self._expand_tree)

    def _expand_tree(self, event):
        node = self.folder_tree.focus()
        vals = self.folder_tree.item(node, 'values')
        if not vals:
            return
        path = Path(vals[0])
        children = self.folder_tree.get_children(node)
        # 더미 제거
        if children and self.folder_tree.item(children[0], 'text') == '...':
            self.folder_tree.delete(*children)
            self._load_tree_node(node, path)

    def _load_tree_node(self, parent, path: Path):
        try:
            entries = sorted(
                [e for e in path.iterdir()
                 if e.is_dir() and (self.show_hidden.get() or not e.name.startswith('.'))],
                key=lambda x: x.name.lower()
            )
        except PermissionError:
            return
        for e in entries:
            child = self.folder_tree.insert(
                parent, 'end',
                text=f'{ICON["folder"]} {e.name}',
                values=[str(e)]
            )
            # 하위 폴더 있으면 더미 삽입
            try:
                if any(sub.is_dir() for sub in e.iterdir()):
                    self.folder_tree.insert(child, 'end', text='...')
            except PermissionError:
                pass

    def _tree_click(self, event):
        item = self.folder_tree.identify_row(event.y)
        if item:
            self.folder_tree.selection_set(item)

    def _tree_select(self, event):
        sel = self.folder_tree.selection()
        if not sel:
            return
        vals = self.folder_tree.item(sel[0], 'values')
        if vals:
            p = Path(vals[0])
            if p.is_dir():
                self.navigate(p)

    # ── 파일 목록 로드 ───────────────────────────────────────────
    def navigate(self, path: Path, add_history=True):
        try:
            path = path.resolve()
        except Exception:
            pass
        if not path.exists():
            messagebox.showerror('오류', f'경로를 찾을 수 없습니다:\n{path}')
            return

        self.current_path = path
        self.addr_var.set(str(path))

        if add_history:
            self.history = self.history[:self.hist_idx+1]
            self.history.append(path)
            self.hist_idx = len(self.history) - 1

        self._update_nav_btns()
        self._load_file_list()
        self.search_var.set('')

    def _load_file_list(self, filter_str=''):
        self.file_list.delete(*self.file_list.get_children())
        try:
            entries = list(self.current_path.iterdir())
        except PermissionError:
            self.status_var.set('❌ 접근 권한이 없습니다.')
            return

        show_h = self.show_hidden.get()
        dirs, files = [], []
        for e in entries:
            if not show_h and e.name.startswith('.'):
                continue
            if filter_str and filter_str.lower() not in e.name.lower():
                continue
            (dirs if e.is_dir() else files).append(e)

        key = lambda x: x.name.lower()
        if self.sort_col == '이름':
            dirs.sort(key=key, reverse=self.sort_rev)
            files.sort(key=key, reverse=self.sort_rev)
        elif self.sort_col == '크기':
            dirs.sort(key=key)
            files.sort(key=lambda x: x.stat().st_size if x.exists() else 0,
                       reverse=self.sort_rev)
        elif self.sort_col == '수정일':
            dirs.sort(key=lambda x: x.stat().st_mtime if x.exists() else 0,
                      reverse=self.sort_rev)
            files.sort(key=lambda x: x.stat().st_mtime if x.exists() else 0,
                       reverse=self.sort_rev)
        elif self.sort_col == '유형':
            dirs.sort(key=key)
            files.sort(key=lambda x: x.suffix.lower(), reverse=self.sort_rev)

        for e in dirs + files:
            try:
                st = e.stat()
                size_str = '' if e.is_dir() else fmt_size(st.st_size)
                date_str = fmt_date(st.st_mtime)
                type_str = '폴더' if e.is_dir() else (
                    f'{e.suffix.upper().lstrip(".")} 파일' if e.suffix else '파일')
                icon = get_file_icon(e)
                self.file_list.insert('', 'end', iid=str(e),
                    values=(f'{icon}  {e.name}', size_str, date_str, type_str))
            except (PermissionError, FileNotFoundError):
                pass

        total = len(dirs) + len(files)
        self.status_var.set(
            f'{total}개 항목  |  폴더 {len(dirs)}개, 파일 {len(files)}개'
            f'  |  {self.current_path}')

    # ── 파일 열기 ────────────────────────────────────────────────
    def _open_item(self, event=None):
        sel = self.file_list.selection()
        if not sel:
            return
        path = Path(sel[0])
        if path.is_dir():
            self.navigate(path)
        else:
            try:
                if sys.platform == 'win32':
                    os.startfile(str(path))
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', str(path)])
                else:
                    subprocess.Popen(['xdg-open', str(path)])
            except Exception as e:
                messagebox.showerror('열기 오류', str(e))

    # ── 컨텍스트 메뉴 ────────────────────────────────────────────
    def _build_context_menu(self):
        self.ctx = tk.Menu(self, tearoff=False)
        self.ctx.add_command(label=f'{ICON["open"]}  열기',          command=self._open_item)
        self.ctx.add_separator()
        self.ctx.add_command(label=f'{ICON["copy"]}  복사',           command=self.copy_items)
        self.ctx.add_command(label=f'{ICON["cut"]}  잘라내기',        command=self.cut_items)
        self.ctx.add_command(label=f'{ICON["paste"]}  붙여넣기',      command=self.paste_items)
        self.ctx.add_separator()
        self.ctx.add_command(label=f'{ICON["rename"]}  이름 변경',    command=self.rename_item)
        self.ctx.add_command(label=f'{ICON["delete"]}  삭제',         command=self.delete_items)
        self.ctx.add_separator()
        self.ctx.add_command(label='📁+  새 폴더',                   command=self.new_folder)
        self.ctx.add_separator()
        self.ctx.add_command(label=f'{ICON["props"]}  속성',          command=self.show_props)

    def _context_menu(self, event):
        item = self.file_list.identify_row(event.y)
        if item:
            if item not in self.file_list.selection():
                self.file_list.selection_set(item)
        try:
            self.ctx.tk_popup(event.x_root, event.y_root)
        finally:
            self.ctx.grab_release()

    # ── 파일 조작 ────────────────────────────────────────────────
    def _get_selected_paths(self) -> list:
        return [Path(s) for s in self.file_list.selection()]

    def copy_items(self):
        sel = self._get_selected_paths()
        if not sel:
            return
        self.clipboard = sel
        self.clipboard_mode = 'copy'
        self.status_var.set(f'복사 준비: {len(sel)}개 항목')

    def cut_items(self):
        sel = self._get_selected_paths()
        if not sel:
            return
        self.clipboard = sel
        self.clipboard_mode = 'cut'
        self.status_var.set(f'잘라내기 준비: {len(sel)}개 항목')

    def paste_items(self):
        if not self.clipboard:
            messagebox.showinfo('붙여넣기', '클립보드가 비어 있습니다.')
            return
        dest = self.current_path
        errors = []
        for src in self.clipboard:
            try:
                dst = dest / src.name
                if dst.exists():
                    base, ext = src.stem, src.suffix
                    i = 1
                    while dst.exists():
                        dst = dest / f'{base} ({i}){ext}'
                        i += 1
                if self.clipboard_mode == 'copy':
                    if src.is_dir():
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                else:  # cut
                    shutil.move(str(src), str(dst))
            except Exception as e:
                errors.append(f'{src.name}: {e}')
        if self.clipboard_mode == 'cut':
            self.clipboard = []
            self.clipboard_mode = None
        if errors:
            messagebox.showerror('오류', '\n'.join(errors))
        self.refresh()

    def delete_items(self):
        sel = self._get_selected_paths()
        if not sel:
            return
        names = '\n'.join(f'  • {p.name}' for p in sel[:10])
        if len(sel) > 10:
            names += f'\n  ... 외 {len(sel)-10}개'
        if not messagebox.askyesno('삭제 확인',
                f'다음 항목을 삭제하시겠습니까?\n\n{names}',
                icon='warning'):
            return
        errors = []
        for p in sel:
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
            except Exception as e:
                errors.append(f'{p.name}: {e}')
        if errors:
            messagebox.showerror('삭제 오류', '\n'.join(errors))
        self.refresh()

    def rename_item(self):
        sel = self._get_selected_paths()
        if not sel:
            return
        src = sel[0]
        new_name = simpledialog.askstring('이름 변경', '새 이름을 입력하세요:',
                                           initialvalue=src.name, parent=self)
        if not new_name or new_name == src.name:
            return
        dst = src.parent / new_name
        if dst.exists():
            messagebox.showerror('오류', f'"{new_name}" 이(가) 이미 존재합니다.')
            return
        try:
            src.rename(dst)
            self.refresh()
        except Exception as e:
            messagebox.showerror('이름 변경 오류', str(e))

    def new_folder(self):
        name = simpledialog.askstring('새 폴더', '폴더 이름을 입력하세요:',
                                       initialvalue='새 폴더', parent=self)
        if not name:
            return
        p = self.current_path / name
        if p.exists():
            messagebox.showerror('오류', f'"{name}" 이(가) 이미 존재합니다.')
            return
        try:
            p.mkdir(parents=True)
            self.refresh()
            # 새 폴더 선택
            self.after(100, lambda: self.file_list.selection_set(str(p)))
        except Exception as e:
            messagebox.showerror('폴더 생성 오류', str(e))

    def show_props(self):
        sel = self._get_selected_paths()
        if not sel:
            return
        p = sel[0]
        try:
            st = p.stat()
            if p.is_dir():
                # 폴더 크기 계산 (별도 스레드)
                info = (f'이름:     {p.name}\n'
                        f'종류:     폴더\n'
                        f'위치:     {p.parent}\n'
                        f'생성일:   {fmt_date(st.st_ctime)}\n'
                        f'수정일:   {fmt_date(st.st_mtime)}\n')
            else:
                info = (f'이름:     {p.name}\n'
                        f'종류:     {p.suffix.upper().lstrip(".")} 파일\n'
                        f'위치:     {p.parent}\n'
                        f'크기:     {fmt_size(st.st_size)}\n'
                        f'생성일:   {fmt_date(st.st_ctime)}\n'
                        f'수정일:   {fmt_date(st.st_mtime)}\n')
            messagebox.showinfo(f'속성: {p.name}', info)
        except Exception as e:
            messagebox.showerror('속성 오류', str(e))

    # ── 탐색 ─────────────────────────────────────────────────────
    def go_back(self):
        if self.hist_idx > 0:
            self.hist_idx -= 1
            self.navigate(self.history[self.hist_idx], add_history=False)

    def go_forward(self):
        if self.hist_idx < len(self.history) - 1:
            self.hist_idx += 1
            self.navigate(self.history[self.hist_idx], add_history=False)

    def go_up(self):
        parent = self.current_path.parent
        if parent != self.current_path:
            self.navigate(parent)

    def go_home(self):
        self.navigate(Path.home())

    def refresh(self):
        self._load_file_list(self.search_var.get())
        self._build_tree()

    def select_all(self):
        self.file_list.selection_set(self.file_list.get_children())

    def _update_nav_btns(self):
        self.btn_back.config(
            state=tk.NORMAL if self.hist_idx > 0 else tk.DISABLED)
        self.btn_forward.config(
            state=tk.NORMAL if self.hist_idx < len(self.history)-1 else tk.DISABLED)
        up = self.current_path.parent
        self.btn_up.config(
            state=tk.NORMAL if up != self.current_path else tk.DISABLED)

    def _addr_enter(self, event):
        p = Path(self.addr_var.get().strip())
        self.navigate(p)

    def _drive_selected(self, event):
        self.navigate(Path(self.drive_var.get()))

    def _update_status(self, event=None):
        sel = self._get_selected_paths()
        if not sel:
            self._load_file_list(self.search_var.get())
            return
        total_sz = sum(p.stat().st_size for p in sel if p.is_file())
        self.status_var.set(
            f'선택: {len(sel)}개  ({fmt_size(total_sz)})  |  {self.current_path}')

    def _sort_by(self, col):
        if self.sort_col == col:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col = col
            self.sort_rev = False
        self._load_file_list(self.search_var.get())

    def _do_search(self):
        self._load_file_list(self.search_var.get())

    # ── 키보드 단축키 ────────────────────────────────────────────
    def _bind_keys(self):
        self.bind('<Control-c>',         lambda e: self.copy_items())
        self.bind('<Control-x>',         lambda e: self.cut_items())
        self.bind('<Control-v>',         lambda e: self.paste_items())
        self.bind('<Delete>',            lambda e: self.delete_items())
        self.bind('<F2>',                lambda e: self.rename_item())
        self.bind('<F5>',                lambda e: self.refresh())
        self.bind('<Control-a>',         lambda e: self.select_all())
        self.bind('<Alt-Left>',          lambda e: self.go_back())
        self.bind('<Alt-Right>',         lambda e: self.go_forward())
        self.bind('<Alt-Up>',            lambda e: self.go_up())
        self.bind('<Control-Shift-N>',   lambda e: self.new_folder())
        self.bind('<BackSpace>',         lambda e: self.go_up())

    # ── 단축키 안내 ──────────────────────────────────────────────
    def _show_shortcuts(self):
        info = (
            '단축키 안내\n'
            '─────────────────────────────\n'
            'Ctrl+C      복사\n'
            'Ctrl+X      잘라내기\n'
            'Ctrl+V      붙여넣기\n'
            'Delete      삭제\n'
            'F2          이름 변경\n'
            'F5          새로 고침\n'
            'Ctrl+A      모두 선택\n'
            'Ctrl+Shift+N  새 폴더\n'
            'Alt+←       뒤로\n'
            'Alt+→       앞으로\n'
            'Alt+↑ / BackSpace  위로\n'
            'Enter / 더블클릭    열기\n'
        )
        messagebox.showinfo('단축키 안내', info)

    def _show_about(self):
        messagebox.showinfo('파일 관리자 정보',
            '파일 관리자 v1.0\n\n'
            '파이썬 tkinter 기반 독립 실행 파일 관리 도구\n'
            'Python 3.8+ | 외부 라이브러리 불필요\n\n'
            '기능: 탐색 · 복사 · 이동 · 삭제 · 이름변경 · 새폴더')


# ══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app = FileManager()
    app.mainloop()
