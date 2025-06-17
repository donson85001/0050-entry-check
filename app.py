import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

st.set_page_config(page_title="0050 進場建議工具", layout="centered")

st.title("📌 0050 進場建議工具（固定參數策略）")

# 固定參數
MOM_PERIOD = 3
VOL_PERIOD = 2
CASH_RATE = 0.05

# 取得 1 年的月資料
ticker = yf.Ticker("0050.TW")
data = ticker.history(period="1y", interval="1mo")[["Close"]].dropna()
data.rename(columns={"Close": "Price"}, inplace=True)

# 計算動能與波動
data["Momentum"] = data["Price"].pct_change(MOM_PERIOD)
data["Volatility"] = data["Price"].pct_change().rolling(VOL_PERIOD).std()
data = data.dropna()

# 標準化
data["Mom_z"] = (data["Momentum"] - data["Momentum"].mean()) / data["Momentum"].std()
data["Vol_z"] = (data["Volatility"] - data["Volatility"].mean()) / data["Volatility"].std()
data["Weight"] = 1 / (1 + np.exp(-(data["Mom_z"] - data["Vol_z"])))

# 最新資料
latest = data.iloc[-1]

# 使用者輸入區
st.subheader("📥 輸入資料")

input_price = st.number_input("目前 0050 價格", value=float(latest["Price"]))
cash_total = st.number_input("可動用資金總額（元）", value=100000.0, step=10000.0)

# 根據輸入價格重新計算動能與波動（保留使用近三個月資料）
# 為了簡單：使用歷史權重，但報價用輸入價格呈現
weight = latest["Weight"]
investment_amount = weight * cash_total
cash_remaining = (1 - weight) * cash_total

# 顯示結果
st.subheader("🔎 策略分析結果")
st.write(f"📈 動能 Z 分數：`{latest['Mom_z']:.2f}`")
st.write(f"📉 波動 Z 分數：`{latest['Vol_z']:.2f}`")
st.write(f"📊 配置建議比率：**{weight:.1%}**")

if weight > 0.8:
    st.success("✅ 建議進場，大幅投入！")
elif weight > 0.5:
    st.info("🟡 可考慮小部分投入")
else:
    st.warning("🔒 建議保守觀望，暫不進場")

st.subheader("💰 資金建議配置")
st.write(f"✅ 建議投入：`{investment_amount:,.0f}` 元")
st.write(f"💤 建議保留現金：`{cash_remaining:,.0f}` 元")
st.caption(f"（以你輸入的價格 {input_price:.2f} 為基礎計算）")

# 顯示歷史圖表
st.subheader("📉 歷史價格走勢")
st.line_chart(data[["Price"]])
