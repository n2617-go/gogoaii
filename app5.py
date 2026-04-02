import streamlit as st
import streamlit.components.v1 as components
import requests
import yfinance as yf
import pandas as pd
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


def score_stock(df, code):
    """
    主流強勢股評分（0~100）：
      MA趨勢（30）＋ 接近新高（30）＋ 量能爆發（20）＋ 當日漲幅（20）
    同時附帶 KD/RSI 供顯示用。
    """
    if df is None or len(df) < 22:
        return None, {}

    # ── 相容新版 yfinance MultiIndex columns ──────────────
    # 新版結構：columns = MultiIndex[(Price, Ticker), ...]
    # 例如 df["Close"] 可能是 MultiIndex，需先降維
    if isinstance(df.columns, pd.MultiIndex):
        # level 0 = 欄位名稱 (Close/Open/…), level 1 = ticker
        # 先嘗試用 ticker 取單支
        tickers_in_col = df.columns.get_level_values(1).unique().tolist()
        target = code + ".TW"
        if target in tickers_in_col:
            df = df.xs(target, axis=1, level=1)
        elif len(tickers_in_col) == 1:
            df = df.xs(tickers_in_col[0], axis=1, level=1)
        else:
            df = df.droplevel(1, axis=1)

    df = df.copy()
    # 確保欄位名稱統一（有時會出現 Price/Adj Close 等變體）
    df.columns = [str(c).strip() for c in df.columns]
    close_col  = next((c for c in df.columns if c.lower() == "close"), None) or \
                 next((c for c in df.columns if "close" in c.lower() and "adj" not in c.lower()), None)
    vol_col    = next((c for c in df.columns if c.lower() == "volume"), None) or \
                 next((c for c in df.columns if "volume" in c.lower()), None)
    high_col   = next((c for c in df.columns if c.lower() == "high"), None) or \
                 next((c for c in df.columns if "high" in c.lower()), None)
    low_col    = next((c for c in df.columns if c.lower() == "low"), None) or \
                 next((c for c in df.columns if "low" in c.lower()), None)
    if not close_col or not vol_col:
        return None, {}

    close  = df[close_col].dropna()
    volume = df[vol_col].dropna()
    high   = df[high_col].dropna() if high_col else close
    low    = df[low_col].dropna()  if low_col  else close
    if len(close) < 22:
        return None, {}

    # ── 指標計算 ──────────────────────────────────────────
    ma5    = close.rolling(5).mean()
    ma20   = close.rolling(20).mean()
    volma5 = volume.rolling(5).mean()

    # KD（供顯示）
    low_min  = low.rolling(9).min()
    high_max = high.rolling(9).max()
    rng      = (high_max - low_min).replace(0, float("nan"))
    rsv      = (close - low_min) / rng * 100
    k_series = rsv.ewm(com=2).mean()
    d_series = k_series.ewm(com=2).mean()

    # RSI（供顯示）
    delta    = close.diff()
    gain     = delta.clip(lower=0).rolling(14).mean()
    loss     = (-delta.clip(upper=0)).rolling(14).mean()
    rs       = gain / loss.replace(0, float("nan"))
    rsi_s    = 100 - (100 / (1 + rs))

    last_close  = float(close.iloc[-1])
    prev_close  = float(close.iloc[-2]) if len(close) >= 2 else last_close
    last_vol    = float(volume.iloc[-1])
    last_volma5 = float(volma5.iloc[-1]) if pd.notna(volma5.iloc[-1]) else 0
    last_ma5    = float(ma5.iloc[-1])    if pd.notna(ma5.iloc[-1])    else 0
    last_ma20   = float(ma20.iloc[-1])   if pd.notna(ma20.iloc[-1])   else 0
    last_k      = float(k_series.iloc[-1]) if pd.notna(k_series.iloc[-1]) else 50.0
    last_d      = float(d_series.iloc[-1]) if pd.notna(d_series.iloc[-1]) else 50.0
    last_rsi    = float(rsi_s.iloc[-1])    if pd.notna(rsi_s.iloc[-1])    else 50.0
    high60      = float(close.tail(60).max())

    score   = 0
    reasons = []
    breakdown = {}  # 各指標得分明細
    change  = (last_close - prev_close) / prev_close if prev_close else 0

    # ① MA 趨勢：MA5 > MA20  → 最高 30 分
    if last_ma5 > 0 and last_ma20 > 0 and last_ma5 > last_ma20:
        score += 30
        reasons.append("均線多頭")
        breakdown["均線多頭 MA5>MA20"] = 30
    else:
        breakdown["均線多頭 MA5>MA20"] = 0

    # ② 接近 60 日新高（>= 97%）→ 最高 30 分
    if high60 > 0 and last_close >= high60 * 0.97:
        score += 30
        reasons.append("逼近新高")
        breakdown["逼近60日新高 ≥97%"] = 30
    else:
        breakdown["逼近60日新高 ≥97%"] = 0

    # ③ 量能爆發：當日量 > 5日均量 × 1.5  → 最高 20 分
    if last_volma5 > 0 and last_vol > last_volma5 * 1.5:
        score += 20
        reasons.append("量能爆發")
        breakdown["量能爆發 >均量×1.5"] = 20
    else:
        breakdown["量能爆發 >均量×1.5"] = 0

    # ④ 當日漲幅  → 最高 20 分
    if change > 0.03:
        score += 20
        reasons.append(f"強漲{change*100:.1f}%")
        breakdown[f"強漲 >3% ({change*100:.1f}%)"] = 20
    elif change > 0.01:
        score += 8
        reasons.append(f"小漲{change*100:.1f}%")
        breakdown[f"小漲 1~3% ({change*100:.1f}%)"] = 8
    else:
        breakdown["當日漲幅"] = 0

    return score, {
        "K": last_k, "D": last_d, "RSI": last_rsi,
        "MACD_hist": change,
        "reasons": reasons,
        "breakdown": breakdown,
        "close": last_close,
        "prev":  prev_close,
    }


