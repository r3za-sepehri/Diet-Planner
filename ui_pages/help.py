import streamlit as st

def display_help_page():
    st.header("About & Program Guide", divider='rainbow')
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Error: README.md not found.")