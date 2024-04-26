import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st
import os

cache_dir = os.getenv('YFINANCE_CACHE_DIR', '/tmp/yfinance_cache')
yf.cache_path = cache_dir


st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAFA+α株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("## 表示日数選択")

days = st.sidebar.slider('日数', 1, 90, 30)

st.write(f"### 過去{days}日間のGAFA+α株価")

@st.cache_data
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try: 
    st.sidebar.write("## 株価の範囲指定")
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0, 600, (50, 500)
    )

    tickers = {
        'apple': 'AAPL',
        'meta platforms': 'META',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN',
        'tesla': 'TSLA',
        'nvidia': 'NVDA'
    }
    df = get_data(days, tickers)

    trend = {}
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period='5d')  # 直近5日間のデータを取得
        trend[company] = "上昇" if hist['Close'].iloc[-1] > hist['Close'].iloc[0] else "下降"

    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['google', 'amazon', 'meta platforms', 'apple','tesla','nvidia']
    )

    if not companies:
        st.error('少なくとも1社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価 (USD)", data.sort_index())
        st.sidebar.write("### 直近のトレンド", pd.Series(trend, index=trend.keys()).loc[companies])
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )
