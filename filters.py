"""
filters.py
──────────
Handles:
  • Data loading & feature engineering  (load_data)
  • Sidebar filter UI                   (render_sidebar)  → returns filtered DataFrame
  • Applying filters to the dataframe   (apply_filters)
  • PDF report builder                  (build_pdf_report)

Course: Exploratory Data Analysis | Instructor: Ali Hassan Sherazi
"""

import io
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

# ──────────────────────────────────────────────
# THEME CONSTANTS  (shared across modules)
# ──────────────────────────────────────────────
PALETTE = [
    "#38bdf8", "#818cf8", "#34d399", "#fb923c", "#f472b6",
    "#facc15", "#a78bfa", "#2dd4bf", "#f87171", "#4ade80",
]
BG   = "#080d1a"
BG2  = "#0d1b3e"
GRID = "#1e3a6e"
TEXT = "#c8d8f0"


# ══════════════════════════════════════════════
# DATA LOADING & FEATURE ENGINEERING
# ══════════════════════════════════════════════
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the NASDAQ CSV and engineer all derived columns."""
    import os
    _BASE = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(_BASE, "data", "1780492838799_nasdaq-listed__1_.csv"))
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Symbol", "Security Name"])
    df = df[df["Symbol"].str.strip() != ""]

    name = df["Security Name"]

    # ── Security Type ─────────────────────────
    def get_type(n: str) -> str:
        n_low = n.lower()
        if "etf" in n_low or "exchange-traded" in n_low:     return "ETF"
        if "common stock" in n_low:                          return "Common Stock"
        if "warrant" in n_low:                               return "Warrant"
        if "unit" in n_low:                                  return "Unit"
        if "right" in n_low:                                 return "Right"
        if "preferred" in n_low:                             return "Preferred"
        if "note" in n_low or "bond" in n_low:               return "Note/Bond"
        if "fund" in n_low:                                  return "Fund"
        if "trust" in n_low:                                 return "Trust"
        if "adr" in n_low or "depositary" in n_low:         return "ADR"
        if "reit" in n_low:                                  return "REIT"
        if "lp" in n_low or "limited partnership" in n_low: return "LP"
        return "Other"

    df["Security_Type"] = name.apply(get_type)

    # ── Share Class ───────────────────────────
    def get_class(n: str) -> str:
        for c in ["Class A", "Class B", "Class C",
                  "Series A", "Series B", "Series C", "Series D"]:
            if c in n:
                return c
        return "No Class"

    df["Share_Class"]   = name.apply(get_class)

    # ── Symbol features ───────────────────────
    df["Symbol_Length"] = df["Symbol"].str.len()
    df["Symbol_First"]  = df["Symbol"].str[0]

    # ── SPAC / International flags ────────────
    df["Is_SPAC"] = name.str.contains(
        r"acquisition|blank check|special purpose", case=False, na=False
    ).map({True: "SPAC", False: "Non-SPAC"})

    df["Is_International"] = name.str.contains(
        r"american depositary|depositary receipt|adr|foreign", case=False, na=False
    ).map({True: "International", False: "Domestic"})

    # ── Name word count ───────────────────────
    df["Name_Word_Count"] = name.str.split().apply(len)

    # ── Entity suffix ─────────────────────────
    def get_entity(n: str) -> str:
        n_up = n.upper()
        if " INC"  in n_up:                   return "Inc."
        if " CORP" in n_up:                   return "Corp."
        if " LTD"  in n_up:                   return "Ltd."
        if " LLC"  in n_up:                   return "LLC"
        if " LP"   in n_up:                   return "L.P."
        if " PLC"  in n_up:                   return "Plc"
        if " CO."  in n_up or " CO," in n_up: return "Co."
        if " GROUP" in n_up:                  return "Group"
        return "Other"

    df["Entity_Suffix"] = name.apply(get_entity)

    # ── Simulated columns ─────────────────────
    rng = np.random.RandomState(42)
    df["Sim_Market_Cap_B"] = (
        np.abs(rng.normal(10, 30, len(df))).clip(0.01, 3000).round(2)
    )
    df["Listing_Year"] = rng.randint(2000, 2025, len(df))

    return df


# ══════════════════════════════════════════════
# APPLY FILTERS  (pure function, no Streamlit)
# ══════════════════════════════════════════════
def apply_filters(df_raw: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Return a filtered copy of df_raw based on the sidebar selections dict."""
    df = df_raw.copy()

    if filters["search_text"]:
        q = filters["search_text"]
        mask = (
            df["Symbol"].str.contains(q, case=False, na=False) |
            df["Security Name"].str.contains(q, case=False, na=False)
        )
        df = df[mask]

    if filters["sel_types"]:
        df = df[df["Security_Type"].isin(filters["sel_types"])]

    if filters["sel_classes"]:
        df = df[df["Share_Class"].isin(filters["sel_classes"])]

    if filters["spac_opt"] != "All":
        df = df[df["Is_SPAC"] == filters["spac_opt"]]

    if filters["sel_entities"]:
        df = df[df["Entity_Suffix"].isin(filters["sel_entities"])]

    lo, hi = filters["sel_len"]
    df = df[(df["Symbol_Length"] >= lo) & (df["Symbol_Length"] <= hi)]

    y0, y1 = filters["sel_year"]
    df = df[(df["Listing_Year"] >= y0) & (df["Listing_Year"] <= y1)]

    return df


