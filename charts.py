"""
charts.py
─────────
All chart-rendering functions for the NASDAQ Dashboard.
Each function accepts a filtered DataFrame and returns a matplotlib Figure.
Theme helpers and the PNG/PDF export utilities are also defined here.
"""

import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages

from filters import PALETTE, BG, BG2, GRID, TEXT


# ──────────────────────────────────────────────
# THEME HELPER
# ──────────────────────────────────────────────
def apply_dark_theme(fig, ax_or_axes):
    """Apply the shared dark navy theme to a figure and its axes."""
    fig.patch.set_facecolor(BG2)
    axes = ax_or_axes if isinstance(ax_or_axes, (list, np.ndarray)) else [ax_or_axes]
    for ax in np.array(axes).flatten():
        ax.set_facecolor(BG2)
        ax.tick_params(colors=TEXT, labelsize=9)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        if ax.get_title():
            ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)
        ax.grid(color=GRID, linestyle="--", linewidth=0.5, alpha=0.7)


# ──────────────────────────────────────────────
# EXPORT HELPERS
# ──────────────────────────────────────────────
def fig_to_png(fig) -> bytes:
    """Serialize a matplotlib Figure to PNG bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()


def build_pdf_report(figures_list: list) -> bytes:
    """
    Render all (title, fig) pairs into a single multi-page PDF.
    Two charts per page; includes a cover page.
    """
    buf = io.BytesIO()
    with PdfPages(buf) as pdf:

        # ── Cover page ────────────────────────
        fig_cover, ax_cover = plt.subplots(figsize=(11, 8.5))
        fig_cover.patch.set_facecolor(BG)
        ax_cover.set_facecolor(BG)
        ax_cover.axis("off")
        for text, y, size, color in [
            ("NASDAQ Listed Securities",           0.65, 28, "#e2eeff"),
            ("Exploratory Data Analysis Dashboard",0.55, 16, "#38bdf8"),
            ("Course: Exploratory Data Analysis",  0.42, 12, "#7ba7d4"),
            ("Instructor: Ali Hassan Sherazi",      0.36, 12, "#7ba7d4"),
            ("Submission: 05-June-2026",            0.30, 12, "#7ba7d4"),
        ]:
            ax_cover.text(0.5, y, text, ha="center", va="center",
                          fontsize=size, fontweight="bold" if size > 12 else "normal",
                          color=color, transform=ax_cover.transAxes)
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
                src_fig.savefig(tmp, format="png", dpi=120, bbox_inches="tight",
                                facecolor=src_fig.get_facecolor())
                tmp.seek(0)
                img = mpimg.imread(tmp)
                ax_p.imshow(img)
                ax_p.axis("off")
                ax_p.set_title(chart_title, color=TEXT, fontsize=10,
                               fontweight="bold", pad=6)
                ax_p.set_facecolor(BG2)

            fig_page.tight_layout(pad=1.5)
            pdf.savefig(fig_page, bbox_inches="tight", facecolor=BG2)
            plt.close(fig_page)

    buf.seek(0)
    return buf.read()


# ──────────────────────────────────────────────
# STREAMLIT RENDER HELPER
# ──────────────────────────────────────────────
def show_chart(fig, filename_stem: str, chart_title: str, all_figures: list):
    """
    Display a chart in Streamlit, append it to all_figures for the PDF,
    and render a PNG download button.
    """
    all_figures.append((chart_title, fig))
    st.pyplot(fig)
    png_bytes = fig_to_png(fig)
    st.download_button(
        label="⬇ Download PNG",
        data=png_bytes,
        file_name=f"{filename_stem}.png",
        mime="image/png",
        key=f"dl_{filename_stem}",
    )
    plt.close(fig)


# ══════════════════════════════════════════════
# INDIVIDUAL CHART FUNCTIONS
# ══════════════════════════════════════════════

def chart_security_type_pie(df) -> plt.Figure:
    """① Pie Chart — Security Type Distribution"""
    type_counts = df["Security_Type"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    fig.patch.set_facecolor(BG2)
    wedges, texts, autotexts = ax.pie(
        type_counts.values,
        labels=None,
        autopct="%1.1f%%",
        colors=PALETTE[:len(type_counts)],
        startangle=140,
        wedgeprops=dict(edgecolor=BG, linewidth=1.5),
        pctdistance=0.82,
    )
    for at in autotexts:
        at.set_color(TEXT); at.set_fontsize(8)
    ax.legend(
        type_counts.index, loc="lower center", ncol=3, fontsize=7.5,
        facecolor=BG2, edgecolor=GRID, labelcolor=TEXT,
        bbox_to_anchor=(0.5, -0.12),
    )
    ax.set_title("Security Type Proportions", color=TEXT, fontsize=11,
                 fontweight="bold", pad=12)
    return fig


def chart_entity_suffix_bar(df) -> plt.Figure:
    """④ Horizontal Bar Chart — Top Entity Suffixes"""
    entity_counts = df["Entity_Suffix"].value_counts().head(8)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    apply_dark_theme(fig, ax)
    bars = ax.barh(
        entity_counts.index[::-1], entity_counts.values[::-1],
        color=PALETTE[:len(entity_counts)], edgecolor=BG, linewidth=0.8,
    )
    ax.bar_label(bars, fmt="%d", padding=4, color=TEXT, fontsize=8.5,
                 fontfamily="monospace")
    ax.set_xlabel("Count", color=TEXT)
    ax.set_title("Securities by Entity Suffix", color=TEXT, fontsize=11,
                 fontweight="bold")
    ax.invert_xaxis()
    return fig


def chart_symbol_length_histogram(df) -> plt.Figure:
    """② Histogram — Symbol Length Distribution"""
    max_len = int(df["Symbol_Length"].max())
    fig, ax = plt.subplots(figsize=(6, 4))
    apply_dark_theme(fig, ax)
    n, bins, patches = ax.hist(
        df["Symbol_Length"], bins=range(1, max_len + 2),
        color=PALETTE[0], edgecolor=BG, linewidth=0.8, alpha=0.9,
    )
    for i, patch in enumerate(patches):
        patch.set_facecolor(PALETTE[i % len(PALETTE)])
    ax.set_xlabel("Symbol Length (characters)", color=TEXT)
    ax.set_ylabel("Frequency", color=TEXT)
    ax.set_title("Distribution of Ticker Symbol Lengths", color=TEXT,
                 fontsize=11, fontweight="bold")
    return fig


def chart_listings_per_year_line(df) -> plt.Figure:
    """③ Line Chart — Listings Per Year Trend"""
    yearly = df.groupby("Listing_Year").size().reset_index(name="Count")
    fig, ax = plt.subplots(figsize=(6, 4))
    apply_dark_theme(fig, ax)
    ax.plot(
        yearly["Listing_Year"], yearly["Count"],
        color=PALETTE[1], linewidth=2.2,
        marker="o", markersize=4, markerfacecolor=PALETTE[2],
    )
    ax.fill_between(yearly["Listing_Year"], yearly["Count"],
                    alpha=0.15, color=PALETTE[1])
    ax.set_xlabel("Listing Year", color=TEXT)
    ax.set_ylabel("Number of Securities", color=TEXT)
    ax.set_title("Securities Listed Per Year (Simulated)", color=TEXT,
                 fontsize=11, fontweight="bold")
    return fig


def chart_scatter_symbol_vs_name(df) -> plt.Figure:
    """⑤ Scatter Plot — Symbol Length vs Name Word Count"""
    sample = df.sample(min(800, len(df)), random_state=42)
    color_map = {
        t: PALETTE[i % len(PALETTE)]
        for i, t in enumerate(df["Security_Type"].unique())
    }
    colors = sample["Security_Type"].map(color_map)
    fig, ax = plt.subplots(figsize=(6, 4))
    apply_dark_theme(fig, ax)
    ax.scatter(sample["Symbol_Length"], sample["Name_Word_Count"],
               c=colors, alpha=0.65, s=30, edgecolors="none")
    ax.set_xlabel("Symbol Length", color=TEXT)
    ax.set_ylabel("Name Word Count", color=TEXT)
    ax.set_title("Symbol Length vs Security Name Length", color=TEXT,
                 fontsize=11, fontweight="bold")
    handles = [mpatches.Patch(color=color_map[t], label=t) for t in color_map]
    ax.legend(handles=handles, fontsize=6.5, facecolor=BG2, edgecolor=GRID,
              labelcolor=TEXT, loc="upper right", ncol=2)
    return fig


def chart_boxplot_word_count(df) -> plt.Figure:
    """⑥ Box Plot — Name Word Count by Security Type"""
    top_types = df["Security_Type"].value_counts().head(6).index.tolist()
    box_df    = df[df["Security_Type"].isin(top_types)]
    groups    = [
        box_df[box_df["Security_Type"] == t]["Name_Word_Count"].values
        for t in top_types
    ]
    fig, ax = plt.subplots(figsize=(6, 4))
    apply_dark_theme(fig, ax)
    bp = ax.boxplot(
        groups, patch_artist=True, notch=False,
        medianprops=dict(color="#facc15", linewidth=2),
        whiskerprops=dict(color=TEXT),
        capprops=dict(color=TEXT),
        flierprops=dict(marker="o", markerfacecolor=PALETTE[4],
                        markersize=3, alpha=0.5),
    )
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color); patch.set_alpha(0.75)
    ax.set_xticks(range(1, len(top_types) + 1))
    ax.set_xticklabels(top_types, rotation=15, ha="right", fontsize=8, color=TEXT)
    ax.set_ylabel("Word Count in Security Name", color=TEXT)
    ax.set_title("Name Word Count by Security Type", color=TEXT,
                 fontsize=11, fontweight="bold")
    return fig


def chart_heatmap_correlation(df) -> plt.Figure:
    """⑦ Heatmap — Feature Correlation Matrix"""
    num_cols = ["Symbol_Length", "Name_Word_Count", "Sim_Market_Cap_B", "Listing_Year"]
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(6, 4.2))
    apply_dark_theme(fig, ax)
    sns.heatmap(
        corr, annot=True, fmt=".2f", ax=ax,
        cmap="Blues", linewidths=0.5, linecolor=BG,
        annot_kws={"size": 10, "color": TEXT},
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Correlation Matrix of Numerical Features", color=TEXT,
                 fontsize=11, fontweight="bold")
    ax.tick_params(colors=TEXT, labelsize=8)
    return fig


def chart_area_cumulative_listings(df) -> plt.Figure:
    """⑧ Area Chart — Cumulative Listings Over Time"""
    yearly2 = df.groupby("Listing_Year").size().reset_index(name="Count")
    yearly2["Cumulative"] = yearly2["Count"].cumsum()
    fig, ax = plt.subplots(figsize=(6, 4))
    apply_dark_theme(fig, ax)
    ax.fill_between(yearly2["Listing_Year"], yearly2["Cumulative"],
                    alpha=0.35, color=PALETTE[2])
    ax.plot(yearly2["Listing_Year"], yearly2["Cumulative"],
            color=PALETTE[2], linewidth=2.2)
    ax.set_xlabel("Year", color=TEXT)
    ax.set_ylabel("Cumulative Count", color=TEXT)
    ax.set_title("Cumulative NASDAQ Listings Over Time", color=TEXT,
                 fontsize=11, fontweight="bold")
    return fig


def chart_countplot_spac(df) -> plt.Figure:
    """⑨ Count Plot — SPAC vs Non-SPAC by Security Type"""
    top4     = df["Security_Type"].value_counts().head(5).index.tolist()
    count_df = df[df["Security_Type"].isin(top4)]
    fig, ax  = plt.subplots(figsize=(6, 4))
    apply_dark_theme(fig, ax)
    sns.countplot(
        data=count_df, x="Security_Type", hue="Is_SPAC", ax=ax,
        palette={"SPAC": PALETTE[0], "Non-SPAC": PALETTE[3]},
        edgecolor=BG, linewidth=0.5,
    )
    ax.set_xlabel("Security Type", color=TEXT)
    ax.set_ylabel("Count", color=TEXT)
    ax.set_title("SPAC vs Non-SPAC Count by Security Type", color=TEXT,
                 fontsize=11, fontweight="bold")
    ax.tick_params(colors=TEXT, labelsize=8)
    ax.legend(facecolor=BG2, edgecolor=GRID, labelcolor=TEXT, fontsize=8)
    plt.xticks(rotation=12)
    return fig


def chart_violin_symbol_length(df) -> plt.Figure:
    """⑩ Violin Plot — Symbol Length by Security Type"""
    viol_types = df["Security_Type"].value_counts().head(5).index.tolist()
    viol_df    = df[df["Security_Type"].isin(viol_types)]
    fig, ax    = plt.subplots(figsize=(6, 4))
    apply_dark_theme(fig, ax)
    parts = ax.violinplot(
        [viol_df[viol_df["Security_Type"] == t]["Symbol_Length"].values
         for t in viol_types],
        positions=range(len(viol_types)),
        showmedians=True, showextrema=True,
    )
    for i, body in enumerate(parts["bodies"]):
        body.set_facecolor(PALETTE[i % len(PALETTE)]); body.set_alpha(0.75)
    parts["cmedians"].set_color("#facc15")
    for key in ("cmaxes", "cmins", "cbars"):
        parts[key].set_color(TEXT)
    ax.set_xticks(range(len(viol_types)))
    ax.set_xticklabels(viol_types, rotation=12, ha="right", color=TEXT, fontsize=8)
    ax.set_ylabel("Symbol Length", color=TEXT)
    ax.set_title("Symbol Length Distribution by Security Type", color=TEXT,
                 fontsize=11, fontweight="bold")
    return fig


def chart_pairplot(df):
    """Bonus — Pair Plot (Numerical Features). Returns a seaborn PairGrid."""
    pair_df = df[["Symbol_Length", "Name_Word_Count", "Listing_Year",
                  "Security_Type"]].copy()
    pair_df = pair_df[
        pair_df["Security_Type"].isin(
            df["Security_Type"].value_counts().head(4).index
        )
    ]
    sample_pair = pair_df.sample(min(400, len(pair_df)), random_state=42)
    type_pal = {
        t: PALETTE[i]
        for i, t in enumerate(sample_pair["Security_Type"].unique())
    }
    g = sns.pairplot(
        sample_pair, hue="Security_Type", palette=type_pal,
        diag_kind="kde",
        plot_kws=dict(alpha=0.5, s=18, edgecolor="none"),
        diag_kws=dict(fill=True, alpha=0.6),
    )
    g.figure.patch.set_facecolor(BG2)
    for ax_r in g.axes.flatten():
        if ax_r:
            ax_r.set_facecolor(BG2)
            ax_r.tick_params(colors=TEXT, labelsize=7)
            for spine in ax_r.spines.values():
                spine.set_edgecolor(GRID)
    return g
