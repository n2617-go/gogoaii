import streamlit as st
import streamlit.components.v1 as components
import requests
import yfinance as yf
from datetime import datetime
import time
import json
import urllib.parse

st.set_page_config(
    page_title="台股看盤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════
CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0d14 !important;
    color: #e2e8f0 !important;
    font-family: 'Noto Sans TC', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0f1a2e 0%, #0a0d14 60%) !important;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stAppViewBlockContainer"] {
    padding: 1rem 0.75rem 5rem !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

.app-header {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.1rem;
}
.app-title { font-size: 1.35rem; font-weight: 900; letter-spacing: -0.02em; color: #f8fafc; }
.app-title span { color: #38bdf8; }
.app-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: #64748b;
    text-align: right; line-height: 1.6;
}
.live-dot {
    display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; background: #22c55e; margin-right: 5px;
    animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.4; transform:scale(.8); }
}

/* 書籤提示橫幅 */
.bookmark-hint {
    background: linear-gradient(135deg, rgba(56,189,248,0.08), rgba(56,189,248,0.04));
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 12px;
    padding: 0.65rem 0.9rem;
    margin-bottom: 1rem;
    font-size: 0.72rem;
    color: #94a3b8;
    line-height: 1.6;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
}
.bookmark-hint-icon { font-size: 0.9rem; flex-shrink: 0; margin-top: 1px; }
.bookmark-hint strong { color: #38bdf8; }

.add-section-title {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #38bdf8; margin-bottom: 0.7rem;
}

[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 0.75rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(56,189,248,0.5) !important;
    box-shadow: 0 0 0 2px rgba(56,189,248,0.1) !important;
}
[data-testid="stTextInput"] label { display: none !important; }

[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0ea5e9, #38bdf8) !important;
    color: #0a0d14 !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.2rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

.stock-card {
    background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.1rem 1.1rem 0.9rem;
    margin-bottom: 0.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.stock-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent, #38bdf8);
    border-radius: 16px 16px 0 0;
}
.stock-card.up   { --accent: #ef4444; }
.stock-card.down { --accent: #22c55e; }
.stock-card.flat { --accent: #94a3b8; }

.card-top {
    display: flex; align-items: flex-start;
    justify-content: space-between; margin-bottom: 0.85rem;
}
.stock-name { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; line-height: 1.3; }
.stock-code { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; margin-top: 2px; }
.price-block { text-align: right; }
.price-main {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem; font-weight: 700; line-height: 1; color: #f8fafc;
}
.price-change {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; font-weight: 700; margin-top: 3px;
}
.up-color   { color: #ef4444; }
.down-color { color: #22c55e; }
.flat-color { color: #94a3b8; }

.ohlc-row {
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 0.3rem; background: rgba(255,255,255,0.03);
    border-radius: 10px; padding: 0.55rem 0.5rem; margin-bottom: 0.85rem;
}
.ohlc-item { text-align: center; }
.ohlc-label {
    font-size: 0.6rem; color: #475569;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 3px;
}
.ohlc-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; color: #cbd5e1; font-weight: 500;
}

.card-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 0.75rem 0; }

.tech-section-title {
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #475569; margin-bottom: 0.6rem;
}
.kd-row { display: flex; gap: 0.5rem; margin-bottom: 0.65rem; }
.kd-chip {
    flex: 1; background: rgba(255,255,255,0.04);
    border-radius: 8px; padding: 0.45rem 0.6rem; text-align: center;
}
.kd-chip-label { font-size: 0.6rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.kd-chip-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-top: 1px;
}
.kd-bar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 99px; height: 4px; margin-top: 5px; overflow: hidden;
}
.kd-bar-fill {
    height: 100%; border-radius: 99px;
    background: var(--bar-color, #38bdf8);
    width: var(--bar-width, 50%);
}
.momentum-row {
    display: flex; align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.03);
    border-radius: 8px; padding: 0.4rem 0.65rem; margin-bottom: 0.65rem;
}
.momentum-label { font-size: 0.7rem; color: #64748b; }
.momentum-val { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; }

.signal-row { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; font-weight: 700;
    border-radius: 99px; padding: 0.3rem 0.75rem;
}
.badge-signal-buy   { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.badge-signal-sell  { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.badge-signal-watch { background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }
.badge-trend-up     { background: rgba(251,146,60,0.12); color: #fb923c; border: 1px solid rgba(251,146,60,0.25); }
.badge-trend-down   { background: rgba(96,165,250,0.12); color: #60a5fa; border: 1px solid rgba(96,165,250,0.25); }

/* 市場掃描區塊 */
.scan-section {
    background: linear-gradient(135deg, rgba(56,189,248,0.06), rgba(139,92,246,0.06));
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 16px;
    padding: 1.1rem;
    margin-bottom: 1.2rem;
}
.scan-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.9rem;
}
.scan-title {
    font-size: 0.88rem; font-weight: 900; color: #f1f5f9; letter-spacing: -0.01em;
}
.scan-title span { color: #38bdf8; }
.scan-subtitle { font-size: 0.65rem; color: #64748b; margin-top: 2px; }
.scan-badge {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.06em;
    background: linear-gradient(135deg,rgba(56,189,248,.15),rgba(139,92,246,.15));
    border: 1px solid rgba(56,189,248,.3); color: #38bdf8;
    border-radius: 99px; padding: 0.2rem 0.6rem;
}
.rec-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 0.75rem 0.85rem;
    margin-bottom: 0.5rem; position: relative; overflow: hidden;
}
.rec-card::before {
    content:''; position:absolute; top:0; left:0; bottom:0; width:3px;
    background: var(--rc, #38bdf8); border-radius: 12px 0 0 12px;
}
.rec-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.5rem; }
.rec-name { font-size: 0.88rem; font-weight: 700; color: #f1f5f9; }
.rec-code { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#64748b; margin-top:1px; }
.rec-score-wrap { text-align:right; }
.rec-score {
    font-family:'JetBrains Mono',monospace;
    font-size: 1.15rem; font-weight: 700; color: #38bdf8; line-height:1;
}
.rec-score-label { font-size:0.58rem; color:#475569; letter-spacing:.05em; }
.rec-indicators {
    display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.5rem;
}
.rec-ind {
    font-family:'JetBrains Mono',monospace; font-size:0.65rem;
    background: rgba(255,255,255,0.05); border-radius:6px;
    padding: 0.2rem 0.45rem; color:#94a3b8;
}
.rec-reasons { display:flex; gap:0.35rem; flex-wrap:wrap; }
.rec-reason {
    font-size:0.65rem; font-weight:700;
    background:rgba(34,197,94,0.1); color:#4ade80;
    border:1px solid rgba(34,197,94,0.2);
    border-radius:99px; padding:0.15rem 0.55rem;
}
.score-bar-wrap {
    background:rgba(255,255,255,0.06); border-radius:99px; height:3px; margin-top:4px; overflow:hidden;
}
.score-bar-fill {
    height:100%; border-radius:99px;
    background: linear-gradient(90deg,#38bdf8,#818cf8);
    width:var(--sw,50%);
}
.scan-progress-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: #64748b; text-align: center;
    margin-top: 0.3rem; letter-spacing: 0.02em;
}

/* 掃描全覽瀏覽器 */
.scan-toolbar {
    display: flex; gap: 0.4rem; align-items: center;
    margin-bottom: 0.75rem; flex-wrap: wrap;
}
.scan-search-wrap {
    flex: 1; min-width: 0;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 0.35rem 0.6rem;
    display: flex; align-items: center; gap: 0.4rem;
}
.scan-search-icon { font-size: 0.75rem; color: #475569; flex-shrink:0; }
.sort-tabs {
    display: flex; gap: 0.25rem; margin-bottom: 0.65rem;
}
.sort-tab {
    font-size: 0.65rem; font-weight: 700;
    border-radius: 8px; padding: 0.28rem 0.6rem;
    background: rgba(255,255,255,0.05);
    color: #64748b; cursor: pointer; border: 1px solid transparent;
    white-space: nowrap;
}
.sort-tab.active {
    background: rgba(56,189,248,0.15);
    color: #38bdf8; border-color: rgba(56,189,248,0.3);
}
.scan-stats {
    font-size: 0.65rem; color: #475569;
    margin-bottom: 0.6rem; display: flex; justify-content: space-between;
}
.scan-row {
    display: flex; align-items: center;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 0.55rem 0.65rem;
    margin-bottom: 0.35rem; gap: 0.5rem;
    position: relative; overflow: hidden;
}
.scan-row::before {
    content:''; position:absolute; top:0; left:0; bottom:0; width:2px;
    background: var(--sr, #334155);
}
.scan-row-rank {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: #475569;
    width: 1.8rem; text-align: right; flex-shrink: 0;
}
.scan-row-info { flex: 1; min-width: 0; }
.scan-row-name {
    font-size: 0.82rem; font-weight: 700; color: #f1f5f9;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.scan-row-code { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #64748b; }
.scan-row-right { text-align: right; flex-shrink: 0; }
.scan-row-score {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; font-weight: 700; line-height: 1.1;
}
.scan-row-pct { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; }
.scan-row-signals { display: flex; gap: 0.25rem; flex-wrap: wrap; margin-top: 0.3rem; }
.scan-sig-chip {
    font-size: 0.58rem; font-weight: 700;
    background: rgba(34,197,94,0.1); color: #4ade80;
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 99px; padding: 0.1rem 0.4rem;
}
.scan-sig-chip.neutral {
    background: rgba(148,163,184,0.08); color: #64748b;
    border-color: rgba(148,163,184,0.15);
}
.page-nav {
    display: flex; align-items: center; justify-content: center;
    gap: 0.5rem; margin-top: 0.7rem;
}
.page-info {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: #64748b;
}
.rank-medal { font-size:0.9rem; margin-right:0.3rem; }
.no-data { font-size: 0.75rem; color: #475569; text-align: center; padding: 0.5rem; font-style: italic; }
.error-msg {
    font-size: 0.75rem; color: #f87171;
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.5rem;
}
.success-msg {
    font-size: 0.75rem; color: #4ade80;
    background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2);
    border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.5rem;
}
.card-gap { margin-bottom: 0.9rem; }
.footer-note { text-align: center; font-size: 0.65rem; color: #334155; margin-top: 1.5rem; line-height: 1.7; }
.element-container { margin-bottom: 0 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 持久化核心：query_params  ← Streamlit 原生，100% 可靠
#
# 原理：把 watchlist 編碼成 JSON 存在 URL 的 ?wl=... 參數。
# Streamlit 每次 rerun 都能直接讀到，不依賴 JS 時序。
# 使用者只需把含參數的網址加入書籤，下次直接開書籤即還原。
# ══════════════════════════════════════════════════════════
QP_KEY = "wl"

DEFAULT_STOCKS = [
    {"id": "2330", "name": "台積電"},
    {"id": "2002", "name": "中鋼"},
    {"id": "1326", "name": "台化"},
    {"id": "6505", "name": "台塑化"},
]


def load_watchlist() -> list:
    """從 query_params 讀取 watchlist，讀不到則回傳預設值"""
    try:
        raw = st.query_params.get(QP_KEY, "")
        if raw:
            data = json.loads(raw)
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception:
        pass
    return DEFAULT_STOCKS.copy()


def save_watchlist(watchlist: list):
    """將 watchlist 寫入 query_params（同步更新網址）"""
    st.query_params[QP_KEY] = json.dumps(watchlist, ensure_ascii=False)


# ══════════════════════════════════════════════════════════
# JS：自動把目前網址（含 ?wl=...）存入 localStorage，
# 下次使用者直接開網址列時自動補回參數（輔助層）
# ══════════════════════════════════════════════════════════
def inject_localstorage_helper():
    components.html("""
    <script>
    (function(){
        var LS_KEY = 'twstock_url_v3';
        try {
            // 如果目前網址有 wl 參數，就存起來
            if (window.parent.location.search.indexOf('wl=') !== -1) {
                localStorage.setItem(LS_KEY, window.parent.location.href);
            } else {
                // 沒有參數時，嘗試從 localStorage 還原
                var saved = localStorage.getItem(LS_KEY);
                if (saved) {
                    var savedUrl = new URL(saved);
                    var wl = savedUrl.searchParams.get('wl');
                    if (wl) {
                        var cur = new URL(window.parent.location.href);
                        cur.searchParams.set('wl', wl);
                        window.parent.history.replaceState({}, '', cur.toString());
                        // 重新載入讓 Streamlit 讀到新的 query_params
                        window.parent.location.reload();
                    }
                }
            }
        } catch(e) {}
    })();
    </script>
    """, height=0)


# ══════════════════════════════════════════════════════════
# 股票名稱查詢
# ══════════════════════════════════════════════════════════
import re as _re

# ── 內建常用台股中文名稱對照表（離線備援）──────────────────
_BUILTIN_NAME_MAP = {
    # 上市權值股
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2382": "廣達",
    "2308": "台達電", "2881": "富邦金", "2882": "國泰金", "2891": "中信金",
    "2886": "兆豐金", "2884": "玉山金", "2892": "第一金", "2880": "華南金",
    "2885": "元大金", "2887": "台新金", "2883": "開發金", "2890": "永豐金",
    "2888": "新光金", "5880": "合庫金", "2302": "聯電", "2303": "聯電",
    "2357": "華碩", "2379": "瑞昱", "2395": "研華", "2412": "中華電",
    "2002": "中鋼",  "1301": "台塑",  "1303": "南亞",  "1326": "台化",
    "6505": "台塑化","2207": "和泰車","2474": "可成",  "3711": "日月光投控",
    "2408": "南亞科","2337": "旺宏",  "3034": "聯詠",  "3008": "大立光",
    "2353": "宏碁",  "2356": "英業達","2376": "技嘉",  "2385": "群光",
    "2392": "正崴",  "2404": "漢唐",  "2441": "超豐",  "2449": "京元電子",
    "2605": "新興",  "1216": "統一",  "1101": "台泥",  "1102": "亞泥",
    "1402": "遠紡",  "2609": "陽明",  "2615": "萬海",  "2603": "長榮",
    "2610": "華航",  "2618": "長榮航","2912": "統一超","2801": "彰銀",
    "1590": "亞德客","6669": "緯穎",  "6770": "力積電","4938": "和碩",
    "3045": "台灣大","4904": "遠傳",  "2498": "宏達電","2344": "華邦電",
    "2327": "國巨",  "2360": "致茂",  "3037": "欣興",  "3044": "健鼎",
    "6415": "矽力-KY","4919": "新唐", "2059": "川湖",  "5269": "祥碩",
    # ETF
    "0050": "元大台灣50",  "0056": "元大高股息",
    "00878": "國泰永續高股息", "00881": "國泰台灣5G+",
    "00919": "群益台灣精選高息", "00929": "復華台灣科技優息",
    "006208": "富邦台50",  "00646": "元大S&P500",
    "00692": "富邦公司治理", "00696B": "富邦美債7-10",
    "00940": "元大台灣價值高息",
}

@st.cache_data(ttl=3600)
def fetch_name_map() -> dict:
    """
    從 TWSE / OTC ISIN 頁面抓完整代碼→中文名稱對照表。
    涵蓋上市(mode=2)、上櫃(mode=4)、全數字與含字母代碼（如 00981A）。
    """
    result = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    for mode in ["2", "4"]:
        try:
            r = requests.get(
                f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}",
                headers=headers, timeout=12
            )
            r.encoding = "big5"
            # 逐列解析：每個 <td> 的第一格格式為「代碼　名稱」（全形空格分隔）
            rows = _re.findall(r'<tr[^>]*>(.*?)</tr>', r.text, _re.S)
            for row in rows:
                tds = _re.findall(r'<td[^>]*>(.*?)</td>', row, _re.S)
                if not tds:
                    continue
                # 去除 HTML 標籤
                cell = _re.sub(r'<[^>]+>', '', tds[0]).strip()
                # 支援全形空格 \u3000 與一般空白兩種分隔
                if '\u3000' in cell:
                    parts = cell.split('\u3000', 1)
                else:
                    parts = cell.split(None, 1)   # 以任意空白切一次
                if len(parts) == 2:
                    code = parts[0].strip()
                    name = parts[1].strip()
                    # 代碼：4~7 碼，可包含英文字母（如 00631L、00981A）
                    if code and name and _re.match(r'^[0-9A-Za-z]{4,7}$', code):
                        result[code] = name
        except Exception:
            pass
    # 合併內建對照表（內建優先補齊，不覆蓋從網路查到的結果）
    for k, v in _BUILTIN_NAME_MAP.items():
        if k not in result:
            result[k] = v
    return result


@st.cache_data(ttl=300)
def fetch_name_from_twse_api(stock_id: str) -> str:
    """
    用 TWSE 即時 API 查單支股票名稱（上市 + 上櫃）。
    非交易時間仍可查到靜態名稱欄位 'n'。
    快取 5 分鐘。
    """
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    for market in ["tse", "otc"]:
        try:
            url = (
                "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
                f"?ex_ch={market}_{stock_id}.tw&json=1"
            )
            r = requests.get(url, headers=headers, timeout=8)
            arr = r.json().get("msgArray", [])
            if arr and arr[0].get("n"):
                return arr[0]["n"]
        except Exception:
            pass
    return ""


def get_stock_name(stock_id: str) -> str:
    """
    取得中文名稱，三層備援：
    1. TWSE/OTC 即時 API（最快，非交易時間也有靜態欄位）
    2. ISIN 名稱對照表（最全，含所有 ETF 含字母代碼）
    3. 代碼本身（最後備援）
    """
    # 層 1：即時 API
    name = fetch_name_from_twse_api(stock_id)
    if name:
        return name
    # 層 2：ISIN 對照表
    name_map = fetch_name_map()
    if stock_id in name_map:
        return name_map[stock_id]
    # 層 2b：大小寫不敏感比對（部分 ETF 代碼大小寫不一致）
    sid_upper = stock_id.upper()
    for k, v in name_map.items():
        if k.upper() == sid_upper:
            return v
    return stock_id   # 最後備援


def verify_stock(stock_id: str):
    """
    驗證台股代碼，回傳 (有效: bool, 中文名稱: str)。
    策略：先用即時 API 驗存在性；若非交易時間則改查 ISIN 表；
    最後用 yfinance 確認歷史資料存在。
    """
    # 層 1：TWSE/OTC 即時 API
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    for market in ["tse", "otc"]:
        try:
            url = (
                "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
                f"?ex_ch={market}_{stock_id}.tw&json=1"
            )
            r = requests.get(url, headers=headers, timeout=8)
            arr = r.json().get("msgArray", [])
            if arr and arr[0].get("n"):
                return True, arr[0]["n"]
        except Exception:
            pass

    # 層 2：ISIN 對照表（含字母代碼、非交易時間皆可查）
    name_map = fetch_name_map()
    sid_upper = stock_id.upper()
    for k, v in name_map.items():
        if k.upper() == sid_upper:
            return True, v

    # 層 3：yfinance 確認存在（先查 info 取名稱，再查內建表）
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{stock_id}{suffix}")
            df = ticker.history(period="5d")
            if not df.empty:
                info = {}
                try:
                    info = ticker.info or {}
                except Exception:
                    pass
                yf_name = info.get("longName") or info.get("shortName") or ""
                # 優先序：yfinance info > 內建表 > ISIN表 > 代碼本身
                name = (yf_name
                        or _BUILTIN_NAME_MAP.get(stock_id)
                        or name_map.get(stock_id)
                        or stock_id)
                return True, name
        except Exception:
            pass

    return False, ""


# ══════════════════════════════════════════════════════════
# 股價資料
# ══════════════════════════════════════════════════════════
def fetch_twse_realtime(stock_ids: list) -> list:
    tse = [f"tse_{sid}.tw" for sid in stock_ids]
    otc = [f"otc_{sid}.tw" for sid in stock_ids]
    ex_ch = "|".join(tse + otc)
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    try:
        return requests.get(url, headers=headers, timeout=10).json().get("msgArray", [])
    except Exception:
        return []


def fetch_yf_hist(stock_id: str):
    try:
        df = yf.Ticker(f"{stock_id}.TW").history(period="3mo")
        return None if df.empty else df
    except Exception:
        return None


def get_realtime_price(tw, yf_close):
    try:
        z = tw.get("z")
        if z not in ["-", "", None, "0"]:
            return float(z)
        b = tw.get("b")
        if b:
            return float(b.split("_")[0])
        a = tw.get("a")
        if a:
            return float(a.split("_")[0])
    except Exception:
        pass
    return yf_close


def calculate_kd(df, period=9):
    low_min  = df["Low"].rolling(window=period).min()
    high_max = df["High"].rolling(window=period).max()
    rsv = (df["Close"] - low_min) / (high_max - low_min) * 100
    df["K"] = rsv.ewm(com=2).mean()
    df["D"] = df["K"].ewm(com=2).mean()
    return df


def calculate_momentum(df, period=10):
    df["Momentum"] = df["Close"] - df["Close"].shift(period)
    return df


def calculate_macd(df):
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9).mean()
    df["MACD_hist"] = df["MACD"] - df["MACD_signal"]
    return df


def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, float("nan"))
    df["RSI"] = 100 - (100 / (1 + rs))
    return df




def calculate_ma(df):
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()
    df["VolMA20"] = df["Volume"].rolling(20).mean()
    return df




def early_breakout_score(df):
    if df is None or len(df) < 60:
        return None, []

    df = calculate_ma(df)

    l = df.iloc[-1]

    score = 0
    reasons = []

    # 均線收斂
    if abs(l["MA20"] - l["MA60"]) / l["MA60"] < 0.03:
        score += 25
        reasons.append("均線收斂")

    # 價格站上MA20
    if l["Close"] > l["MA20"]:
        score += 20
        reasons.append("站上MA20")

    # 溫和放量
    if l["Volume"] > l["VolMA20"] * 1.2:
        score += 20
        reasons.append("量能增溫")

    # 波動收斂
    recent_range = (df["High"].rolling(20).max() - df["Low"].rolling(20).min()) / df["Close"]
    if recent_range.iloc[-1] < 0.1:
        score += 20
        reasons.append("波動收斂")

    return score, reasons
def breakout_score(df):
    if df is None or len(df) < 60:
        return None, []

    df = calculate_ma(df)

    l = df.iloc[-1]
    p = df.iloc[-2]

    score = 0
    reasons = []

    if l["Close"] < l["MA20"]:
        return 0, []

    if l["Close"] > l["MA20"] > l["MA60"]:
        score += 30
        reasons.append("多頭排列")

    if l["Close"] >= df["Close"].rolling(60).max().iloc[-1]:
        score += 30
        reasons.append("突破新高")

    if l["Volume"] > l["VolMA20"] * 1.5:
        score += 20
        reasons.append("爆量")

    if l["MA20"] > p["MA20"]:
        score += 20
        reasons.append("均線上彎")

    return score, reasons
def score_stock(df, code):
    """計算技術面評分（0~100），越高越適合買入"""
    if df is None or len(df) < 30:
        return None, {}
    df = calculate_kd(df)
    df = calculate_momentum(df)
    df = calculate_macd(df)
    df = calculate_rsi(df)

    l, p = df.iloc[-1], df.iloc[-2]
    score = 0
    reasons = []

    # KD 黃金交叉
    if p["K"] < p["D"] and l["K"] > l["D"]:
        score += 30
        reasons.append("KD黃金交叉")
    # KD 超賣回升（K < 30）
    if l["K"] < 30:
        score += 15
        reasons.append(f"KD超賣(K={l['K']:.0f})")
    elif l["K"] < 50:
        score += 8

    # MACD 翻多
    if p["MACD_hist"] < 0 and l["MACD_hist"] > 0:
        score += 25
        reasons.append("MACD翻多")
    elif l["MACD_hist"] > 0 and l["MACD"] > l["MACD_signal"]:
        score += 10
        reasons.append("MACD多頭")

    # RSI 超賣
    rsi = l["RSI"]
    if 30 <= rsi <= 50:
        score += 20
        reasons.append(f"RSI低檔({rsi:.0f})")
    elif rsi < 30:
        score += 15
        reasons.append(f"RSI超賣({rsi:.0f})")

    # 動能正向
    if l["Momentum"] > 0:
        score += 10
        reasons.append("動能正向")

    return score, {"K": l["K"], "D": l["D"], "RSI": rsi,
                   "MACD_hist": l["MACD_hist"], "reasons": reasons,
                   "close": float(df["Close"].iloc[-1]),
                   "prev": float(df["Close"].iloc[-2])}


@st.cache_data(ttl=600)
def fetch_twse_top_volume(top_n: int = 200) -> list[tuple[str, str]]:
    """
    從 TWSE 即時行情抓當日成交量前 top_n 支上市股票（純股票，排除 ETF/權證）。
    回傳 [(code, name), ...]，按成交量降冪排列。
    快取 10 分鐘。
    """
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    result = []
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"
        r = requests.get(url, headers=headers, timeout=12)
        data = r.json()
        # data 是 list of dict: Code, Name, ClosingPrice, MonthlyAveragePrice
        for item in data:
            code = item.get("Code", "").strip()
            name = item.get("Name", "").strip()
            # 只保留 4 碼純數字（排除 ETF 如 0050/00878、權證等）
            if _re.match(r'^\d{4}$', code) and name:
                result.append((code, name))
    except Exception:
        pass

    # 備援：若 openapi 抓不到，改用 TWSE 大盤即時行情 API 取成交量排名
    if not result:
        try:
            url2 = "https://mis.twse.com.tw/stock/api/getCategory.jsp?ex=tse&i=MS&json=1"
            r2 = requests.get(url2, headers=headers, timeout=12)
            arr = r2.json().get("msgArray", [])
            for item in arr:
                code = item.get("c", "").strip()
                name = item.get("n", "").strip()
                vol_str = item.get("v", "0") or "0"
                try:
                    vol = float(vol_str)
                except Exception:
                    vol = 0
                if _re.match(r'^\d{4}$', code) and name and vol > 0:
                    result.append((code, name, vol))
            result.sort(key=lambda x: x[2] if len(x) > 2 else 0, reverse=True)
            result = [(c, n) for c, n, *_ in result]
        except Exception:
            pass

    # 最多取 top_n 筆
    return result[:top_n]


def run_market_scan_live(progress_bar, status_text, top_n: int = 200):
    """
    即時掃描 TWSE 成交量前 top_n 名股票，帶進度回呼。
    回傳評分 Top 5（不快取，由呼叫端控制）。
    """
    candidates = fetch_twse_top_volume(top_n)
    if not candidates:
        # 若 API 全失敗，回退到內建池
        candidates = [
            ("2330","台積電"), ("2317","鴻海"), ("2454","聯發科"), ("2382","廣達"),
            ("2308","台達電"), ("2881","富邦金"), ("2882","國泰金"), ("2891","中信金"),
            ("2886","兆豐金"), ("2884","玉山金"), ("2302","聯電"),   ("2357","華碩"),
            ("2412","中華電"), ("2002","中鋼"),   ("1301","台塑"),   ("1303","南亞"),
            ("6505","台塑化"), ("3711","日月光投控"), ("3008","大立光"), ("2327","國巨"),
            ("2059","川湖"),   ("2609","陽明"),   ("2615","萬海"),   ("2603","長榮"),
            ("6669","緯穎"),   ("4938","和碩"),   ("2912","統一超"), ("1101","台泥"),
        ]

    total   = len(candidates)
    results = []

    for i, (code, name) in enumerate(candidates):
        # 更新進度
        pct = (i + 1) / total
        progress_bar.progress(pct)
        status_text.markdown(
            f'<div class="scan-progress-text">掃描中 {i+1}/{total}　{name}（{code}）</div>',
            unsafe_allow_html=True,
        )
        try:
            df = yf.Ticker(f"{code}.TW").history(period="6mo")
            if df is None or df.empty:
                df = yf.Ticker(f"{code}.TWO").history(period="6mo")
            tech_score, info = score_stock(df, code)
            trend_score, trend_reasons = breakout_score(df)
            total_score = (tech_score or 0) + (trend_score or 0)

            if total_score > 0:
                results.append({
                    "code": code,
                    "name": name,
                    "score": total_score,
                    "trend_reasons": trend_reasons,
                    "early_reasons": early_reasons,
                    **(info or {})
                })
            if score is not None and score > 0:
                results.append({"code": code, "name": name, "score": score, **info})
        except Exception:
            pass

    progress_bar.progress(1.0)
    status_text.empty()
    results.sort(key=lambda x: x["score"], reverse=True)
    return results   # 回傳全部，由 UI 層決定顯示幾筆


def analyze_signal(df):
    if len(df) < 2:
        return "觀望", "無法判斷"
    l, p = df.iloc[-1], df.iloc[-2]
    sig = "觀望"
    if p["K"] < p["D"] and l["K"] > l["D"]:
        sig = "買進 (黃金交叉)"
    elif p["K"] > p["D"] and l["K"] < l["D"]:
        sig = "賣出 (死亡交叉)"
    trend = "上升動能" if l["Momentum"] > 0 else "下跌動能"
    return sig, trend


def get_stock_data(twse_data, stock):
    code = stock["id"]
    tw = next((x for x in twse_data if x.get("c") == code), None)
    # 名稱優先序：即時API > watchlist已存 > 內建表 > 代碼本身
    if tw and tw.get("n"):
        name = tw["n"]
    elif stock["name"] != code:
        name = stock["name"]
    else:
        name = _BUILTIN_NAME_MAP.get(code) or get_stock_name(code)
    df = fetch_yf_hist(code)

    prev_close = open_price = high = low = yf_close = None
    if df is not None and len(df) >= 2:
        prev_close = float(df["Close"].iloc[-2])
        open_price = float(df["Open"].iloc[-1])
        high       = float(df["High"].iloc[-1])
        low        = float(df["Low"].iloc[-1])
        yf_close   = float(df["Close"].iloc[-1])

    price = get_realtime_price(tw, yf_close) if tw else yf_close
    if prev_close is None and tw:
        try:    prev_close = float(tw.get("y") or 0)
        except: pass

    k = d = momentum = None
    signal = trend = "無資料"
    if df is not None:
        df = calculate_kd(df)
        df = calculate_momentum(df)
        signal, trend = analyze_signal(df)
        l = df.iloc[-1]
        k, d, momentum = float(l["K"]), float(l["D"]), float(l["Momentum"])

    change     = (price - prev_close) if (prev_close and price) else 0.0
    change_pct = (change / prev_close * 100) if prev_close else 0.0

    return dict(name=name, code=code, price=price, prev_close=prev_close,
                open=open_price, high=high, low=low,
                change=change, change_pct=change_pct,
                K=k, D=d, Momentum=momentum, signal=signal, trend=trend)


# ══════════════════════════════════════════════════════════
# 畫面輔助
# ══════════════════════════════════════════════════════════
def fmt(v, d=2):
    return f"{v:.{d}f}" if v is not None else "－"

def direction_class(c):
    if c > 0: return "up",   "up-color",   "▲"
    if c < 0: return "down", "down-color",  "▼"
    return "flat", "flat-color", "－"

def sig_cls(s):
    if "買進" in s: return "badge-signal-buy"
    if "賣出" in s: return "badge-signal-sell"
    return "badge-signal-watch"

def trend_cls(t):
    return "badge-trend-up" if "上升" in t else "badge-trend-down"

def kd_bar(val, color):
    pct = min(max(val, 0), 100) if val is not None else 50
    return (
        '<div class="kd-bar-wrap"><div class="kd-bar-fill" style="'
        f'--bar-width:{pct:.0f}%;--bar-color:{color};"></div></div>'
    )


def render_card(row, idx):
    cc, pc, arrow = direction_class(row["change"])

    ohlc = "".join(
        f'<div class="ohlc-item"><div class="ohlc-label">{lb}</div>'
        f'<div class="ohlc-val">{fmt(v)}</div></div>'
        for lb, v in [("昨收", row["prev_close"]), ("開盤", row["open"]),
                      ("最高", row["high"]),        ("最低", row["low"])]
    )

    if row["K"] is not None:
        kd_sec = (
            '<div class="kd-row">'
            '<div class="kd-chip"><div class="kd-chip-label">K 值</div>'
            f'<div class="kd-chip-val">{fmt(row["K"])}</div>{kd_bar(row["K"], "#38bdf8")}</div>'
            '<div class="kd-chip"><div class="kd-chip-label">D 值</div>'
            f'<div class="kd-chip-val">{fmt(row["D"])}</div>{kd_bar(row["D"], "#f472b6")}</div>'
            '</div>'
        )
        mc = "#22c55e" if row["Momentum"] > 0 else "#ef4444"
        mom_sec = (
            '<div class="momentum-row"><span class="momentum-label">動能指標 (10日)</span>'
            f'<span class="momentum-val" style="color:{mc};">{fmt(row["Momentum"])}</span></div>'
        )
        st_text, tr_text = row["signal"], row["trend"]
    else:
        kd_sec  = '<div class="no-data">歷史資料不足，無法計算技術指標</div>'
        mom_sec = ""
        st_text, tr_text = "資料不足", ""

    tr_badge = f'<span class="badge {trend_cls(tr_text)}">{tr_text}</span>' if tr_text else ""
    chg_str  = f'{arrow} {abs(row["change"]):.2f} ({abs(row["change_pct"]):.2f}%)' if row["change"] else "－"

    st.markdown(
        f'<div class="stock-card {cc}">'
        '<div class="card-top"><div>'
        f'<div class="stock-name">{row["name"]}</div>'
        f'<div class="stock-code">{row["code"]} · TW</div>'
        '</div><div class="price-block">'
        f'<div class="price-main">{fmt(row["price"])}</div>'
        f'<div class="price-change {pc}">{chg_str}</div>'
        '</div></div>'
        f'<div class="ohlc-row">{ohlc}</div>'
        '<div class="card-divider"></div>'
        '<div class="tech-section-title">技術指標</div>'
        f'{kd_sec}{mom_sec}'
        f'<div class="signal-row"><span class="badge {sig_cls(st_text)}">{st_text}</span>{tr_badge}</div>'
        '</div><div class="card-gap"></div>',
        unsafe_allow_html=True,
    )

    if st.button(f"移除  {row['name']} ({row['code']})", key=f"del_{row['code']}_{idx}"):
        st.session_state.watchlist = [
            s for s in st.session_state.watchlist if s["id"] != row["code"]
        ]
        save_watchlist(st.session_state.watchlist)
        st.rerun()


# ══════════════════════════════════════════════════════════
# 主程式
# ══════════════════════════════════════════════════════════

# ① 每次 run 最開始先從 query_params 讀取 watchlist
#    （query_params 在 Streamlit 啟動時就已解析完畢，不存在時序問題）
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()
    # 自動修補：若某支股票的 name 就是 id（代表之前沒查到中文名稱），補回正確名稱
    needs_save = False
    for s in st.session_state.watchlist:
        if s["name"] == s["id"]:
            recovered = get_stock_name(s["id"])
            if recovered != s["id"]:
                s["name"] = recovered
                needs_save = True
    save_watchlist(st.session_state.watchlist)

# ② 注入 localStorage 輔助（把目前網址同步存/還原，為雙重保險）
inject_localstorage_helper()

if "add_msg"  not in st.session_state: st.session_state.add_msg  = ""
if "add_type" not in st.session_state: st.session_state.add_type = ""

now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

# ── 頂部標題 ─────────────────────────────────────────────
st.markdown(
    '<div class="app-header">'
    '<div class="app-title">📊 台股<span>看盤</span></div>'
    f'<div class="app-time"><span class="live-dot"></span>即時更新<br>{now}</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── 書籤提示 ─────────────────────────────────────────────
st.markdown(
    '<div class="bookmark-hint">'
    '<span class="bookmark-hint-icon">🔖</span>'
    '<span>將目前網址加入<strong>書籤</strong>，下次直接開啟書籤即可還原您的關注清單</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── 新增股票 ──────────────────────────────────────────────
with st.expander("➕ 新增關注股票", expanded=False):
    st.markdown(
        '<div class="add-section-title">輸入台股代碼（上市 / 上櫃 / ETF）</div>',
        unsafe_allow_html=True,
    )
    new_id = st.text_input(
        "代碼", placeholder="例如：0050、2454、6669",
        label_visibility="collapsed", key="new_stock_input",
    )
    if st.button("查詢並加入", key="add_btn"):
        cid = new_id.strip()
        if not cid:
            st.session_state.add_msg  = "請輸入股票代碼"
            st.session_state.add_type = "err"
        elif any(s["id"] == cid for s in st.session_state.watchlist):
            st.session_state.add_msg  = f"「{cid}」已在關注清單中"
            st.session_state.add_type = "err"
        else:
            with st.spinner("查詢中…"):
                valid, name = verify_stock(cid)
            if valid:
                st.session_state.watchlist.append({"id": cid, "name": name})
                save_watchlist(st.session_state.watchlist)   # ← 立即寫入 query_params
                st.session_state.add_msg  = f"✅ 已加入「{name}（{cid}）」"
                st.session_state.add_type = "ok"
                st.rerun()
            else:
                st.session_state.add_msg  = f"找不到代碼「{cid}」，請確認為台股代碼"
                st.session_state.add_type = "err"

    if st.session_state.add_msg:
        st.markdown(
            f'<div class="{"success-msg" if st.session_state.add_type == "ok" else "error-msg"}">'
            f'{st.session_state.add_msg}</div>',
            unsafe_allow_html=True,
        )

# ── 市場掃描推薦 ──────────────────────────────────────────
MEDALS   = ["🥇","🥈","🥉","4️⃣","5️⃣"]
PAGE_SIZE = 20

def _score_color(score):
    if score >= 60: return "#22c55e"
    if score >= 35: return "#f59e0b"
    if score >= 10: return "#38bdf8"
    return "#475569"

def _score_bar_color(score):
    if score >= 60: return "#22c55e"
    if score >= 35: return "#f59e0b"
    return "#38bdf8"

def render_scan_row(rank, s, in_watchlist):
    pct       = (s["close"] - s["prev"]) / s["prev"] * 100 if s.get("prev") else 0
    pct_color = "#ef4444" if pct > 0 else "#22c55e"
    pct_str   = f"{'▲' if pct>0 else '▼'} {abs(pct):.2f}%"
    sc        = s["score"]
    sc_color  = _score_color(sc)
    bar_color = _score_bar_color(sc)
    sr_color  = sc_color

    reasons = (s.get("reasons", []) or []) + (s.get("trend_reasons", []) or []) + (s.get("early_reasons", []) or [])
    if reasons:
        chips = "".join(f'<span class="scan-sig-chip">{r}</span>' for r in reasons)
    else:
        chips = '<span class="scan-sig-chip neutral">無明顯信號</span>'

    medal = MEDALS[rank - 1] if rank <= 5 else f"#{rank}"

    st.markdown(
        f'<div class="scan-row" style="--sr:{sr_color};">'
        f'<div class="scan-row-rank">{medal}</div>'
        f'<div class="scan-row-info">'
        f'<div class="scan-row-name">{s["name"]}</div>'
        f'<div class="scan-row-code">{s["code"]} · '
        f'K{s["K"]:.0f} D{s["D"]:.0f} RSI{s["RSI"]:.0f}</div>'
        f'<div class="scan-row-signals">{chips}</div>'
        f'</div>'
        f'<div class="scan-row-right">'
        f'<div class="scan-row-score" style="color:{sc_color};">{sc}分</div>'
        f'<div class="score-bar-wrap" style="width:56px;margin:3px 0 3px auto;">'
        f'<div class="score-bar-fill" style="--sw:{min(sc,100)}%;background:{bar_color};"></div></div>'
        f'<div class="scan-row-pct" style="color:{pct_color};">{pct_str}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    # 加入關注清單按鈕
    btn_label = f"✓ 已加入" if in_watchlist else f"＋ 加入關注"
    if not in_watchlist:
        if st.button(btn_label, key=f"qadd_{s['code']}_{rank}", use_container_width=True):
            st.session_state.watchlist.append({"id": s["code"], "name": s["name"]})
            save_watchlist(st.session_state.watchlist)
            st.rerun()
    else:
        st.markdown(
            f'<div style="font-size:0.65rem;color:#4ade80;text-align:center;'
            f'padding:0.2rem 0;margin-bottom:0.35rem;">✓ 已在關注清單</div>',
            unsafe_allow_html=True,
        )


def render_scan_section():
    st.markdown(
        '<div class="scan-section">'
        '<div class="scan-header">'
        '<div><div class="scan-title">🔍 台股<span>掃描瀏覽</span></div>'
        '<div class="scan-subtitle">即時成交量前 200 名 · 全部結果可翻頁瀏覽</div></div>'
        '<span class="scan-badge">即時選股</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # session_state 初始化
    for k, v in [("scan_results", None), ("scan_timestamp", None),
                 ("scan_page", 0), ("scan_sort", "score"), ("scan_q", "")]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── 掃描按鈕 ────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.scan_timestamp:
            total_cnt = len(st.session_state.scan_results or [])
            st.markdown(
                f'<div style="font-size:0.65rem;color:#475569;">'
                f'上次掃描：{st.session_state.scan_timestamp}　共 {total_cnt} 筆</div>',
                unsafe_allow_html=True,
            )
    with col2:
        do_scan = st.button("▶ 掃描", key="scan_btn", use_container_width=True)

    if do_scan or st.session_state.scan_results is None:
        st.markdown(
            '<div style="font-size:0.7rem;color:#64748b;margin-bottom:0.4rem;">'
            '正在抓取當日成交量前 200 名，逐一進行技術分析…</div>',
            unsafe_allow_html=True,
        )
        progress_bar = st.progress(0)
        status_text  = st.empty()
        all_results  = run_market_scan_live(progress_bar, status_text, top_n=200)
        st.session_state.scan_results   = all_results
        st.session_state.scan_timestamp = datetime.now().strftime("%m/%d %H:%M")
        st.session_state.scan_page      = 0
        st.rerun()
        return

    all_results = st.session_state.scan_results or []
    if not all_results:
        st.markdown('<div class="no-data">目前無資料，請點掃描</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── 搜尋框 ──────────────────────────────────────────────
    q = st.text_input(
        "搜尋", placeholder="🔎  搜尋股票名稱或代碼…",
        value=st.session_state.scan_q,
        key="scan_search_input",
        label_visibility="collapsed",
    )
    if q != st.session_state.scan_q:
        st.session_state.scan_q    = q
        st.session_state.scan_page = 0
        st.rerun()

    # ── 排序切換 ────────────────────────────────────────────
    sort_options = {"score": "評分↓", "pct_desc": "漲幅↓", "pct_asc": "跌幅↓"}
    sort_labels  = list(sort_options.values())
    sort_keys    = list(sort_options.keys())
    cur_sort_idx = sort_keys.index(st.session_state.scan_sort) if st.session_state.scan_sort in sort_keys else 0

    sel = st.radio(
        "排序", sort_labels,
        index=cur_sort_idx,
        horizontal=True,
        key="scan_sort_radio",
        label_visibility="collapsed",
    )
    new_sort = sort_keys[sort_labels.index(sel)]
    if new_sort != st.session_state.scan_sort:
        st.session_state.scan_sort = new_sort
        st.session_state.scan_page = 0
        st.rerun()

    # ── 篩選 + 排序資料 ─────────────────────────────────────
    data = all_results[:]
    if q:
        ql = q.lower()
        data = [s for s in data if ql in s["name"].lower() or ql in s["code"].lower()]

    if st.session_state.scan_sort == "pct_desc":
        data.sort(key=lambda s: (s["close"]-s["prev"])/s["prev"] if s.get("prev") else 0, reverse=True)
    elif st.session_state.scan_sort == "pct_asc":
        data.sort(key=lambda s: (s["close"]-s["prev"])/s["prev"] if s.get("prev") else 0)
    else:
        data.sort(key=lambda x: x["score"], reverse=True)

    total     = len(data)
    max_page  = max((total - 1) // PAGE_SIZE, 0)
    page      = min(st.session_state.scan_page, max_page)
    start     = page * PAGE_SIZE
    end       = min(start + PAGE_SIZE, total)
    page_data = data[start:end]

    watchlist_ids = {s["id"] for s in st.session_state.watchlist}

    st.markdown(
        f'<div class="scan-stats">'
        f'<span>共 {total} 筆結果</span>'
        f'<span>第 {start+1}–{end} 筆</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── 逐筆顯示 ────────────────────────────────────────────
    for i, s in enumerate(page_data):
        global_rank = start + i + 1
        render_scan_row(global_rank, s, s["code"] in watchlist_ids)

    # ── 分頁導航 ────────────────────────────────────────────
    st.markdown('<div class="page-nav">', unsafe_allow_html=True)
    pc1, pc2, pc3 = st.columns([1, 2, 1])
    with pc1:
        if page > 0:
            if st.button("◀ 上一頁", key="scan_prev", use_container_width=True):
                st.session_state.scan_page = page - 1
                st.rerun()
    with pc2:
        st.markdown(
            f'<div class="page-info" style="text-align:center;padding-top:0.4rem;">'
            f'{page+1} / {max_page+1} 頁</div>',
            unsafe_allow_html=True,
        )
    with pc3:
        if page < max_page:
            if st.button("下一頁 ▶", key="scan_next", use_container_width=True):
                st.session_state.scan_page = page + 1
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.62rem;color:#334155;text-align:center;margin-bottom:0.8rem;">'
        '⚠️ 以上僅為技術面參考，不構成投資建議，請自行判斷風險</div>',
        unsafe_allow_html=True,
    )

with st.expander("🔍 台股掃描瀏覽（即時成交量 Top 200）", expanded=False):
    render_scan_section()

# ── 股票清單 ──────────────────────────────────────────────
if not st.session_state.watchlist:
    st.markdown(
        '<div style="text-align:center;padding:3rem 1rem;color:#475569;">'
        '<div style="font-size:2.5rem;margin-bottom:0.75rem;">📭</div>'
        '<div style="font-size:0.9rem;font-weight:700;color:#64748b;">關注清單是空的</div>'
        '<div style="font-size:0.75rem;margin-top:0.4rem;">點上方「新增關注股票」來加入</div>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    ids       = [s["id"] for s in st.session_state.watchlist]
    twse_data = fetch_twse_realtime(ids)
    for idx, stock in enumerate(st.session_state.watchlist):
        row = get_stock_data(twse_data, stock)
        render_card(row, idx)

# ── 頁尾 ──────────────────────────────────────────────────
st.markdown(
    '<div class="footer-note">'
    "資料來源：TWSE 即時 API + Yahoo Finance<br>"
    "每 15 秒自動更新 ／ 僅供參考，不構成投資建議"
    "</div>",
    unsafe_allow_html=True,
)

time.sleep(15)
st.rerun()
