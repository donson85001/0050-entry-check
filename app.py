import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime

st.title("📌 0050 進場建議工具（固定參數策略）")

# 固定參數
MOM_PERIOD = 3
VOL_PERIOD = 2
CASH_RATE = 0.05

# 取得歷史資料（0050.TW = 元大台灣50）
ticker = yf.Ticker("0050.TW")
data = ticker.history(period="1y", interval="1mo")[["Close"]].dropna()
data.rename(columns={"Close": "Price"}, inplace=True)

# 計算動能 & 波動
data["Momentum"] = data["Price"].pct_change(MOM_PERIOD)
data["Volatility"] = data["Price"].pct_change().rolling(VOL_PERIOD).std()
data["Mom_z"] = (data["Momentum"] - data["Momentum"].mean()) / data["Momentum"].std()
data["Vol_z"] = (data["Volatility"] - data["Volatility"].mean()) / data["Volatility"].std()
data["Weight"] = 1 / (1 + np.exp(-(data["Mom_z"] - data["Vol_z"])))

# 最新資料
latest = data.dropna().iloc[-1]
latest_price = latest["Price"]
weight = latest["Weight"]

# 使用者輸入目前價格（可選）
input_price = st.number_input("📥 輸入目前 0050 價格（可選）", value=float(latest_price))

# 結果
st.subheader("💡 策略結果")
st.write(f"動能 Z 分數：`{latest['Mom_z']:.2f}`")
st.write(f"波動 Z 分數：`{latest['Vol_z']:.2f}`")
st.write(f"➡️ 建議配置比例：`{weight:.1%}`")

# 判斷建議
if weight > 0.8:
    st.success("✅ 建議進場，大幅投入！")
elif weight > 0.5:
    st.info("🟡 可考慮小部分投入")
else:
    st.warning("🔒 目前不宜進場，保留現金較佳")

# 顯示歷史趨勢圖
st.line_chart(data[["Price"]])