@st.cache_data(ttl=3600)
def fetch_twse_top_volume(top_n: int = 1800) -> list[tuple[str, str]]:
    """
    抓取全市場上市＋上櫃股票清單。
    策略：API + 內建靜態清單 **一律全部合併**，不短路。
    確保任何情況下都有 1000+ 筆可掃描。
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    name_map = {}   # code -> name，用 dict 去重並保留名稱

    # ── 1. TWSE 上市 OpenAPI ───────────────────────────────
    for url in [
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL",
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL",
    ]:
        try:
            data = requests.get(url, headers=headers, timeout=15).json()
            if isinstance(data, list):
                for item in data:
                    code = str(item.get("Code", "")).strip()
                    name = str(item.get("Name", "")).strip()
                    if _re.match(r'^\d{4}$', code) and name:
                        name_map[code] = name
            if len(name_map) >= 800:
                break
        except Exception:
            continue

    # ── 2. TPEx 上櫃 OpenAPI（所有備援欄位都試）──────────
    tpex_attempts = [
        ("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes",
         [("SecuritiesCompanyCode","CompanyName"), ("Code","Name"), ("code","name")]),
        ("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis",
         [("SecuritiesCompanyCode","CompanyName"), ("Code","Name")]),
        ("https://www.tpex.org.tw/openapi/v1/tpex_listed_companies",
         [("SecuritiesCompanyCode","CompanyName"), ("Code","Name")]),
    ]
    for url, field_pairs in tpex_attempts:
        try:
            data = requests.get(url, headers=headers, timeout=15).json()
            if not isinstance(data, list) or len(data) < 5:
                continue
            # 偵測哪對欄位有效
            sample = data[0] if data else {}
            ck, nk = "Code", "Name"
            for fk, fn in field_pairs:
                if fk in sample:
                    ck, nk = fk, fn
                    break
            added = 0
            for item in data:
                code = str(item.get(ck, "")).strip()
                name = str(item.get(nk, "")).strip()
                if _re.match(r'^\d{4}$', code) and name and code not in name_map:
                    name_map[code] = name
                    added += 1
            if added >= 50:
                break
        except Exception:
            continue

    # ── 3. 內建靜態清單（不管 API 有沒有成功，一律補入）──
    BUILTIN = [
        ("2330","台積電"),("2454","聯發科"),("2303","聯電"),("2344","華邦電"),
        ("2408","南亞科"),("3711","日月光投控"),("2379","瑞昱"),("3034","聯詠"),
        ("2337","旺宏"),("6415","矽力-KY"),("4938","和碩"),("2357","華碩"),
        ("2376","技嘉"),("3008","大立光"),("2382","廣達"),("2317","鴻海"),
        ("2308","台達電"),("2327","國巨"),("2360","致茂"),("3037","欣興"),
        ("3044","健鼎"),("4919","新唐"),("2059","川湖"),("5269","祥碩"),
        ("6669","緯穎"),("2356","英業達"),("2353","宏碁"),("6770","力積電"),
        ("3533","嘉澤"),("2368","金像電"),("2385","群光"),("2392","正崴"),
        ("2404","漢唐"),("2441","超豐"),("2449","京元電子"),("3045","台灣大"),
        ("4904","遠傳"),("2412","中華電"),("2324","仁寶"),("2352","佳世達"),
        ("3042","晶技"),("2409","友達"),("3481","群創"),("5483","中美晶"),
        ("3105","穩懋"),("2881","富邦金"),("2882","國泰金"),("2891","中信金"),
        ("2886","兆豐金"),("2884","玉山金"),("2892","第一金"),("2880","華南金"),
        ("2885","元大金"),("2887","台新金"),("2883","開發金"),("2890","永豐金"),
        ("2888","新光金"),("5880","合庫金"),("2801","彰銀"),("5876","上海商銀"),
        ("2834","臺企銀"),("2838","聯邦銀"),("2849","安泰銀"),("2823","中壽"),
        ("6005","群益證"),("2002","中鋼"),("1301","台塑"),("1303","南亞"),
        ("1326","台化"),("6505","台塑化"),("1101","台泥"),("1102","亞泥"),
        ("1216","統一"),("1402","遠紡"),("1434","福懋"),("1440","南紡"),
        ("2006","東和鋼"),("2007","燁興"),("2008","高興昌"),("2010","春源"),
        ("2014","中鴻"),("2015","豐興"),("1605","華新"),("1604","聲寶"),
        ("1603","華城"),("1538","正峰"),("1536","和成"),("1533","車王電"),
        ("2609","陽明"),("2615","萬海"),("2603","長榮"),("2610","華航"),
        ("2618","長榮航"),("2605","新興"),("2606","裕民"),("2607","榮運"),
        ("2608","大榮"),("2207","和泰車"),("2201","裕隆"),("2204","中華"),
        ("2206","三陽工"),("1590","亞德客"),("2103","台橡"),("2105","正新"),
        ("1504","東元"),("1503","士林電"),("1502","中興電"),("2912","統一超"),
        ("2903","遠百"),("1217","愛之味"),("1218","泰山"),("1219","福壽"),
        ("1227","佳格"),("1229","聯華"),("1232","大統益"),("1234","黑松"),
        ("2504","國產"),("2505","國揚"),("2511","太子"),("2515","中工"),
        ("2520","冠德"),("2524","京城"),("2527","宏璟"),("2528","皇翔"),
        ("5522","遠雄"),("5534","長虹"),("5536","聖暉"),("3673","TPK-KY"),
        ("6176","瑞儀"),("6271","同欣電"),("6274","台燿"),("6277","宏正"),
        ("6279","胡連"),("6285","啟碁"),("6290","良維"),("3702","大聯大"),
        ("3706","神達"),("8016","矽創"),("8020","彩晶"),("8039","台虹"),
        ("4736","泰博"),("4737","華廣"),("4739","康普"),("4743","合一"),
        ("4747","強茂"),("4757","宇瞻"),("6741","91APP-KY"),("6745","晶宏"),
        ("6746","台揚"),("6748","瑞傳"),("6749","愛普"),("6752","岱宇"),
        # 補充上市中小型
        ("1110","東泥"),("1111","南亞塑"),("1201","味全"),("1203","味王"),
        ("1210","大成"),("1213","大飲"),("1215","卜蜂"),("1231","聯華實"),
        ("1304","台聚"),("1305","華夏"),("1308","亞聚"),("1309","台達化"),
        ("1310","台苯"),("1312","國喬"),("1313","聯成"),("1315","達新"),
        ("1316","上曜"),("1321","大洋"),("1323","永裕"),("1324","地球"),
        ("1325","恆大"),("1330","恆豐"),("1337","再生"),("1338","廣輝"),
        ("1339","昭輝"),("1340","勝泰"),("1341","富林"),("1342","八方"),
        ("1409","新纖"),("1410","南染"),("1412","中紡"),("1413","宏洲"),
        ("1414","東和"),("1416","廣豐"),("1417","嘉裕"),("1418","東華"),
        ("1419","新遠東"),("1423","利華"),("1436","華友聯"),("1437","勤益控"),
        ("1438","裕豐"),("1439","中和"),("1444","力麗"),("1445","大宇"),
        ("1446","宏和"),("1447","力鵬"),("1448","中興紡"),("1449","佳和"),
        ("1452","宏益"),("1453","大將"),("1454","台富"),("1456","怡華"),
        ("1457","宜進"),("1459","聯發"),("1460","宏遠"),("1461","中鑫"),
        ("1462","中宇"),("1463","強盛"),("1464","得力"),("1465","偉全"),
        ("1466","聚隆"),("1467","南緯"),("1468","昶和"),("1470","大魯閣"),
        ("2101","南港"),("2102","泰豐"),("2104","中橡"),("2106","建大"),
        ("2108","南帝"),("2109","華豐"),("2114","鑫永銓"),("2115","六暉"),
        ("2117","味丹"),("2118","松霖"),("2120","日勝生"),("2121","三優"),
        ("2123","中宇"),("2124","愷信"),("2125","湯石"),("2126","紅陽能源"),
        ("2201","裕隆"),("2202","裕隆日產"),("2203","台灣日産"),("2208","台船"),
        ("2209","裕融"),("2211","長榮鋼"),("2212","新煒"),("2213","東普"),
        ("2215","廣隆"),("2216","貳陸"),("2219","成運"),("2220","彰源"),
        ("2221","大甲"),("2222","大江"),("2223","鑫聯"),("2224","豐釩"),
        ("2227","裕日車"),("2228","劍麟"),("2229","聿聯"),("2230","泰銘"),
        ("2231","為升"),("2233","宇隆"),("2235","環兆"),("2236","東台"),
        ("2239","合騏"),("2241","艾姆勒"),("2243","迎廣"),("2246","振躍"),
        ("2247","雙德"),("2249","志聖"),("2250","友輝"),("2251","順德"),
    ]
    for code, name in BUILTIN:
        if code not in name_map:
            name_map[code] = name

    # 轉成 list 輸出
    result = list(name_map.items())   # [(code, name), ...]
    return result[:top_n]


def fetch_realtime_price_batch(codes: list[str]) -> dict[str, float]:
    """
    用 TWSE 即時 API 一次查多支股票的即時價格。
    回傳 {code: price}。
    """
    prices  = {}
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    # 分批查（每批最多 50 支）
    for i in range(0, len(codes), 50):
        batch = codes[i:i+50]
        ex_ch = "|".join([f"tse_{c}.tw" for c in batch] + [f"otc_{c}.tw" for c in batch])
        try:
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1"
            arr = requests.get(url, headers=headers, timeout=8).json().get("msgArray", [])
            for item in arr:
                code = item.get("c", "")
                z    = item.get("z", "-")
                if z not in ["-", "", None, "0"]:
                    try:
                        prices[code] = float(z)
                    except Exception:
                        pass
        except Exception:
            pass
    return prices


@st.cache_data(ttl=1800)
def _fetch_hist_cached(code: str) -> pd.DataFrame | None:
    """
    快取單支股票 2 個月歷史（ttl=30 分鐘）。
    第二次掃描直接從 Streamlit 快取讀，不重打 Yahoo Finance API。
    """
    for suffix in [".TW", ".TWO"]:
        try:
            df = yf.Ticker(f"{code}{suffix}").history(period="2mo")
            if df is not None and not df.empty and len(df) >= 22:
                return df
        except Exception:
            pass
    return None


def run_market_scan_live(progress_bar, status_text, result_container, top_n: int = 1800):
    """
    掃描全市場股票。
    使用 @st.cache_data 逐支快取，第二次掃描從快取讀，結果穩定不會變 0。
    """
    candidates = fetch_twse_top_volume(top_n)
    n_cand     = len(candidates)

    status_text.markdown(
        f'<div class="scan-progress-text">📋 股票清單 {n_cand} 筆，開始掃描…</div>',
        unsafe_allow_html=True,
    )

    total        = len(candidates)
    results      = []
    PREVIEW_STEP = 5

    for i, (code, name) in enumerate(candidates):
        progress_bar.progress((i + 1) / total)
        if i % 10 == 0:
            status_text.markdown(
                f'<div class="scan-progress-text">'
                f'分析 {i+1}/{total}　{name}（{code}）　'
                f'<span style="color:#4ade80;">✅ {len(results)} 筆</span></div>',
                unsafe_allow_html=True,
            )

        df = _fetch_hist_cached(code)
        if df is None:
            continue

        try:
            score, info = score_stock(df, code)
            if score is None or score < 30:
                continue
            results.append({"code": code, "name": name, "score": score, **info})
            if len(results) % PREVIEW_STEP == 0:
                _render_live_preview(result_container, results)
        except Exception:
            continue

    progress_bar.progress(1.0)
    status_text.markdown(
        f'<div class="scan-progress-text" style="color:#4ade80;">'
        f'✅ 掃描完成！分析 {total} 支，找到 {len(results)} 筆，補抓即時股價中…</div>',
        unsafe_allow_html=True,
    )

    if results:
        codes     = [s["code"] for s in results]
        rt_prices = fetch_realtime_price_batch(codes)
        for s in results:
            if s["code"] in rt_prices:
                s["realtime_price"] = rt_prices[s["code"]]

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def _render_live_preview(container, results):
    """即時預覽：顯示目前已找到的前 10 筆（掃描中用）"""
    top = sorted(results, key=lambda x: x["score"], reverse=True)[:10]
    SCORE_COLORS = ["#f59e0b","#94a3b8","#cd7f32","#38bdf8","#38bdf8",
                    "#38bdf8","#38bdf8","#38bdf8","#38bdf8","#38bdf8"]
    html = '<div style="margin-top:0.5rem;">'
    html += '<div style="font-size:0.65rem;color:#475569;margin-bottom:0.4rem;">🔴 即時預覽（掃描中持續更新）</div>'
    for i, s in enumerate(top):
        pct      = (s["close"] - s["prev"]) / s["prev"] * 100 if s.get("prev") else 0
        pc       = "#ef4444" if pct > 0 else "#22c55e"
        sc_color = SCORE_COLORS[i] if i < len(SCORE_COLORS) else "#38bdf8"
        rt       = s.get("realtime_price")
        price_str = f'{rt:.2f}' if rt else f'{s["close"]:.2f}'
        price_label = "即時" if rt else "收盤"
        reasons  = "　".join(s.get("reasons", []))
        medal    = MEDALS[i] if i < len(MEDALS) else f"#{i+1}"
        html += (
            f'<div class="scan-row" style="--sr:{sc_color};">'
            f'<div class="scan-row-rank">{medal}</div>'
            f'<div class="scan-row-info">'
            f'<div class="scan-row-name">{s["name"]}</div>'
            f'<div class="scan-row-code">{s["code"]} · {reasons}</div>'
            f'</div>'
            f'<div class="scan-row-right">'
            f'<div class="scan-row-score" style="color:{sc_color};">{s["score"]}分</div>'
            f'<div style="font-size:0.7rem;font-weight:700;color:#f1f5f9;">{price_str}</div>'
            f'<div class="scan-row-pct" style="color:{pc};">▲ {abs(pct):.1f}%　{price_label}</div>'
            f'</div></div>'
        )
    html += '</div>'
    container.markdown(html, unsafe_allow_html=True)

    total   = len(candidates)
    results = []
    skip    = 0
    hit     = 0

    for i, (code, name) in enumerate(candidates):
        pct = (i + 1) / total
        progress_bar.progress(pct)
        status_text.markdown(
            f'<div class="scan-progress-text">'
            f'分析 {i+1}/{total}　{name}（{code}）　✅{hit} 筆　⬜{skip} 筆略過</div>',
            unsafe_allow_html=True,
        )

        df = None
        # 先試上市(.TW)，再試上櫃(.TWO)
        for suffix in [".TW", ".TWO"]:
            try:
                tmp = yf.Ticker(f"{code}{suffix}").history(period="2mo")
                if tmp is not None and not tmp.empty and len(tmp) >= 22:
                    df = tmp
                    break
            except Exception:
                pass

        if df is None:
            skip += 1
            continue

        try:
            score, info = score_stock(df, code)
            if score is None:
                skip += 1
                continue
            if score >= 30:
                hit += 1
                results.append({"code": code, "name": name, "score": score, **info})
            else:
                skip += 1
        except Exception:
            skip += 1
            continue

    progress_bar.progress(1.0)
    status_text.markdown(
        f'<div class="scan-progress-text" style="color:#4ade80;">'
        f'✅ 掃描完成！共找到 {len(results)} 筆符合條件的股票</div>',
        unsafe_allow_html=True,
    )
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


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
    pct_arr   = "▲" if pct > 0 else "▼"
    sc        = s["score"]
    sc_color  = _score_color(sc)
    bar_color = _score_bar_color(sc)

    rt          = s.get("realtime_price")
    price_str   = f'{rt:.2f}' if rt else f'{s["close"]:.2f}'
    price_label = '<span style="color:#38bdf8;font-size:0.55rem;">即時</span>' if rt else \
                  '<span style="color:#475569;font-size:0.55rem;">收盤</span>'

    reasons = s.get("reasons", [])
    chips   = "".join(f'<span class="scan-sig-chip">{r}</span>' for r in reasons) \
              if reasons else '<span class="scan-sig-chip neutral">無明顯信號</span>'
    medal   = MEDALS[rank - 1] if rank <= 5 else f"#{rank}"

    # 評分明細
    breakdown = s.get("breakdown", {})
    bd_html = ""
    if breakdown:
        bd_items = "".join(
            f'<div style="display:flex;justify-content:space-between;padding:0.15rem 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.04);">'
            f'<span style="color:#94a3b8;font-size:0.62rem;">{label}</span>'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.62rem;'
            f'color:{"#4ade80" if pts > 0 else "#475569"};font-weight:700;">'
            f'{"+" if pts > 0 else ""}{pts}分</span>'
            f'</div>'
            for label, pts in breakdown.items()
        )
        bd_html = (
            f'<div style="background:rgba(0,0,0,0.2);border-radius:8px;'
            f'padding:0.4rem 0.6rem;margin-top:0.4rem;">'
            f'<div style="font-size:0.6rem;color:#475569;letter-spacing:0.08em;'
            f'text-transform:uppercase;margin-bottom:0.3rem;">評分明細（滿分100）</div>'
            f'{bd_items}'
            f'<div style="display:flex;justify-content:space-between;padding-top:0.3rem;">'
            f'<span style="font-size:0.65rem;font-weight:700;color:#e2e8f0;">總分</span>'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.65rem;'
            f'font-weight:700;color:{sc_color};">{sc} 分</span>'
            f'</div></div>'
        )

    st.markdown(
        f'<div class="scan-row" style="--sr:{sc_color};">'
        f'<div class="scan-row-rank">{medal}</div>'
        f'<div class="scan-row-info">'
        f'<div class="scan-row-name">{s["name"]}</div>'
        f'<div class="scan-row-code">{s["code"]} · '
        f'K{s["K"]:.0f} D{s["D"]:.0f} RSI{s["RSI"]:.0f}</div>'
        f'<div class="scan-row-signals">{chips}</div>'
        f'{bd_html}'
        f'</div>'
        f'<div class="scan-row-right">'
        f'<div class="scan-row-score" style="color:{sc_color};">{sc}分</div>'
        f'<div class="score-bar-wrap" style="width:56px;margin:3px 0 2px auto;">'
        f'<div class="score-bar-fill" style="--sw:{min(sc,100)}%;background:{bar_color};"></div></div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.85rem;'
        f'font-weight:700;color:#f1f5f9;text-align:right;">{price_str} {price_label}</div>'
        f'<div class="scan-row-pct" style="color:{pct_color};">{pct_arr} {abs(pct):.2f}%</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    if not in_watchlist:
        if st.button("＋ 加入關注", key=f"qadd_{s['code']}_{rank}", use_container_width=True):
            st.session_state.watchlist.append({"id": s["code"], "name": s["name"]})
            save_watchlist(st.session_state.watchlist)
            st.rerun()
    else:
        st.markdown(
            '<div style="font-size:0.65rem;color:#4ade80;text-align:center;'
            'padding:0.2rem 0;margin-bottom:0.35rem;">✓ 已在關注清單</div>',
            unsafe_allow_html=True,
        )


def render_scan_section():
    st.markdown(
        '<div class="scan-section">'
        '<div class="scan-header">'
        '<div><div class="scan-title">🔥 主流股<span>強勢掃描</span></div>'
        '<div class="scan-subtitle">全市場上市股 · MA趨勢＋新高＋量能＋漲幅 綜合評分</div></div>'
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
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        if st.session_state.scan_timestamp:
            total_cnt = len(st.session_state.scan_results or [])
            cached_cnt = len(st.session_state.get("scan_df_cache", {}))
            st.markdown(
                f'<div style="font-size:0.65rem;color:#475569;">'
                f'上次掃描：{st.session_state.scan_timestamp}　共 {total_cnt} 筆'
                f'　<span style="color:#334155;">快取 {cached_cnt} 支</span></div>',
                unsafe_allow_html=True,
            )
    with col2:
        do_scan = st.button("▶ 掃描", key="scan_btn", use_container_width=True)
    with col3:
        if st.button("🗑️ 清快取", key="scan_clear_btn", use_container_width=True):
            st.session_state.scan_df_cache  = {}
            st.session_state.scan_results   = None
            st.session_state.scan_timestamp = None
            st.rerun()

    if do_scan or st.session_state.scan_results is None:
        st.markdown(
            '<div style="font-size:0.7rem;color:#64748b;margin-bottom:0.4rem;">'
            '正在抓取全市場上市＋上櫃股票清單，逐一技術分析，找到符合條件即時顯示…</div>',
            unsafe_allow_html=True,
        )
        progress_bar     = st.progress(0)
        status_text      = st.empty()
        result_container = st.empty()   # 即時預覽區
        all_results      = run_market_scan_live(
            progress_bar, status_text, result_container, top_n=1800
        )
        result_container.empty()   # 掃描完後清掉預覽，改用正式分頁顯示
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

with st.expander("🔥 主流強勢股掃描（全市場上市股）", expanded=False):
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
