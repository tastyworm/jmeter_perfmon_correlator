import streamlit as st
from config.config import set_page_config
import os


    
set_page_config()
   
   
with st.sidebar:
    st.title("Performance Analysis Tool")
    st.write("Welcome to the Performance Analysis Tool")
    st.write("This tool is designed to help you analyse performance data by correlating data from different sources and providing you with insights.")

    l, c, r = st.columns([1,1,2])
    with r:
        if st.button("Let's Begin!"):
            st.switch_page("pages/jmeter.py")
    

 
    
folderlist = ['chart_data', 'formatted_data', 'uploaded_data']

# If there are any files in any of the folders listed above, write a message saying that the files are being deleted
if any([len(os.listdir(folder)) > 0 for folder in folderlist]):
    st.switch_page("pages/cleanup.py")

# if the operating system is not windows, write a message saying that the tool is not supported
if os.name != 'nt':
    st.error("This tool is only supported on Windows operating systems.")
    st.stop()
    
