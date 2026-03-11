import streamlit as st
import pandas as pd
st.title("Share of Voice Dashboard")
#below is mock data
df = pd.DataFrame(
    {
        "Brand": ["Nike", "Adidas", "Puma", "Under Armour"],
        "Share of Voice (%)": [42, 30, 18, 10],
    }
)
st.subheader("Table")
st.dataframe(df)
st.subheader("Bar Chart")
st.bar_chart(df.set_index("Brand"))