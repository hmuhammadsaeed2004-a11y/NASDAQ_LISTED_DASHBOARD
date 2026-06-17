"""
app.py
──────
Main Streamlit entry point for the NASDAQ Listed Securities Dashboard.

Run with:
    streamlit run app.py

Project structure:
    app.py        ← this file (layout + orchestration)
    filters.py    ← data loading, feature engineering, sidebar filters
    charts.py     ← all chart functions + export helpers
    data/
        1780492838799_nasdaq-listed__1_.csv
"""

import streamlit as st

# ── Page config (must be the very first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="NASDAQ Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local modules ─────────────────────────────────────────────────────────────
from filters import load_data, render_sidebar
from charts import (
    show_chart, fig_to_png, build_pdf_report, chart_pairplot,
    chart_security_type_pie,
    chart_entity_suffix_bar,
    chart_symbol_length_histogram,
    chart_listings_per_year_line,
    chart_scatter_symbol_vs_name,
    chart_boxplot_word_count,
    chart_heatmap_correlation,
    chart_area_cumulative_listings,
    chart_countplot_spac,
    chart_violin_symbol_length,
)

# ──────────────────────────────────────────────
# CUSTOM CSS  (dark navy + electric-blue accent)
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #0d1b3e 100%);
    border-right: 1px solid #1e3a6e;
}
[data-testid="stSidebar"] * { color: #c8d8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label { color: #7ba7d4 !important; }

.main { background: #080d1a; }
.block-container { padding-top: 1.5rem; }

.kpi-card {
    background: linear-gradient(135deg, #0d1b3e 0%, #122244 100%);
    border: 1px solid #1e3a6e;
    border-radius: 12px;
    padding: 18px 22px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,100,255,0.12);
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #38bdf8;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-label {
    font-size: 0.78rem;
    color: #7ba7d4;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #38bdf8;
    border-bottom: 2px solid #1e3a6e;
    padding-bottom: 6px;
    margin-bottom: 16px;
    margin-top: 10px;
}

.dash-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #e2eeff;
    letter-spacing: -0.5px;
}
.dash-sub {
    font-size: 0.9rem;
    color: #4f7aad;
    margin-top: 2px;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #0d1b3e, #122244);
    color: #38bdf8 !important;
    border: 1px solid #1e3a6e;
    border-radius: 8px;
    font-size: 0.78rem;
    padding: 4px 12px;
    margin-top: 6px;
    transition: all 0.2s ease;
}
.stDownloadButton > button:hover {
    border-color: #38bdf8;
    background: #122244;
    box-shadow: 0 0 10px rgba(56,189,248,0.25);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# DATA  +  SIDEBAR FILTERS
# ══════════════════════════════════════════════
df_raw = load_data()
df     = render_sidebar(df_raw)   # filtered DataFrame


# ══════════════════════════════════════════════
# HEADER  +  PDF PLACEHOLDER
# ══════════════════════════════════════════════
title_col, pdf_col = st.columns([4, 1])
with title_col:
    st.markdown('<div class="dash-title">📊 NASDAQ Listed Securities Dashboard</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="dash-sub">Exploratory Data Analysis · '
        'All charts respond to sidebar filters simultaneously</div>',
        unsafe_allow_html=True,
    )
with pdf_col:
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_placeholder = st.empty()   # filled after all figures are built

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════
k1, k2, k3, k4, k5 = st.columns(5)
kpi_data = [
    (k1, f"{len(df):,}",                           "Total Securities"),
    (k2, f"{df['Security_Type'].nunique()}",        "Security Types"),
    (k3, f"{df[df['Is_SPAC']=='SPAC'].shape[0]:,}", "SPACs"),
    (k4, f"{df['Symbol_Length'].mean():.1f}",       "Avg Symbol Len"),
    (k5, f"{df['Entity_Suffix'].nunique()}",         "Entity Types"),
]
for col, val, label in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Collect figures for the PDF (populated by show_chart calls below)
all_figures: list = []


# ══════════════════════════════════════════════
# ROW 1 — PIE  |  BAR
# ══════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">① Pie Chart — Security Type Distribution</div>',
                unsafe_allow_html=True)
    show_chart(chart_security_type_pie(df),
               "01_security_type_pie", "Security Type Distribution", all_figures)

with col2:
    st.markdown('<div class="section-header">④ Bar Chart — Top Entity Suffixes</div>',
                unsafe_allow_html=True)
    show_chart(chart_entity_suffix_bar(df),
               "04_entity_suffix_bar", "Top Entity Suffixes", all_figures)


# ══════════════════════════════════════════════
# ROW 2 — HISTOGRAM  |  LINE
# ══════════════════════════════════════════════
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-header">② Histogram — Symbol Length Distribution</div>',
                unsafe_allow_html=True)
    show_chart(chart_symbol_length_histogram(df),
               "02_symbol_length_histogram", "Symbol Length Distribution", all_figures)

