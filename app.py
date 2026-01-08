import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config (Tab Title)
st.set_page_config(page_title="Logi-Flow Japan", layout="wide")

# 2. The Language Dictionary (The "Foreigner's Edge")
translations = {
    'en': {
        'title': "Logi-Flow Japan: 2024 Optimization",
        'sidebar_title': "Settings",
        'lang_select': "Language / 言語",
        'kpi_cargo': "Total Cargo (Tons)",
        'kpi_cost': "Est. Fuel Cost (¥)",
        'tab_demand': "Demand Forecast",
        'tab_route': "Route Optimization"
    },
    'jp': {
        'title': "Logi-Flow Japan: 2024年物流最適化",
        'sidebar_title': "設定",
        'lang_select': "Language / 言語",
        'kpi_cargo': "総貨物量 (トン)",
        'kpi_cost': "推定燃料費 (円)",
        'tab_demand': "需要予測",
        'tab_route': "ルート最適化"
    }
}

# 3. Sidebar - Language Toggle
st.sidebar.title("Logi-Flow Settings")
lang = st.sidebar.radio(
    "Language / 言語",
    ('English', '日本語')
)

# Set the current code (en or jp)
current_lang = 'en' if lang == 'English' else 'jp'
t = translations[current_lang]

# 4. Main Title
st.title(t['title'])

# 5. Load Data (The Parquet file you made earlier!)
# We use @st.cache_data so it doesn't reload every time you click a button.
@st.cache_data
def load_data():
    return pd.read_parquet('data/features_engineered.parquet')

df = load_data()

# 6. KPI Row (Fake metrics for now, we will connect them later)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=t['kpi_cargo'], value=f"{df['Cargo_Weight_Tons'].sum():,.0f}")
with col2:
    st.metric(label=t['kpi_cost'], value="¥1,250,000", delta="-12% (Optimization)")
with col3:
    st.metric("Model Precision (MAE)", "0.85 Tons")

# 7. Visualization
st.subheader(t['tab_demand'])
st.write("Visualizing Cargo Weight by Prefecture (Simulated)")

# Simple Bar Chart
cargo_by_pref = df.groupby('Origin_Prefecture_Code')['Cargo_Weight_Tons'].sum().reset_index()
fig = px.bar(cargo_by_pref, x='Origin_Prefecture_Code', y='Cargo_Weight_Tons')
st.plotly_chart(fig)