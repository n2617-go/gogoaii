
# 穩定全市場掃描版（優化：批次抓取 + 防阻擋）
import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests

st.set_page_config(page_title="台股掃描穩定版", layout="centered")

st.title("🔥 台股全市場穩定掃描")

# ─────────────────────────────────────────
# 取得股票清單（上市+上櫃）
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_stock_list():
    urls = [
        ("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", "Code", "Name"),
        ("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes",
         "SecuritiesCompanyCode", "CompanyName")
    ]
    stocks = []
    for url, ck, nk in urls:
        try:
            data = requests.get(url, timeout=10).json()
            for d in data:
                code = str(d.get(ck, "")).strip()
                name = str(d.get(nk, "")).strip()
                if code.isdigit() and len(code) == 4:
                    stocks.append((code, name))
        except:
            pass
    return list(set(stocks))

# ─────────────────────────────────────────
# 批次抓資料（避免被封）
# ─────────────────────────────────────────
def fetch_batch(codes):
    tickers = [c + ".TW" for c in codes] + [c + ".TWO" for c in codes]
    try:
        df = yf.download(tickers, period="2mo", group_by="ticker", progress=False)
        return df
    except:
        return None

# ─────────────────────────────────────────
# 簡單評分
# ─────────────────────────────────────────
def score(df):
    try:
        close = df["Close"]
        ma5 = close.rolling(5).mean()
        ma20 = close.rolling(20).mean()
        if ma5.iloc[-1] > ma20.iloc[-1]:
            return 50
        return 10
    except:
        return 0

# ─────────────────────────────────────────
# 掃描
# ─────────────────────────────────────────
if st.button("開始掃描"):
    stocks = get_stock_list()
    st.write(f"📊 股票數量：{len(stocks)}")

    results = []
    progress = st.progress(0)

    batch_size = 50
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        codes = [c for c, _ in batch]

        data = fetch_batch(codes)
        if data is None:
            continue

        for code, name in batch:
            try:
                key = code + ".TW"
                if key not in data:
                    key = code + ".TWO"
                df = data[key].dropna()
                if len(df) < 20:
                    continue

                s = score(df)
                if s >= 50:
                    results.append((code, name, s))
            except:
                continue

        progress.progress((i + batch_size) / len(stocks))
        time.sleep(0.5)  # 防止被封

    results.sort(key=lambda x: x[2], reverse=True)

    st.success(f"完成！找到 {len(results)} 檔")

    for r in results[:50]:
        st.write(f"{r[1]} ({r[0]}) - 分數: {r[2]}")