with col4:
    st.markdown('<div class="section-header">③ Line Chart — Listings Per Year Trend</div>',
                unsafe_allow_html=True)
    show_chart(chart_listings_per_year_line(df),
               "03_listings_per_year_line", "Listings Per Year Trend", all_figures)


# ══════════════════════════════════════════════
# ROW 3 — SCATTER  |  BOX
# ══════════════════════════════════════════════
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-header">⑤ Scatter Plot — Symbol Length vs Name Word Count</div>',
                unsafe_allow_html=True)
    show_chart(chart_scatter_symbol_vs_name(df),
               "05_scatter_symbol_vs_name", "Symbol Length vs Name Word Count", all_figures)

with col6:
    st.markdown('<div class="section-header">⑥ Box Plot — Name Word Count by Security Type</div>',
                unsafe_allow_html=True)
    show_chart(chart_boxplot_word_count(df),
               "06_boxplot_word_count", "Name Word Count by Security Type", all_figures)


# ══════════════════════════════════════════════
# ROW 4 — HEATMAP  |  AREA
# ══════════════════════════════════════════════
col7, col8 = st.columns(2)

with col7:
    st.markdown('<div class="section-header">⑦ Heatmap — Feature Correlation Matrix</div>',
                unsafe_allow_html=True)
    show_chart(chart_heatmap_correlation(df),
               "07_heatmap_correlation", "Feature Correlation Matrix", all_figures)

with col8:
    st.markdown('<div class="section-header">⑧ Area Chart — Cumulative Listings Over Time</div>',
                unsafe_allow_html=True)
    show_chart(chart_area_cumulative_listings(df),
               "08_area_cumulative_listings", "Cumulative Listings Over Time", all_figures)


# ══════════════════════════════════════════════
# ROW 5 — COUNT PLOT  |  VIOLIN
# ══════════════════════════════════════════════
col9, col10 = st.columns(2)

with col9:
    st.markdown('<div class="section-header">⑨ Count Plot — SPAC vs Non-SPAC by Type</div>',
                unsafe_allow_html=True)
    show_chart(chart_countplot_spac(df),
               "09_countplot_spac", "SPAC vs Non-SPAC by Type", all_figures)

with col10:
    st.markdown('<div class="section-header">⑩ Violin Plot — Symbol Length by Security Type</div>',
                unsafe_allow_html=True)
    show_chart(chart_violin_symbol_length(df),
               "10_violin_symbol_length", "Symbol Length by Security Type", all_figures)


# ══════════════════════════════════════════════
# BONUS — PAIR PLOT
# ══════════════════════════════════════════════
with st.expander("🎁 Bonus — Pair Plot (Numerical Features)"):
    st.markdown('<div class="section-header">Bonus: Pair Plot</div>',
                unsafe_allow_html=True)
    g = chart_pairplot(df)
    st.pyplot(g.figure)

    pair_png = fig_to_png(g.figure)
    st.download_button(
        label="⬇ Download Pair Plot PNG",
        data=pair_png,
        file_name="bonus_pair_plot.png",
        mime="image/png",
        key="dl_pair_plot",
    )
    import matplotlib.pyplot as plt
    plt.close()


# ══════════════════════════════════════════════
# DATA TABLE  +  CSV DOWNLOAD
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown('<div class="section-header">📋 Filtered Data Table</div>',
            unsafe_allow_html=True)

show_cols = [
    "Symbol", "Security Name", "Security_Type", "Share_Class",
    "Entity_Suffix", "Is_SPAC", "Symbol_Length", "Name_Word_Count", "Listing_Year",
]
st.dataframe(df[show_cols].reset_index(drop=True),
             use_container_width=True, height=280)

csv_bytes = df[show_cols].to_csv(index=False).encode("utf-8")
dl_col1, _ = st.columns([1, 5])
with dl_col1:
    st.download_button(
        label="⬇ Download CSV",
        data=csv_bytes,
        file_name="nasdaq_filtered_data.csv",
        mime="text/csv",
        key="dl_csv",
    )

st.caption(
    f"Showing {len(df):,} of {len(df_raw):,} securities · "
    "Data: NASDAQ Listed Securities Dataset"
)


# ══════════════════════════════════════════════
# PDF REPORT  (now all figures are collected)
# ══════════════════════════════════════════════
pdf_bytes = build_pdf_report(all_figures)
with pdf_placeholder:
    st.download_button(
        label="⬇ Full PDF Report",
        data=pdf_bytes,
        file_name="nasdaq_dashboard_report.pdf",
        mime="application/pdf",
        key="dl_pdf",
    )
