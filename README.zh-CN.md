[English README](README.md)

# 1% 生活宽松度 · 双重校正计算器

**公式**
Ease = (US/CN 1%门槛) × [ w_H·(Rent_CN/Rent_US) + (1-w_H)·(ExRent_CN/ExRent_US) ]

**目录结构**
```
wealth_ease_calc/
  ├─ data/
  │   ├─ cities.json           # 城市级指数：ex_rent, rent（纽约=100刻度）
  │   └─ thresholds.json       # 1%财富门槛预设（USD）
  ├─ model.py                  # 核心公式与函数
  ├─ cli.py                    # 命令行工具
  └─ app_streamlit.py          # Streamlit 小应用
```

## 本地使用

### 方式 A：命令行
```bash
cd wealth_ease_calc
python3 cli.py --cn Beijing Shanghai Shenzhen Guangzhou                --us "New York" "San Francisco" "San Jose" Boston                --w_h 0.25                --method KF                --cn_price 100 --fx 7.2                --out result.json
```

输出包括：门槛倍率 M、价格比、Ease 倍率，以及（如提供 cn_price）给出的“美国1%体感”等价价。

### 方式 B：Streamlit App
```bash
cd wealth_ease_calc
pip install streamlit
streamlit run app_streamlit.py
```
浏览器中选择城市、w_H 与门槛方法即可。

## 更新数据
- 编辑 `data/cities.json`：添加/修改城市及其 `ex_rent`（不含租）与 `rent` 指数。
- 编辑 `data/thresholds.json`：替换为你信任的 1% 门槛来源。  
- 指数是**无量纲**相对水平，建议保持纽约=100 的刻度以保证可比性。

## 注意
- 示例数据仅为演示；请用你认可的口径更新后再做政策或投资决策。
- 如需扩展到税费、教育、医疗、金融成本等，可在 `model.py` 增加更多维度与权重。