# ══════════════════════════════════════════════
# SIDEBAR FILTER UI
# Returns a filtered DataFrame so app.py can do:
#     df = render_sidebar(df_raw)
# ══════════════════════════════════════════════
def render_sidebar(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Render sidebar widgets, apply the chosen filters, and return the
    filtered DataFrame.

    Reset works by deleting every widget key from st.session_state so
    Streamlit re-initialises them to their default values on the next run.
    """
    WIDGET_KEYS = [
        "filter_search",
        "filter_types",
        "filter_classes",
        "filter_spac",
        "filter_entities",
        "filter_sym_len",
        "filter_year",
    ]

    with st.sidebar:
        st.markdown("## 🔍 Filters")
        st.markdown("---")

        # ── Reset button FIRST so state is cleared before widgets render ──
        if st.button("🔄 Reset All Filters"):
            for k in WIDGET_KEYS:
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown("---")

        # ── Search ────────────────────────────────────────────────────────
        search_text = st.text_input(
            "🔎 Search by Name / Symbol", "",
            key="filter_search",
        )

        # ── Security Type ─────────────────────────────────────────────────
        all_types = sorted(df_raw["Security_Type"].unique())
        sel_types = st.multiselect(
            "Security Type", all_types, default=all_types,
            key="filter_types",
        )

        # ── Share Class ───────────────────────────────────────────────────
        all_classes = sorted(df_raw["Share_Class"].unique())
        sel_classes = st.multiselect(
            "Share Class", all_classes, default=all_classes,
            key="filter_classes",
        )

        # ── SPAC ──────────────────────────────────────────────────────────
        spac_opt = st.selectbox(
            "SPAC / Non-SPAC", ["All", "SPAC", "Non-SPAC"],
            key="filter_spac",
        )

        # ── Entity Suffix ─────────────────────────────────────────────────
        all_entities = sorted(df_raw["Entity_Suffix"].unique())
        sel_entities = st.multiselect(
            "Entity Suffix", all_entities, default=all_entities,
            key="filter_entities",
        )

        # ── Symbol Length slider ──────────────────────────────────────────
        min_len = int(df_raw["Symbol_Length"].min())
        max_len = int(df_raw["Symbol_Length"].max())
        sel_len = st.slider(
            "Symbol Length", min_len, max_len, (min_len, max_len),
            key="filter_sym_len",
        )

        # ── Listing Year slider ───────────────────────────────────────────
        sel_year = st.slider(
            "Listing Year", 2000, 2024, (2000, 2024),
            key="filter_year",
        )

        st.markdown("---")
        st.markdown("**Course:** Exploratory Data Analysis")
        st.markdown("**Instructor:** Ali Hassan Sherazi")
        st.markdown("**Submission:** 05-June-2026")

    # ── Build filter dict and return filtered DataFrame ───────────────────
    filters = {
        "search_text": search_text,
        "sel_types":   sel_types,
        "sel_classes": sel_classes,
        "spac_opt":    spac_opt,
        "sel_entities":sel_entities,
        "sel_len":     sel_len,
        "sel_year":    sel_year,
        "max_len":     max_len,
    }
    return apply_filters(df_raw, filters)


# ══════════════════════════════════════════════
# PDF REPORT BUILDER
# ══════════════════════════════════════════════
def build_pdf_report(figures_list: list) -> bytes:
    """
    Render all collected (title, fig) tuples into a single multi-page PDF.
    Layout: styled cover page + 2 charts per page.
    """
    buf = io.BytesIO()

    with PdfPages(buf) as pdf:
        # ── Cover page ────────────────────────
        fig_cover, ax_cover = plt.subplots(figsize=(11, 8.5))
        fig_cover.patch.set_facecolor(BG)
        ax_cover.set_facecolor(BG)
        ax_cover.axis("off")
        for y, size, color, txt in [
            (0.65, 28, "#e2eeff", "NASDAQ Listed Securities"),
            (0.55, 16, "#38bdf8", "Exploratory Data Analysis Dashboard"),
            (0.42, 12, "#7ba7d4", "Course: Exploratory Data Analysis"),
            (0.36, 12, "#7ba7d4", "Instructor: Ali Hassan Sherazi"),
            (0.30, 12, "#7ba7d4", "Submission: 05-June-2026"),
        ]:
            ax_cover.text(
                0.5, y, txt, ha="center", va="center",
                fontsize=size,
                fontweight="bold" if size > 12 else "normal",
                color=color, transform=ax_cover.transAxes,
            )
        pdf.savefig(fig_cover, bbox_inches="tight", facecolor=BG)
        plt.close(fig_cover)

        # ── Chart pages (2 per page) ──────────
        for i in range(0, len(figures_list), 2):
            n_charts = min(2, len(figures_list) - i)
            fig_page, axes_page = plt.subplots(1, n_charts, figsize=(14, 6))
            fig_page.patch.set_facecolor(BG2)
            if n_charts == 1:
                axes_page = [axes_page]

            for j, ax_p in enumerate(axes_page):
                chart_title, src_fig = figures_list[i + j]
                tmp = io.BytesIO()
                src_fig.savefig(
                    tmp, format="png", dpi=120,
                    bbox_inches="tight",
                    facecolor=src_fig.get_facecolor(),
                )
                tmp.seek(0)
                img = mpimg.imread(tmp)
                ax_p.imshow(img)
                ax_p.axis("off")
                ax_p.set_title(
                    chart_title, color=TEXT,
                    fontsize=10, fontweight="bold", pad=6,
                )
                ax_p.set_facecolor(BG2)

            fig_page.tight_layout(pad=1.5)
            pdf.savefig(fig_page, bbox_inches="tight", facecolor=BG2)
            plt.close(fig_page)

    buf.seek(0)
    return buf.read()
