import streamlit as st
from tracking.perplexity_client import query_perplexity

st.title("Perplexity Client Demo")

prompt = st.text_input("Ask a question")

if st.button("Run Query"):
    if prompt.strip():
        result = query_perplexity(prompt)

        if "error" in result:
            st.error(result["error"])
        else:
            try:
                st.write(result["choices"][0]["message"]["content"])
            except Exception:
                st.json(result)
    else:
        st.warning("Enter a question first.")