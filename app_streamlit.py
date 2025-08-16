
import json
import streamlit as st
from model import (
    load_cities, load_thresholds, Thresholds, get_threshold_multiplier,
    composite_price_ratio, ease_multiplier, equivalent_price
)

st.set_page_config(page_title="1% Ease Calculator", layout="centered")

st.title("1% 生活宽松度 · 双重校正计算器")

cities = load_cities("data/cities.json")
ths = load_thresholds("data/thresholds.json")["presets"]

st.markdown("选择城市组合与方法，得到『财富门槛 × 价格水平』双重校正后的**生活宽松度倍率**。")

tab1, tab2 = st.tabs(["计算", "数据与说明"])

with tab1:
    cn_all = list(cities["CN"].keys())
    us_all = list(cities["US"].keys())

    default_cn = cities.get("clusters", {}).get("CN_Tier1", [])
    default_us = cities.get("clusters", {}).get("US_1pct_metros", [])

    cn_sel = st.multiselect("中国城市", options=cn_all, default=default_cn)
    us_sel = st.multiselect("美国城市", options=us_all, default=default_us)

    w_h = st.slider("住房权重 w_H", min_value=0.0, max_value=1.0, value=0.25, step=0.05)

    method = st.selectbox("门槛方法", options=["KF","SCF_LOW","SCF_HIGH","CUSTOM"], index=0)

    if method == "CUSTOM":
        us_thr = st.number_input("US 1% 门槛（USD）", min_value=0.0, value=5800000.0, step=10000.0, format="%.2f")
        cn_thr = st.number_input("CN 1% 门槛（USD）", min_value=0.0, value=1074000.0, step=1000.0, format="%.2f")
    else:
        preset = ths[method]
        us_thr, cn_thr = float(preset["US"]), float(preset["CN"])

    fx = st.number_input("汇率（CNY per USD，可选）", min_value=0.0, value=0.0, step=0.01, format="%.2f")
    cn_price = st.number_input("中国物价（例如一顿午餐，CNY，可选）", min_value=0.0, value=0.0, step=1.0, format="%.2f")

    run = st.button("计算")

    if run:
        if not cn_sel or not us_sel:
            st.error("请至少选择一个中国城市和一个美国城市。")
        else:
            try:
                M = get_threshold_multiplier(Thresholds(US=us_thr, CN=cn_thr))
                pr = composite_price_ratio(cities, cn_sel, us_sel, w_h)
                ease = ease_multiplier(M, pr)
                st.success("计算完成")
                st.write({
                    "threshold_multiplier_M": M,
                    "price_ratio": pr,
                    "ease_multiplier": ease
                })
                if cn_price > 0:
                    eq = equivalent_price(cn_price, ease, fx if fx>0 else None)
                    st.write({"equivalent_price": eq})
            except Exception as e:
                st.error(str(e))

with tab2:
    st.subheader("说明")
    st.markdown("""
- **阐释**：Ease = (US/CN 1%门槛) × [w_H·(Rent_CN/Rent_US) + (1-w_H)·(ExRent_CN/ExRent_US)]
- **指数刻度**：城市指数采用与纽约=100 同刻度的相对指数（Numbeo风格）。
- **数据**：项目自带示例值，建议根据你最新口径更新 `data/cities.json` 与 `data/thresholds.json`。
- **建议**：若关注家庭层面的教育/医疗/税费，请进一步扩展篮子与权重。
""")
