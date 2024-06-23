import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title="Performance Analysis Tool", 
        layout="wide", 
        initial_sidebar_state="expanded")
    
    st.markdown(
        """
    <style>
        [data-testid="stSidebarNav"] {
            display: none
        }
        .very-small-font {
        font-size: 12px !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )