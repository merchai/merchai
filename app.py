import logging
import streamlit as st

from src.tracking.perplexity_client import query_perplexity

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

st.set_page_config(page_title="Perplexity Client", page_icon="🤖")

st.title("Perplexity Client")
st.write("Simple UI with retry logic.")

prompt = st.text_area("Prompt", height=180, placeholder="Ask something...")

if st.button("Send"):
    if not prompt.strip():
        st.error("Enter a prompt.")
    else:
        with st.spinner("Sending request..."):
            result = query_perplexity(prompt)

        if result.get("success") is False or "error" in result:
            st.error("Request failed")
            st.json(result)
        else:
            st.success("Request succeeded")

            try:
                answer = result["choices"][0]["message"]["content"]
                st.subheader("Answer")
                st.write(answer)
            except Exception:
                st.subheader("Raw Response")
                st.json(result)

st.caption("Retry logs appear in the terminal.")