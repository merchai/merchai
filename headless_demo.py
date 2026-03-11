"""
Simple UI to demo the headless browser runner: enter a URL and view its raw HTML.

Run locally:
    python -m streamlit run headless_demo.py

Run in Docker:
    docker compose run --rm -p 8501:8501 -e PYTHONPATH=/app app \
        python -m streamlit run headless_demo.py --server.address=0.0.0.0
"""

import streamlit as st

from src.infra.headless_runner import get_page_html


st.set_page_config(page_title="Headless Runner Demo", layout="centered")
st.title("Headless Browser Runner Demo")
st.caption("Load a webpage and view its raw HTML (no API required).")

url = st.text_input("URL", value="https://example.com", placeholder="https://...")

if st.button("Get HTML"):
    if not url or not url.strip():
        st.error("Please enter a URL.")
    else:
        with st.spinner("Loading page..."):
            try:
                html = get_page_html(url.strip())
                st.success(f"Loaded {len(html):,} characters.")
                st.text_area("Raw HTML", html, height=400)
            except Exception as e:
                st.error(str(e))

