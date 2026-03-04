import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="MerchAI",
    layout="wide",
)

st.title("Brand Visibility Metrics")
st.markdown(
    "Mock Share of Voice data for shoe brands extracted from AI answer-engine responses."
)

MOCK_SOV_DATA: list[dict[str, object]] = [
    {"brand": "Nike", "mentions": 42, "share_pct": 18.3},
    {"brand": "Adidas", "mentions": 35, "share_pct": 15.2},
    {"brand": "Hoka", "mentions": 30, "share_pct": 13.0},
    {"brand": "New Balance", "mentions": 27, "share_pct": 11.7},
    {"brand": "Brooks", "mentions": 22, "share_pct": 9.6},
    {"brand": "On Running", "mentions": 19, "share_pct": 8.3},
    {"brand": "Salomon", "mentions": 16, "share_pct": 7.0},
    {"brand": "Allbirds", "mentions": 12, "share_pct": 5.2},
    {"brand": "Common Projects", "mentions": 9, "share_pct": 3.9},
    {"brand": "Cole Haan", "mentions": 7, "share_pct": 3.0},
    {"brand": "Alden", "mentions": 6, "share_pct": 2.6},
    {"brand": "Crockett & Jones", "mentions": 5, "share_pct": 2.2},
]

df = pd.DataFrame(MOCK_SOV_DATA)

st.subheader("Share of Voice (%)")
st.bar_chart(df.set_index("brand")["share_pct"])

st.subheader("Detailed Metrics")
st.dataframe(
    df.rename(columns={
        "brand": "Brand",
        "mentions": "Mentions",
        "share_pct": "Share of Voice (%)",
    }),
    use_container_width=True,
    hide_index=True,
)
