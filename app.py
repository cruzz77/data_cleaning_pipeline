import streamlit as st
import pandas as pd
import numpy as np
import time
import yfinance as yf

from cleaner import clean_price, reset_history

from signals import momentum, rolling_volatility, moving_average, vwap

st.set_page_config(page_title="QuantClean Pro", layout="wide")
st.title("Real-Time Market Data Cleaning Dashboard")

st.markdown("""
This dashboard supports two data modes:

**1️⃣ Upload CSV (local historical data)**  
**2️⃣ Real-Time Feed (Yahoo Finance)**  

Both modes apply project's pipeline:
- Rolling Z-score cleaning  
- Momentum  
- Rolling volatility  
- Moving averages  
- Volume-Weighted Average Price  
""")

st.sidebar.header("📁 Data Source")

data_mode = st.sidebar.radio(
    "Select mode:",
    ("Upload CSV", "Real-Time Feed (Yahoo Finance)")
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"],
    key="csv_uploader"
)

# Parameters for both modes
st.sidebar.markdown("### Parameters")
window_clean = st.sidebar.number_input("Z-score Window", 5, 200, 20)
z_threshold = st.sidebar.number_input("Z-score Threshold", 1.0, 10.0, 3.0)
mom_window = st.sidebar.number_input("Momentum Window", 1, 20, 3)
vol_window = st.sidebar.number_input("Volatility Window", 2, 200, 20)
ma_short = st.sidebar.number_input("MA Short Window", 1, 200, 5)
ma_long = st.sidebar.number_input("MA Long Window", 1, 200, 20)

#store params 
params = {
    "mom_window": int(mom_window),
    "vol_window": int(vol_window),
    "ma_short": int(ma_short),
    "ma_long": int(ma_long),
    "clean_window": int(window_clean),
    "clean_threshold": float(z_threshold)
}

# PROCESS FUNCTION
def process_df(df, params):

    reset_history()  # reset clean buffer each run

    cleaned, moms, vols, ma_s, ma_l, vwaps = [], [], [], [], [], []
    volumes = df["volume"].tolist() if "volume" in df else [0] * len(df)

    for i, raw in enumerate(df["price"]):
        # clean price
        cleaned_val = clean_price(
            float(raw),
            window=params["clean_window"],
            threshold=params["clean_threshold"]
        )
        cleaned.append(cleaned_val)

        # pipeline signals
        moms.append(momentum(cleaned, params["mom_window"]))
        vols.append(rolling_volatility(cleaned, params["vol_window"]))
        ma_s.append(moving_average(cleaned, params["ma_short"]))
        ma_l.append(moving_average(cleaned, params["ma_long"]))
        vwaps.append(vwap(cleaned, volumes[: i + 1], params["vol_window"]))

    df_out = df.copy()
    df_out["cleaned_price"] = cleaned
    df_out["momentum"] = moms
    df_out["volatility"] = vols
    df_out[f"ma_{params['ma_short']}"] = ma_s
    df_out[f"ma_{params['ma_long']}"] = ma_l
    df_out["vwap"] = vwaps
    return df_out


# MODE 1: UPLOAD CSV
if data_mode == "Upload CSV":

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        if "price" not in df.columns:
            st.error("CSV must contain a 'price' column.")
            st.stop()

        df_out = process_df(df, params)

        st.subheader("📊 Raw vs Cleaned Prices")
        st.line_chart(df_out[["price", "cleaned_price"]])

        st.subheader("📈 Signals")
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(df_out["momentum"].fillna(0))
        with col2:
            st.line_chart(df_out["volatility"].fillna(0))

        st.subheader("📄 Output Table")
        st.dataframe(df_out)

    else:
        st.info("Upload a CSV or use the Real-Time Feed option from the sidebar.")


# MODE 2: REAL-TIME FEED
elif data_mode == "Real-Time Feed (Yahoo Finance)":
    ticker = st.sidebar.text_input("Ticker symbol", "AAPL")
    refresh_speed = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)

    st.subheader(f"📡 Live Feed — {ticker}")

    if "live_prices" not in st.session_state:
        st.session_state.live_prices = []
        st.session_state.live_vols = []
        st.session_state.live_running = False

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("▶ Start Feed"):
            st.session_state.live_running = True

    with colB:
        if st.button("⏸ Pause Feed"):
            st.session_state.live_running = False

    with colC:
        if st.button("🔄 Reset Feed"):
            st.session_state.live_running = False
            st.session_state.live_prices = []
            st.session_state.live_vols = []
            reset_history()
            st.rerun()

    chart_area = st.empty()
    mom_area = st.empty()
    table_area = st.empty()

    if st.session_state.live_running:

        try:
            data = yf.Ticker(ticker).history(period="1d", interval="1m")
            price = float(data["Close"][-1])
            vol = int(data["Volume"][-1])
        except Exception as e:
            st.error(f"Could not fetch data for '{ticker}'. Error: {e}")
            st.stop()

        st.session_state.live_prices.append(price)
        st.session_state.live_vols.append(vol)

        df_live = pd.DataFrame({
            "time": list(range(len(st.session_state.live_prices))),
            "price": st.session_state.live_prices,
            "volume": st.session_state.live_vols
        })

        df_out = process_df(df_live, params)

        chart_area.line_chart(df_out[["price", "cleaned_price"]])
        mom_area.line_chart(df_out["momentum"].fillna(0))
        table_area.dataframe(df_out.tail(200))

        time.sleep(refresh_speed)
        st.rerun()

    else:
        st.info("Live feed paused. Click ▶ Start Feed to begin.")
