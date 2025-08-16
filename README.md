[中文说明](README.zh-CN.md)

# 1% Ease Calculator — Dual-Adjusted Cost-of-Living & Wealth Threshold Model

This repository implements a small, reproducible calculator to compare *lived affordability*
for households at the **top 1% wealth bracket** in **China** vs **the United States**.

The model applies a **two-step adjustment**:
1) **Wealth threshold multiplier** `M = US_1%_threshold / CN_1%_threshold`  
2) **Price-level ratio** that blends **housing (rent)** and **non-housing (ex-rent)** city indices:
	a. Choose any set of cities in CN and US (indices are on a common scale, NYC = 100)
	b. Pick a housing weight `w_H` in [0, 1]

**Ease Multiplier (core result):**

```
Ease = (US/CN 1% wealth threshold)
     × [ w_H · (Rent_CN / Rent_US) + (1 - w_H) · (ExRent_CN / ExRent_US) ]
```

Interpretation: `Ease > 1` ⇒ the US 1% has more “room” (after local prices) than the CN 1% for the selected city mix and `w_H`; `Ease < 1` ⇒ the reverse.

> **Important**: Indices are **relative** (unitless). Replace the bundled demo values with your preferred sources before using the results for analysis or decisions.

---

## Repository Layout

```
wealth_ease_calc/
├─ data/
│  ├─ cities.json        # City-level indices: {ex_rent, rent}; common scale (NYC = 100)
│  └─ thresholds.json    # Wealth thresholds for 1% (USD)
├─ model.py              # Core formulae and helpers
├─ cli.py                # Command-line interface
└─ app_streamlit.py      # Streamlit app for interactive use
```

---

## Quick Start

### A) Command Line
```bash
cd wealth_ease_calc
python3 cli.py \
  --cn Beijing Shanghai Shenzhen Guangzhou \
  --us "New York" "San Francisco" "San Jose" Boston \
  --w_h 0.25 \
  --method KF \
  --cn_price 100 --fx 7.2 \
  --out result.json
```
**Outputs** include:
- `threshold_multiplier_M`  — US/CN 1% wealth threshold ratio
- `price_ratio`             — blended price ratio using rent & ex-rent
- `ease_multiplier`         — two-step adjusted “lived affordability” multiplier
- `equivalent_price`        — optional: a CN price converted into the “US-1% feel” price

### B) Streamlit App
```bash
cd wealth_ease_calc
pip install streamlit
streamlit run app_streamlit.py
```
Select CN/US cities, choose `w_H`, and switch the wealth threshold method (KF / SCF / CUSTOM).

---

## Configuration

- **Update city indices** in `data/cities.json`. Values are relative indices on the NYC=100 scale
  (Numbeo-style). Feel free to add cities or clusters.
- **Update 1% wealth thresholds** in `data/thresholds.json` using your preferred sources:
  - `KF`  — Knight Frank (e.g., US ≈ 5.8M; CN ≈ 1.074M USD)
  - `SCF` — Commonly cited US 1% thresholds from Fed/SCF-based estimates (e.g., 11.6–13.7M USD)
  - `CUSTOM` — Supply your own values via CLI / Streamlit

---

## Example: From a CN Price to a “US-1% Feel” Price

Given a CN price `P_CN` (e.g., a lunch at 100 CNY):

```
P_equiv = P_CN × Ease
```

Ease depends on your chosen city sets, `w_H`, and the wealth-threshold method.

---

## Notes & Caveats

- **Indices are demo values** and should be replaced before any policy or investment use.
- **Numbeo-style city indices** are crowdsourced; they work best for *relative* comparisons under a
  consistent source and scale. For stronger grounding, consider combining **ICP (AIC-PPP)** at the
  national level with **US BEA RPP** for regional price parities.
- Not included yet: taxes, education/healthcare costs, and financing costs. You can extend
  `model.py` to incorporate them with additional weights.

---
