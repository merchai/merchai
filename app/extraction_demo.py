import streamlit as st
from src.extraction import extract_brands_from_text

st.title("Brand Extraction Demo")
st.caption("Extract brand mentions from any AI-generated text.")

text = st.text_area(
    "Paste AI response text here",
    value="Nike and Adidas are the most popular brands, followed by Puma and Under Armour.",
    height=200
)

if st.button("Extract Brands"):
    if not text.strip():
        st.error("Please enter some text.")
    else:
        brands = extract_brands_from_text(text)
        if brands:
            st.success(f"Found {len(brands)} brand mention(s)!")
            for brand in set(brands):
                st.markdown(f"- **{brand}**")
        else:
            st.warning("No brands found.")