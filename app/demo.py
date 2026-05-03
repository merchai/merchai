"""
app/demo.py

MerchAI Demo Dashboard — runs entirely on mock data, no API key needed.
Deploy to Streamlit Cloud for free at streamlit.io/cloud.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="MerchAI · Brand Visibility Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.02em; }
    .block-container { padding-top: 2rem; max-width: 1200px; }
    .stButton > button {
        background: #c8ff57; color: #000; border: none;
        font-family: 'Syne', sans-serif; font-weight: 700;
        border-radius: 6px; padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { background: #b4eb43; color: #000; }
    .demo-banner {
        background: #1a1a1a; border: 1px solid #c8ff57;
        border-radius: 8px; padding: 10px 16px;
        font-size: 13px; color: #c8ff57; margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

CATEGORIES = ["hoodies", "t-shirts", "sweatpants", "hats & caps", "varsity jackets", "collegiate merch"]

BRAND_UNIVERSE = {
    "hoodies":           {"Nike": 24.3, "Adidas": 18.1, "Champion": 14.2, "Supreme": 9.8, "Under Armour": 8.4, "Carhartt": 6.2, "Patagonia": 5.1, "Puma": 4.8, "NOBE": 4.6, "Hanes": 4.5},
    "t-shirts":          {"Nike": 28.1, "Hanes": 19.3, "Gildan": 14.8, "Adidas": 12.2, "Champion": 9.1, "Fruit of the Loom": 7.4, "Under Armour": 4.8, "NOBE": 2.4, "Puma": 1.9},
    "sweatpants":        {"Nike": 26.4, "Adidas": 22.3, "Champion": 17.1, "Under Armour": 11.2, "Puma": 8.4, "H&M": 5.8, "Uniqlo": 4.2, "NOBE": 2.8, "Gap": 1.8},
    "hats & caps":       {"Nike": 22.4, "New Balance": 18.9, "Adidas": 16.3, "Carhartt": 12.1, "Patagonia": 9.8, "Supreme": 7.2, "NOBE": 1.9, "Puma": 4.8, "Vans": 6.6},
    "varsity jackets":   {"Nike": 21.2, "Adidas": 17.8, "Champion": 22.1, "Letterman": 12.4, "Under Armour": 8.9, "Augusta": 6.3, "NOBE": 3.8, "Puma": 4.2, "Holloway": 3.3},
    "collegiate merch":  {"Champion": 28.3, "Nike": 19.4, "Adidas": 14.2, "Under Armour": 11.8, "Columbia": 8.1, "Fanatics": 6.4, "NOBE": 5.8, "Russell": 3.6, "Gear": 2.4},
}

def generate_trend(base: float, n: int = 8) -> list[float]:
    random.seed(42)
    vals = []
    current = base * 0.7
    for _ in range(n):
        current += random.uniform(-1.5, 2.5)
        current = max(0.5, min(current, base * 1.3))
        vals.append(round(current, 1))
    vals[-1] = base
    return vals

def generate_runs() -> list[dict]:
    runs = []
    now = datetime.utcnow()
    run_id = 20
    for i, cat in enumerate(CATEGORIES):
        for j in range(3):
            sov = BRAND_UNIVERSE[cat]
            top = list(sov.keys())[0]
            runs.append({
                "id": run_id,
                "category": cat,
                "top_brand": top,
                "top_sov": list(sov.values())[0],
                "brand_count": len(sov),
                "mention_count": random.randint(40, 90),
                "success": j != 1 or i != 5,
                "run_at": (now - timedelta(hours=i*8 + j*2)).strftime("%Y-%m-%d %H:%M"),
            })
            run_id -= 1
    return runs

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚡ MerchAI")
    st.markdown("*Brand Visibility in AI Answers*")
    st.divider()

    st.markdown("""
    <div style="background:#111;border:1px solid #c8ff57;border-radius:6px;padding:8px 12px;font-size:11px;color:#c8ff57;">
        🟡 Demo mode — mock data only
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### Simulate a Run")
    selected_category = st.selectbox("Category", CATEGORIES, format_func=str.title)

    if st.button("▶ Simulate Analysis", use_container_width=True):
        with st.spinner(f"Querying AI for '{selected_category}'..."):
            import time; time.sleep(1.5)
        st.success(f"✅ Found {len(BRAND_UNIVERSE[selected_category])} brands.")

    st.divider()
    st.caption("Production version connects to Perplexity API + SQLite.")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Share of Voice",
    "📈 Trends Over Time",
    "🔁 Brand Comparison",
    "📋 Run History",
])

