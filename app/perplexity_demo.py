import streamlit as st
import json

st.title("Perplexity Query Client")
st.caption("Send a prompt to an AI answer engine and get back a response.")

prompt = st.text_input(
    "Enter your prompt",
    value="What brands sell hoodies?"
)

if st.button("Query Perplexity"):
    if not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        with st.spinner("Querying Perplexity API..."):
            mock_response = {
                "model": "sonar-pro",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": f"Some of the most popular brands that sell hoodies include Nike, Adidas, Champion, Supreme, Under Armour, and Puma. Nike and Adidas dominate the market with their performance and lifestyle hoodies, while Champion is known for its affordable and classic styles. Supreme is popular in streetwear, and Under Armour focuses on athletic performance."
                    }
                }]
            }
            st.success("Response received!")
            st.subheader("Raw API Response")
            st.json(mock_response)