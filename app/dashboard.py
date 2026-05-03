"""
app/dashboard.py

MerchAI Phase 3 Dashboard — Brand Visibility Analytics
Built with Streamlit. Connects to SQLite for historical data.

Features:
- Run live pipeline for any category
- SOV bar chart with top brands
- Time-series tracking of brand visibility
- Competitor comparison across categories
- Multi-brand benchmarking
- Export results as CSV
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Make sure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

from src import db as database
from src.pipeline import DEFAULT_CATEGORIES, run as run_pipeline

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="MerchAI · Brand Visibility",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Mono', monospace;
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
        letter-spacing: -0.02em;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    .metric-card {
        background: #0f0f0f;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.5rem;
    }

    .metric-card .label {
        font-size: 0.7rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #f0f0f0;
        font-family: 'Syne', sans-serif;
    }

    .brand-pill {
        display: inline-block;
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 0.2rem 0.6rem;
        margin: 0.2rem;
        font-size: 0.8rem;
        color: #ccc;
    }

    .stButton > button {
        background: #e8ff47;
        color: #000;
        border: none;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
    }

    .stButton > button:hover {
        background: #d4eb30;
        color: #000;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Init DB
# ---------------------------------------------------------------------------

database.init_db()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚡ MerchAI")
    st.markdown("*Brand Visibility in AI Answers*")
    st.divider()

    st.markdown("### Run Pipeline")
    selected_category = st.selectbox(
        "Category",
        options=DEFAULT_CATEGORIES + ["custom"],
        format_func=lambda x: x.title() if x != "custom" else "✏️ Custom...",
    )

    if selected_category == "custom":
        selected_category = st.text_input("Enter category", placeholder="e.g. snapbacks")

    force_rerun = st.checkbox("Force rerun (ignore cache)", value=False)

    run_clicked = st.button("▶ Run Analysis", use_container_width=True)

    st.divider()
    st.markdown("### Batch Run")
    if st.button("Run All Default Categories", use_container_width=True):
        with st.spinner("Running all categories..."):
            from src.pipeline import run_all
            results = run_all(DEFAULT_CATEGORIES, skip_duplicates=not force_rerun)
            st.success(f"Done! Ran {len(results)} categories.")

    st.divider()
    st.caption("Data stored in `data/merchai.db`")

# ---------------------------------------------------------------------------
# Run pipeline on demand
# ---------------------------------------------------------------------------

if run_clicked and selected_category:
    with st.spinner(f"Querying AI for '{selected_category}'..."):
        result = run_pipeline(
            selected_category,
            skip_duplicates=not force_rerun,
        )

    if result.skipped:
        st.info(f"⚡ Using cached data for **{selected_category}** (ran within last 24h). Enable 'Force rerun' to refresh.")
    elif result.success:
        st.success(f"✅ Analysis complete — {len(set(result.extraction.brand_names))} brands found.")
    else:
        st.error(f"❌ Pipeline failed: {result.error}")

# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Share of Voice",
    "📈 Trends Over Time",
    "🔁 Brand Comparison",
    "📋 Raw Runs",
])

# ---- Tab 1: SOV snapshot ----
with tab1:
    st.markdown("## Share of Voice")
    st.caption("Most recent analysis per category")

    categories = database.get_categories()

    if not categories:
        st.info("No data yet. Run a pipeline from the sidebar to get started.")
    else:
        chosen = st.selectbox("Select category", categories, key="sov_cat")
        latest_sov = database.get_latest_sov(chosen)

        if not latest_sov:
            st.warning("No data for this category yet.")
        else:
            # Metrics row
            top_brand = list(latest_sov.keys())[0]
            top_sov = list(latest_sov.values())[0]
            total_brands = len(latest_sov)

            col1, col2, col3 = st.columns(3)
            col1.metric("Top Brand", top_brand)
            col2.metric("Top Brand SOV", f"{top_sov}%")
            col3.metric("Brands Tracked", total_brands)

            st.divider()

            # Bar chart
            df = pd.DataFrame(
                list(latest_sov.items()),
                columns=["Brand", "Share of Voice (%)"]
            ).head(15)

            st.markdown("### Top 15 Brands")
            st.bar_chart(df.set_index("Brand"), color="#e8ff47")

            # Table
            st.markdown("### Full Breakdown")
            st.dataframe(
                df.style.format({"Share of Voice (%)": "{:.1f}%"}),
                use_container_width=True,
            )

            # Export
            csv = df.to_csv(index=False)
            st.download_button(
                "⬇ Export CSV",
                data=csv,
                file_name=f"sov_{chosen.replace(' ', '_')}.csv",
                mime="text/csv",
            )

# ---- Tab 2: Trends over time ----
with tab2:
    st.markdown("## Brand Visibility Over Time")
    st.caption("Track how a brand's share of voice changes across runs")

    categories = database.get_categories()

    if not categories:
        st.info("No data yet. Run the pipeline a few times to see trends.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            trend_cat = st.selectbox("Category", categories, key="trend_cat")
        with col2:
            # Get brands seen in this category
            runs = database.get_runs(category=trend_cat)
            all_brands: set[str] = set()
            for r in runs:
                all_brands.update(r["sov"].keys())
            trend_brand = st.selectbox(
                "Brand",
                sorted(all_brands) if all_brands else ["—"],
                key="trend_brand",
            )

        if runs and trend_brand != "—":
            time_data = database.get_sov_over_time(trend_cat, trend_brand)
            if time_data:
                df_time = pd.DataFrame(time_data)
                df_time["created_at"] = pd.to_datetime(df_time["created_at"])
                df_time = df_time.set_index("created_at")
                df_time.columns = [f"{trend_brand} SOV (%)"]

                st.line_chart(df_time, color="#e8ff47")
                st.caption(f"{len(df_time)} data points across {len(df_time)} runs")
            else:
                st.info(f"No time-series data for {trend_brand} in {trend_cat} yet.")

# ---- Tab 3: Brand comparison across categories ----
with tab3:
    st.markdown("## Multi-Brand Benchmarking")
    st.caption("Compare brands head-to-head across categories")

    categories = database.get_categories()

    if len(categories) < 2:
        st.info("Run at least 2 categories to enable comparison.")
    else:
        # Get all brands across all categories
        all_brands_global: set[str] = set()
        sov_by_cat: dict[str, dict[str, float]] = {}
        for cat in categories:
            sov = database.get_latest_sov(cat)
            sov_by_cat[cat] = sov
            all_brands_global.update(sov.keys())

        selected_brands = st.multiselect(
            "Select brands to compare",
            sorted(all_brands_global),
            default=sorted(all_brands_global)[:5],
        )

        if selected_brands:
            # Build comparison matrix
            rows = []
            for cat in categories:
                row = {"Category": cat.title()}
                for brand in selected_brands:
                    row[brand] = sov_by_cat.get(cat, {}).get(brand, 0.0)
                rows.append(row)

            df_comp = pd.DataFrame(rows).set_index("Category")

            st.markdown("### SOV Heatmap")
            st.dataframe(
                df_comp.style
                    .format("{:.1f}%")
                    .background_gradient(cmap="YlOrRd", axis=None),
                use_container_width=True,
            )

            st.markdown("### Bar Comparison")
            st.bar_chart(df_comp, color=["#e8ff47", "#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"])

            # Export
            csv = df_comp.reset_index().to_csv(index=False)
            st.download_button(
                "⬇ Export Comparison CSV",
                data=csv,
                file_name="brand_comparison.csv",
                mime="text/csv",
            )

# ---- Tab 4: Raw runs log ----
with tab4:
    st.markdown("## Run History")
    st.caption("All pipeline runs stored in the database")

    categories = database.get_categories()
    filter_cat = st.selectbox(
        "Filter by category",
        ["All"] + categories,
        key="runs_cat",
    )

    runs = database.get_runs(
        category=filter_cat if filter_cat != "All" else None,
        limit=50,
    )

    if not runs:
        st.info("No runs yet.")
    else:
        rows = []
        for r in runs:
            top_brand = list(r["sov"].keys())[0] if r["sov"] else "—"
            top_sov = list(r["sov"].values())[0] if r["sov"] else 0
            rows.append({
                "ID": r["id"],
                "Category": r["category"].title(),
                "Top Brand": top_brand,
                "Top SOV (%)": top_sov,
                "Brands": r["brand_count"],
                "Mentions": r["mention_count"],
                "Status": "✅" if r["success"] else "❌",
                "Run At": r["created_at"][:19].replace("T", " "),
            })

        df_runs = pd.DataFrame(rows)
        st.dataframe(df_runs, use_container_width=True, hide_index=True)

        # Expandable raw response viewer
        if runs:
            st.divider()
            st.markdown("### Inspect a Run")
            run_id = st.number_input("Run ID", min_value=1, value=runs[0]["id"])
            matching = [r for r in runs if r["id"] == run_id]
            if matching:
                r = matching[0]
                with st.expander("Raw LLM Response"):
                    st.text(r["raw_response"])
                with st.expander("SOV Data"):
                    st.json(r["sov"])