# ---- Tab 1: SOV ----
with tab1:
    st.markdown("## Share of Voice")
    st.caption("Latest snapshot per category — mock data")

    chosen_cat = st.selectbox("Category", CATEGORIES, format_func=str.title, key="sov_cat")
    sov = BRAND_UNIVERSE[chosen_cat]
    top_brand = list(sov.keys())[0]
    top_pct = list(sov.values())[0]
    nobe_pct = sov.get("NOBE", 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Top Brand", top_brand)
    col2.metric("Top Brand SOV", f"{top_pct}%")
    col3.metric("NOBE SOV", f"{nobe_pct}%")
    col4.metric("Brands Tracked", len(sov))

    st.divider()

    df = pd.DataFrame(list(sov.items()), columns=["Brand", "Share of Voice (%)"])

    st.markdown("### Top Brands")

    colors = ["#c8ff57" if b == "NOBE" else "#9b8aff" for b in df["Brand"]]
    st.bar_chart(df.set_index("Brand"), color="#9b8aff")

    st.markdown("### Full Breakdown")
    st.dataframe(
        df.style.format({"Share of Voice (%)": "{:.1f}%"}),
        use_container_width=True,
        hide_index=True,
    )

    csv = df.to_csv(index=False)
    st.download_button("⬇ Export CSV", data=csv,
                       file_name=f"sov_{chosen_cat.replace(' ','_')}.csv",
                       mime="text/csv")

# ---- Tab 2: Trends ----
with tab2:
    st.markdown("## Brand Visibility Over Time")
    st.caption("Simulated trend across 8 pipeline runs")

    col1, col2 = st.columns(2)
    with col1:
        trend_cat = st.selectbox("Category", CATEGORIES, format_func=str.title, key="trend_cat")
    with col2:
        brands_in_cat = list(BRAND_UNIVERSE[trend_cat].keys())
        trend_brand = st.selectbox("Brand", brands_in_cat, key="trend_brand")

    base_sov = BRAND_UNIVERSE[trend_cat][trend_brand]
    trend_vals = generate_trend(base_sov)

    now = datetime.utcnow()
    dates = [(now - timedelta(days=7-i)).strftime("%b %d") for i in range(8)]

    df_trend = pd.DataFrame({
        "Date": dates,
        f"{trend_brand} SOV (%)": trend_vals,
    }).set_index("Date")

    st.line_chart(df_trend, color="#c8ff57")
    st.caption(f"8 simulated data points · Latest: {trend_vals[-1]}%")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current SOV", f"{trend_vals[-1]}%")
    col2.metric("Peak SOV", f"{max(trend_vals)}%")
    col3.metric("Change (7d)", f"{round(trend_vals[-1] - trend_vals[0], 1):+}%")

# ---- Tab 3: Comparison ----
with tab3:
    st.markdown("## Multi-Brand Benchmarking")
    st.caption("Compare brands across all categories")

    all_brands: set[str] = set()
    for sov_data in BRAND_UNIVERSE.values():
        all_brands.update(sov_data.keys())

    selected_brands = st.multiselect(
        "Select brands to compare",
        sorted(all_brands),
        default=["Nike", "Adidas", "Champion", "NOBE"],
    )

    if selected_brands:
        rows = []
        for cat in CATEGORIES:
            row = {"Category": cat.title()}
            for brand in selected_brands:
                row[brand] = BRAND_UNIVERSE[cat].get(brand, 0.0)
            rows.append(row)

        df_comp = pd.DataFrame(rows).set_index("Category")

        st.markdown("### SOV Heatmap")
        st.dataframe(
            df_comp.style.format("{:.1f}%"),
            use_container_width=True,
        )

        st.markdown("### Bar Comparison")
        st.bar_chart(df_comp)

        csv = df_comp.reset_index().to_csv(index=False)
        st.download_button("⬇ Export CSV", data=csv,
                           file_name="brand_comparison.csv", mime="text/csv")
    else:
        st.info("Select at least one brand above.")

# ---- Tab 4: Run history ----
with tab4:
    st.markdown("## Run History")
    st.caption("Simulated pipeline run log")

    runs = generate_runs()

    filter_cat = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="runs_filter")
    if filter_cat != "All":
        runs = [r for r in runs if r["category"] == filter_cat]

    rows = []
    for r in runs:
        rows.append({
            "ID": f"#{r['id']}",
            "Category": r["category"].title(),
            "Top Brand": r["top_brand"],
            "Top SOV (%)": r["top_sov"],
            "Brands": r["brand_count"],
            "Mentions": r["mention_count"],
            "Status": "✅ ok" if r["success"] else "❌ error",
            "Run At": r["run_at"],
        })

    df_runs = pd.DataFrame(rows)
    st.dataframe(df_runs, use_container_width=True, hide_index=True)