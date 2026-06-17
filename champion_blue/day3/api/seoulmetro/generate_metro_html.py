"""
서울 지하철 실시간 정보 HTML 생성기
SVG를 인라인 임베드하여 단일 HTML 파일을 생성합니다.

<prompt>
  <task>
    'champion_blue/api/seoul-metro-schematic.svg' 이 svg 위에 https://data.seoul.go.kr/dataList/OA-12601/A/1/datasetView.do 에서 제공하는 API를 이용하여 실시간 지도 위에 나타나는 단일 html 파일을 작성하라.
    API key는 내가 따로 입력할 것이다.
  <constraints>
    - 서버를 만들지 말 것.
  </constraints>
</prompt>
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(BASE_DIR, "seoul-metro-schematic.svg")
OUT_PATH = os.path.join(BASE_DIR, "seoul_metro_realtime.html")

with open(SVG_PATH, "r", encoding="utf-8") as f:
    svg_raw = f.read()

# SVG에 id 부여 및 스타일 보존
svg_content = svg_raw.replace("<svg ", '<svg id="metro-svg" ', 1)

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>서울 지하철 실시간 도착 정보</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Pretendard', 'Noto Sans KR', Arial, sans-serif;
      background: #111827;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }}

    /* ── 지도 영역 ── */
    #map-container {{
      position: fixed;
      inset: 0;
      overflow: hidden;
      cursor: grab;
      user-select: none;
    }}
    #map-container.dragging {{ cursor: grabbing; }}

    #svg-wrapper {{
      position: absolute;
      top: 0; left: 0;
      transform-origin: 0 0;
      will-change: transform;
    }}

    #metro-svg {{
      display: block;
      width: 3240px;
      height: 2626px;
    }}

    /* 선택된 역 강조 */
    .station-hotspot.selected {{
      fill-opacity: 0.7 !important;
      stroke-opacity: 1 !important;
      stroke: #facc15 !important;
    }}

    /* ── 사이드 패널 ── */
    #panel {{
      position: fixed;
      top: 0; right: 0;
      width: 340px;
      height: 100vh;
      background: rgba(17, 24, 39, 0.95);
      border-left: 1px solid #374151;
      display: flex;
      flex-direction: column;
      z-index: 100;
      backdrop-filter: blur(4px);
    }}

    #panel-header {{
      padding: 20px 20px 16px;
      border-bottom: 1px solid #374151;
    }}

    #panel-header h1 {{
      font-size: 16px;
      font-weight: 700;
      color: #f9fafb;
      margin-bottom: 14px;
      letter-spacing: -0.3px;
    }}

    .api-row {{
      display: flex;
      gap: 8px;
    }}

    #api-key-input {{
      flex: 1;
      background: #1f2937;
      border: 1px solid #374151;
      border-radius: 6px;
      padding: 8px 10px;
      color: #f9fafb;
      font-size: 13px;
      outline: none;
    }}
    #api-key-input:focus {{ border-color: #3b82f6; }}
    #api-key-input::placeholder {{ color: #6b7280; }}

    #save-btn {{
      background: #3b82f6;
      border: none;
      border-radius: 6px;
      color: #fff;
      font-size: 13px;
      font-weight: 600;
      padding: 8px 14px;
      cursor: pointer;
      white-space: nowrap;
    }}
    #save-btn:hover {{ background: #2563eb; }}
    #save-btn.saved {{ background: #10b981; }}

    /* ── 선택 역 정보 ── */
    #station-info {{
      padding: 16px 20px 12px;
      border-bottom: 1px solid #374151;
    }}

    #station-name-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 6px;
    }}

    #station-name {{
      font-size: 20px;
      font-weight: 700;
      color: #f9fafb;
    }}

    #line-badge {{
      display: inline-flex;
      align-items: center;
      padding: 3px 10px;
      border-radius: 100px;
      font-size: 12px;
      font-weight: 600;
      color: #fff;
    }}

    #station-hint {{
      font-size: 13px;
      color: #6b7280;
    }}

    /* ── 도착 목록 ── */
    #arrivals-area {{
      flex: 1;
      overflow-y: auto;
      padding: 12px 20px;
    }}
    #arrivals-area::-webkit-scrollbar {{ width: 4px; }}
    #arrivals-area::-webkit-scrollbar-track {{ background: transparent; }}
    #arrivals-area::-webkit-scrollbar-thumb {{ background: #374151; border-radius: 2px; }}

    .arrival-empty {{
      color: #6b7280;
      font-size: 14px;
      text-align: center;
      padding-top: 40px;
      line-height: 1.8;
    }}

    .direction-group {{
      margin-bottom: 18px;
    }}

    .direction-label {{
      font-size: 11px;
      font-weight: 700;
      color: #9ca3af;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}

    .arrival-card {{
      background: #1f2937;
      border-radius: 8px;
      padding: 12px 14px;
      margin-bottom: 8px;
      border-left: 4px solid transparent;
    }}

    .arrival-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 4px;
    }}

    .arrival-dest {{
      font-size: 14px;
      font-weight: 600;
      color: #f9fafb;
    }}

    .arrival-time {{
      font-size: 22px;
      font-weight: 700;
      text-align: right;
      line-height: 1;
    }}

    .arrival-time .unit {{
      font-size: 12px;
      font-weight: 400;
      color: #9ca3af;
    }}

    .arrival-msg {{
      font-size: 12px;
      color: #9ca3af;
      margin-top: 2px;
    }}

    .arvl-arriving {{ color: #ef4444 !important; }}
    .arvl-soon {{ color: #f59e0b !important; }}
    .arvl-coming {{ color: #60a5fa !important; }}

    .tag-express {{
      display: inline-block;
      background: #7c3aed;
      color: #fff;
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 4px;
      margin-left: 6px;
      vertical-align: middle;
    }}
    .tag-last {{
      display: inline-block;
      background: #dc2626;
      color: #fff;
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 4px;
      margin-left: 6px;
      vertical-align: middle;
    }}

    /* ── 하단 상태바 ── */
    #panel-footer {{
      padding: 10px 20px;
      border-top: 1px solid #374151;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    #status-msg {{
      font-size: 12px;
      color: #6b7280;
    }}
    #status-msg.error {{ color: #ef4444; }}

    #countdown-bar {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #6b7280;
    }}

    #countdown-ring {{
      width: 20px; height: 20px;
      transform: rotate(-90deg);
    }}
    #countdown-ring circle {{
      fill: none;
      stroke: #374151;
      stroke-width: 3;
    }}
    #countdown-ring .progress {{
      stroke: #3b82f6;
      stroke-linecap: round;
      transition: stroke-dashoffset 1s linear;
    }}

    /* ── 줌 버튼 ── */
    #zoom-controls {{
      position: fixed;
      bottom: 24px;
      left: 24px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      z-index: 100;
    }}

    .zoom-btn {{
      width: 36px;
      height: 36px;
      background: rgba(31, 41, 55, 0.9);
      border: 1px solid #374151;
      border-radius: 6px;
      color: #f9fafb;
      font-size: 18px;
      line-height: 1;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      backdrop-filter: blur(4px);
    }}
    .zoom-btn:hover {{ background: #374151; }}

    /* ── 호선 범례 ── */
    #legend {{
      position: fixed;
      bottom: 24px;
      left: 80px;
      display: flex;
      gap: 6px;
      z-index: 100;
    }}

    .legend-dot {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
      color: #fff;
      cursor: default;
      title: '';
    }}

    /* 로딩 스피너 */
    .spinner {{
      display: inline-block;
      width: 20px; height: 20px;
      border: 2px solid #374151;
      border-top-color: #3b82f6;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
      vertical-align: middle;
      margin-right: 8px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

    /* CORS 경고 */
    #cors-warning {{
      display: none;
      background: #1f2937;
      border: 1px solid #f59e0b;
      border-radius: 8px;
      padding: 12px;
      margin-top: 10px;
      font-size: 12px;
      color: #fbbf24;
      line-height: 1.6;
    }}
  </style>
</head>
<body>

<!-- 지도 -->
<div id="map-container">
  <div id="svg-wrapper">
    {svg_content}
  </div>
</div>

<!-- 줌 컨트롤 -->
<div id="zoom-controls">
  <button class="zoom-btn" id="btn-zoom-in" title="확대">＋</button>
  <button class="zoom-btn" id="btn-reset" title="초기화" style="font-size:12px;">↺</button>
  <button class="zoom-btn" id="btn-zoom-out" title="축소">－</button>
</div>

<!-- 호선 범례 -->
<div id="legend">
  <div class="legend-dot" style="background:#0052A4" title="1호선">1</div>
  <div class="legend-dot" style="background:#00A84D" title="2호선">2</div>
  <div class="legend-dot" style="background:#EF7C1C" title="3호선">3</div>
  <div class="legend-dot" style="background:#00A5DE" title="4호선">4</div>
  <div class="legend-dot" style="background:#996CAC" title="5호선">5</div>
  <div class="legend-dot" style="background:#CD7C2F" title="6호선">6</div>
  <div class="legend-dot" style="background:#747F00" title="7호선">7</div>
  <div class="legend-dot" style="background:#E6186C" title="8호선">8</div>
</div>

<!-- 사이드 패널 -->
<div id="panel">
  <div id="panel-header">
    <h1>🚇 서울 지하철 실시간</h1>
    <div class="api-row">
      <input id="api-key-input" type="password" placeholder="서울 열린데이터광장 API 키">
      <button id="save-btn">저장</button>
    </div>
    <div id="cors-warning">
      ⚠️ CORS 오류 발생 시: 브라우저 CORS 확장(Allow CORS)을 켜거나
      <code>chrome --disable-web-security</code>로 실행하세요.
    </div>
  </div>

  <div id="station-info">
    <div id="station-name-row">
      <span id="station-name" style="color:#6b7280;font-size:15px;">역을 클릭하세요</span>
    </div>
    <div id="station-hint" style="font-size:12px;color:#4b5563;">
      지도를 드래그하거나 휠로 확대·축소할 수 있습니다
    </div>
  </div>

  <div id="arrivals-area">
    <div class="arrival-empty">역을 클릭하면<br>실시간 도착 정보를 표시합니다</div>
  </div>

  <div id="panel-footer">
    <span id="status-msg"></span>
    <div id="countdown-bar" style="display:none">
      <svg id="countdown-ring" viewBox="0 0 20 20">
        <circle cx="10" cy="10" r="8"/>
        <circle class="progress" cx="10" cy="10" r="8"
          stroke-dasharray="50.27" stroke-dashoffset="0" id="ring-progress"/>
      </svg>
      <span id="countdown-text">30초</span>
    </div>
  </div>
</div>

<script>
// ────────────────────────────────────────────
// 상수
// ────────────────────────────────────────────
const LINE_COLORS = {{
  '1': '#0052A4', '2': '#00A84D', '3': '#EF7C1C',
  '4': '#00A5DE', '5': '#996CAC', '6': '#CD7C2F',
  '7': '#747F00', '8': '#E6186C'
}};

const REFRESH_SEC = 30;
const CIRCUMFERENCE = 2 * Math.PI * 8; // r=8

// ────────────────────────────────────────────
// 상태
// ────────────────────────────────────────────
const state = {{
  scale: 1,
  tx: 0,
  ty: 0,
  isDragging: false,
  dragStartX: 0,
  dragStartY: 0,
  prevTx: 0,
  prevTy: 0,
  selected: null,       // {{ name, line, code, el }}
  refreshTimer: null,
  countdownTimer: null,
  countdownVal: REFRESH_SEC,
  isLoading: false,
}};

// ────────────────────────────────────────────
// DOM refs
// ────────────────────────────────────────────
const mapContainer = document.getElementById('map-container');
const svgWrapper   = document.getElementById('svg-wrapper');
const apiInput     = document.getElementById('api-key-input');
const saveBtn      = document.getElementById('save-btn');
const stationName  = document.getElementById('station-name');
const stationHint  = document.getElementById('station-hint');
const nameRow      = document.getElementById('station-name-row');
const arrivalsArea = document.getElementById('arrivals-area');
const statusMsg    = document.getElementById('status-msg');
const countdownBar = document.getElementById('countdown-bar');
const countdownTxt = document.getElementById('countdown-text');
const ringProgress = document.getElementById('ring-progress');
const corsWarning  = document.getElementById('cors-warning');

// ────────────────────────────────────────────
// API 키 관리
// ────────────────────────────────────────────
function loadApiKey() {{
  const saved = localStorage.getItem('seoulMetroApiKey');
  if (saved) apiInput.value = saved;
}}

saveBtn.addEventListener('click', () => {{
  const key = apiInput.value.trim();
  if (!key) return;
  localStorage.setItem('seoulMetroApiKey', key);
  saveBtn.textContent = '✓ 저장됨';
  saveBtn.classList.add('saved');
  setTimeout(() => {{
    saveBtn.textContent = '저장';
    saveBtn.classList.remove('saved');
  }}, 2000);
}});

apiInput.addEventListener('keydown', (e) => {{
  if (e.key === 'Enter') saveBtn.click();
}});

// ────────────────────────────────────────────
// 줌 / 팬
// ────────────────────────────────────────────
function applyTransform() {{
  svgWrapper.style.transform = `translate(${{state.tx}}px, ${{state.ty}}px) scale(${{state.scale}})`;
}}

function zoomAt(cx, cy, factor) {{
  const newScale = Math.max(0.15, Math.min(6, state.scale * factor));
  const ratio = newScale / state.scale;
  state.tx = cx - ratio * (cx - state.tx);
  state.ty = cy - ratio * (cy - state.ty);
  state.scale = newScale;
  applyTransform();
}}

mapContainer.addEventListener('wheel', (e) => {{
  e.preventDefault();
  const rect = mapContainer.getBoundingClientRect();
  const cx = e.clientX - rect.left;
  const cy = e.clientY - rect.top;
  zoomAt(cx, cy, e.deltaY < 0 ? 1.12 : 1 / 1.12);
}}, {{ passive: false }});

// 드래그
let didDrag = false;

mapContainer.addEventListener('mousedown', (e) => {{
  if (e.button !== 0) return;
  state.isDragging = true;
  didDrag = false;
  state.dragStartX = e.clientX;
  state.dragStartY = e.clientY;
  state.prevTx = state.tx;
  state.prevTy = state.ty;
  mapContainer.classList.add('dragging');
}});

window.addEventListener('mousemove', (e) => {{
  if (!state.isDragging) return;
  const dx = e.clientX - state.dragStartX;
  const dy = e.clientY - state.dragStartY;
  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag = true;
  state.tx = state.prevTx + dx;
  state.ty = state.prevTy + dy;
  applyTransform();
}});

window.addEventListener('mouseup', () => {{
  state.isDragging = false;
  mapContainer.classList.remove('dragging');
}});

// 터치 지원
let lastTouchDist = null;
let touchMidX = 0, touchMidY = 0;

mapContainer.addEventListener('touchstart', (e) => {{
  if (e.touches.length === 2) {{
    const t0 = e.touches[0], t1 = e.touches[1];
    lastTouchDist = Math.hypot(t1.clientX - t0.clientX, t1.clientY - t0.clientY);
    touchMidX = (t0.clientX + t1.clientX) / 2;
    touchMidY = (t0.clientY + t1.clientY) / 2;
  }} else if (e.touches.length === 1) {{
    state.isDragging = true;
    didDrag = false;
    state.dragStartX = e.touches[0].clientX;
    state.dragStartY = e.touches[0].clientY;
    state.prevTx = state.tx;
    state.prevTy = state.ty;
  }}
}}, {{ passive: true }});

mapContainer.addEventListener('touchmove', (e) => {{
  e.preventDefault();
  if (e.touches.length === 2 && lastTouchDist) {{
    const t0 = e.touches[0], t1 = e.touches[1];
    const dist = Math.hypot(t1.clientX - t0.clientX, t1.clientY - t0.clientY);
    zoomAt(touchMidX, touchMidY, dist / lastTouchDist);
    lastTouchDist = dist;
  }} else if (e.touches.length === 1 && state.isDragging) {{
    const dx = e.touches[0].clientX - state.dragStartX;
    const dy = e.touches[0].clientY - state.dragStartY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag = true;
    state.tx = state.prevTx + dx;
    state.ty = state.prevTy + dy;
    applyTransform();
  }}
}}, {{ passive: false }});

mapContainer.addEventListener('touchend', () => {{
  state.isDragging = false;
  lastTouchDist = null;
}});

// 줌 버튼
document.getElementById('btn-zoom-in').addEventListener('click', () => {{
  const w = mapContainer.clientWidth, h = mapContainer.clientHeight;
  zoomAt(w / 2, h / 2, 1.3);
}});
document.getElementById('btn-zoom-out').addEventListener('click', () => {{
  const w = mapContainer.clientWidth, h = mapContainer.clientHeight;
  zoomAt(w / 2, h / 2, 1 / 1.3);
}});
document.getElementById('btn-reset').addEventListener('click', resetView);

function resetView() {{
  // 뷰포트 중앙에 서울 중심부가 오도록 초기 위치 설정
  const panelW = 340;
  const vw = window.innerWidth - panelW;
  const vh = window.innerHeight;
  const svgW = 3240, svgH = 2626;
  state.scale = Math.min(vw / svgW, vh / svgH) * 0.9;
  state.tx = (vw - svgW * state.scale) / 2;
  state.ty = (vh - svgH * state.scale) / 2;
  applyTransform();
}}

// ────────────────────────────────────────────
// 역 클릭 핸들러
// ────────────────────────────────────────────
function setupStationClicks() {{
  document.querySelectorAll('.station-hotspot').forEach(el => {{
    el.addEventListener('click', (e) => {{
      if (didDrag) return; // 드래그 후 클릭 무시
      e.stopPropagation();
      const station = e.currentTarget;
      selectStation(
        station.dataset.station,
        station.dataset.line,
        station.dataset.code,
        station
      );
    }});
  }});
}}

function selectStation(name, line, code, el) {{
  // 이전 선택 해제
  if (state.selected && state.selected.el) {{
    state.selected.el.classList.remove('selected');
  }}

  el.classList.add('selected');
  state.selected = {{ name, line, code, el }};

  // UI 업데이트
  const color = LINE_COLORS[line] || '#888';
  nameRow.innerHTML = `
    <span id="station-name" style="font-size:20px;font-weight:700;color:#f9fafb;">${{name}}</span>
    <span id="line-badge" style="background:${{color}};padding:3px 10px;border-radius:100px;font-size:12px;font-weight:600;color:#fff;">${{line}}호선</span>
  `;
  document.getElementById('station-hint').textContent = `역코드: ${{code}}`;

  // 자동 갱신 초기화
  clearTimers();
  fetchAndDisplay();
  startRefreshCycle();
}}

// ────────────────────────────────────────────
// API 호출
// ────────────────────────────────────────────
async function fetchArrivals(stationName) {{
  const key = localStorage.getItem('seoulMetroApiKey') || apiInput.value.trim();
  if (!key) throw new Error('API 키 없음');

  const url = `http://swopenAPI.seoul.go.kr/api/subway/${{key}}/json/realtimeStationArrival/0/5/${{encodeURIComponent(stationName)}}`;
  const res = await fetch(url, {{ mode: 'cors' }});
  if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
  const data = await res.json();

  const code = data.errorMessage?.code;
  if (code && code !== 'INFO-000') {{
    throw new Error(data.errorMessage.message || code);
  }}
  return data.realtimeArrivalList || [];
}}

async function fetchAndDisplay() {{
  if (!state.selected) return;
  if (state.isLoading) return;
  state.isLoading = true;

  arrivalsArea.innerHTML = '<div class="arrival-empty"><span class="spinner"></span>불러오는 중...</div>';
  setStatus('');

  try {{
    const list = await fetchArrivals(state.selected.name);
    corsWarning.style.display = 'none';
    renderArrivals(list);
    setStatus(`최종 수신: ${{new Date().toLocaleTimeString('ko-KR')}}`);
  }} catch (err) {{
    if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError') || err.message.includes('CORS')) {{
      corsWarning.style.display = 'block';
      setStatus('네트워크 오류 (CORS 확인 필요)', true);
    }} else if (err.message.includes('API 키 없음')) {{
      setStatus('API 키를 입력·저장하세요', true);
    }} else {{
      setStatus(`오류: ${{err.message}}`, true);
    }}
    arrivalsArea.innerHTML = `<div class="arrival-empty">데이터를 불러올 수 없습니다<br><small style="color:#4b5563;">${{err.message}}</small></div>`;
  }} finally {{
    state.isLoading = false;
  }}
}}

// ────────────────────────────────────────────
// 도착 정보 렌더링
// ────────────────────────────────────────────
function renderArrivals(list) {{
  if (!list || list.length === 0) {{
    arrivalsArea.innerHTML = '<div class="arrival-empty">현재 운행 정보가 없습니다<br><small style="color:#4b5563;">(심야 또는 운행 종료 시간대)</small></div>';
    return;
  }}

  // 상행/하행 분리
  const groups = {{}};
  list.forEach(item => {{
    const dir = getDirectionLabel(item);
    if (!groups[dir]) groups[dir] = [];
    groups[dir].push(item);
  }});

  const color = LINE_COLORS[state.selected.line] || '#888';
  let html = '';

  Object.entries(groups).forEach(([dir, items]) => {{
    html += `<div class="direction-group">`;
    html += `<div class="direction-label">${{dir}}</div>`;
    items.forEach(item => {{
      html += renderCard(item, color);
    }});
    html += `</div>`;
  }});

  arrivalsArea.innerHTML = html;
}}

function renderCard(item, color) {{
  const secs = parseInt(item.barvlDt) || 0;
  const mins = Math.floor(secs / 60);
  const remSecs = secs % 60;

  let timeHTML = '';
  let timeClass = '';

  if (item.arvlCd === '0' || item.arvlCd === '1') {{
    // 진입/도착
    timeHTML = `<span class="arrival-time arvl-arriving">도착</span>`;
    timeClass = 'arvl-arriving';
  }} else if (secs <= 60) {{
    timeHTML = `<span class="arrival-time arvl-soon">${{secs}}<span class="unit">초</span></span>`;
    timeClass = 'arvl-soon';
  }} else {{
    timeHTML = `<span class="arrival-time arvl-coming">${{mins}}<span class="unit">분</span> ${{remSecs > 0 ? remSecs + '<span class="unit">초</span>' : ''}}</span>`;
    timeClass = 'arvl-coming';
  }}

  const dest = item.trainLineNm || item.statnTnm || '';
  const msg  = item.arvlMsg2 || '';
  const isExpress = item.directAt === '1';
  const isLast    = item.lstcarAt === '1';

  return `
    <div class="arrival-card" style="border-left-color:${{color}}">
      <div class="arrival-top">
        <div>
          <span class="arrival-dest">${{dest}}</span>
          ${{isExpress ? '<span class="tag-express">급행</span>' : ''}}
          ${{isLast    ? '<span class="tag-last">막차</span>'    : ''}}
        </div>
        ${{timeHTML}}
      </div>
      <div class="arrival-msg">${{msg}}</div>
    </div>
  `;
}}

function getDirectionLabel(item) {{
  // updnLine: 0=상행/외선, 1=하행/내선, 2=외선, 3=내선
  const updnLine = item.updnLine;
  const line = state.selected?.line;
  if (line === '2' || line === '6') {{
    return updnLine === '0' || updnLine === '2' ? '↻ 외선 (시계방향)' : '↺ 내선 (반시계방향)';
  }}
  return updnLine === '0' ? '↑ 상행' : '↓ 하행';
}}

// ────────────────────────────────────────────
// 자동 갱신 (30초)
// ────────────────────────────────────────────
function startRefreshCycle() {{
  state.countdownVal = REFRESH_SEC;
  updateCountdown();
  countdownBar.style.display = 'flex';

  state.countdownTimer = setInterval(() => {{
    state.countdownVal--;
    if (state.countdownVal <= 0) {{
      state.countdownVal = REFRESH_SEC;
      fetchAndDisplay();
    }}
    updateCountdown();
  }}, 1000);
}}

function updateCountdown() {{
  const v = state.countdownVal;
  countdownTxt.textContent = v < 60 ? `${{v}}초` : `${{Math.floor(v/60)}}분`;
  const offset = CIRCUMFERENCE * (1 - v / REFRESH_SEC);
  ringProgress.style.strokeDashoffset = offset;
}}

function clearTimers() {{
  clearInterval(state.refreshTimer);
  clearInterval(state.countdownTimer);
  state.refreshTimer = null;
  state.countdownTimer = null;
  countdownBar.style.display = 'none';
}}

// ────────────────────────────────────────────
// 상태 메시지
// ────────────────────────────────────────────
function setStatus(msg, isError = false) {{
  statusMsg.textContent = msg;
  statusMsg.className = isError ? 'error' : '';
}}

// ────────────────────────────────────────────
// 초기화
// ────────────────────────────────────────────
function init() {{
  loadApiKey();
  setupStationClicks();
  resetView();
}}

init();
</script>
</body>
</html>"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"생성 완료: {OUT_PATH}")
print(f"파일 크기: {os.path.getsize(OUT_PATH) / 1024 / 1024:.1f} MB")
