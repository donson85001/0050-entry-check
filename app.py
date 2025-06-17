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

# 取得歷史資料（過去1年）
ticker = yf.Ticker("0050.TW")
data = ticker.history(period="1y", interval="1mo")[["Close"]].dropna()
data.rename(columns={"Close": "Price"}, inplace=True)

# 使用者輸入
st.subheader("📥 輸入資料")
latest_price = float(data["Price"].iloc[-1])
input_price = st.number_input("輸入目前 0050 價格", value=latest_price)
cash_total = st.number_input("可動用資金總額（元）", value=100000.0, step=10000.0)

# 替換最後一筆價格為使用者輸入價格
data = data.copy()
data.iloc[-1, data.columns.get_loc("Price")] = input_price

# 計算動能與波動
data["Momentum"] = data["Price"].pct_change(MOM_PERIOD)
data["Volatility"] = data["Price"].pct_change().rolling(VOL_PERIOD).std()

# 標準化 (丟掉NA以免錯誤)
data = data.dropna()
data["Mom_z"] = (data["Momentum"] - data["Momentum"].mean()) / data["Momentum"].std()
data["Vol_z"] = (data["Volatility"] - data["Volatility"].mean()) / data["Volatility"].std()
data["Weight"] = 1 / (1 + np.exp(-(data["Mom_z"] - data["Vol_z"])))

# 最新資料（包含你輸入價格計算出來的結果）
latest = data.iloc[-1]
weight = latest["Weight"]
investment_amount = weight * cash_total
cash_remaining = (1 - weight) * cash_total

# 顯示分析結果
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

# 顯示建議金額
st.subheader("💰 資金建議配置")
st.write(f"✅ 建議投入：`{investment_amount:,.0f}` 元")
st.write(f"💤 建議保留現金：`{cash_remaining:,.0f}` 元")

# 顯示歷史價格
st.subheader("📉 歷史價格走勢")
st.line_chart(data[["Price"]])
