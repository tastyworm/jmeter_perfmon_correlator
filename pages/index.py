import streamlit as st
import os

st.set_page_config(page_title="Performance Analysis Tool", layout="wide", initial_sidebar_state="collapsed")

# Hide the left column which streamlit shows by default
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
# Remove any history of the session state - start over fresh
st.session_state.clear()

# Setup the uploaded_data directory
directory = 'uploaded_data/'
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)

# Header
header_left_column, header_center_column, header_right_column = st.columns([1,4,1])


# Center

left_column, center_column, right_column = st.columns([1,4,1])

with center_column:
    st.title("Performance Analysis Tool")
    st.caption("Welcome to the Performance Analysis Tool")
    st.caption("This tool is designed to help you analyse performance data from different sources.")
    with st.container(border=True):
        st.caption("This tool currently supports the following file types:")
        st.caption("* JMeter .jtl files")
        st.caption("* Perfmon .csv files")
        # st.caption("* Event Viewer .csv files")

with right_column:
    logo = st.container()
    logo.image("pages/images/perfanalysislogo.png", width=200)
    
    spacer = st.container(height=100, border=0)
    
st.divider()


# Footer
footer_left_column, footer_center_column, footer_right_column = st.columns([1,4,1])

if footer_right_column.button("Let's Begin!"):
    st.switch_page("pages/upload_jmeter.py")


