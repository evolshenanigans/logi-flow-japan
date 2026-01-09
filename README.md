# 🚛 Logi-Flow Japan: Solving the 2024 Logistics Crisis
# 🚛 Logi-Flow Japan: 2024年物流問題の解決に向けた最適化システム

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://jjdnclzmej37trpzqzepol.streamlit.app/)

> **Click the badge above to launch the Live Demo / 上記のバッジをクリックしてデモをご覧ください**

## 📌 Overview / 概要
**Logi-Flow Japan** is a strategic logistics optimization engine designed to address the **"2024 Problem"** (strict overtime regulations for drivers in Japan).
It utilizes **Machine Learning (LightGBM)** for demand forecasting and **Constraint Programming (Google OR-Tools)** to generate legally compliant delivery routes.

**Logi-Flow Japan** は、「2024年問題」（ドライバーの時間外労働規制）に対応するために設計された物流最適化エンジンです。
**機械学習 (LightGBM)** による需要予測と、**数理最適化 (Google OR-Tools)** を用いた配送ルートの自動生成を組み合わせ、法的規制を遵守しつつ効率的な物流網を構築します。

## 🚀 Key Features / 主な機能

### 1. Demand Forecasting (需要予測)
* **Engine:** LightGBM (Gradient Boosting)
* **Logic:** Predicts cargo volume based on seasonal trends (Golden Week, Obon) and "Holiday Distance."
* **Impact:** Prevents understaffing during peak seasons.
* **エンジン:** LightGBM (勾配ブースティング)
* **ロジック:** 季節性（GW、お盆）や「祝日からの距離」等の特徴量を用い、貨物量を予測。
* **効果:** 繁忙期の人員不足を未然に防止。

### 2. Route Optimization (配送ルート最適化)
* **Engine:** Google OR-Tools
* **Constraint:** Strictly adheres to the **960-hour/year overtime cap** by limiting route distance.
* **Heijunka (Leveling):** Distributes workload evenly among drivers to prevent burnout.
* **エンジン:** Google OR-Tools
* **制約条件:** 年間960時間の残業規制を遵守するため、各ルートの走行距離を厳密に制限。
* **平準化:** 特定のドライバーへの負荷集中を防ぎ、労働環境を改善。

## 🛠 Tech Stack / 使用技術
* **Python:** 3.9
* **ML:** LightGBM, Scikit-learn
* **Optimization:** Google OR-Tools
* **Visualization:** Streamlit, Plotly
* **Data Format:** Parquet (Columnar storage for efficiency)

## 👨‍💻 Author / 著者
Josh
*Seeking Data Science opportunities in Japan.*
*日本でのデータサイエンス職を探しています。*
