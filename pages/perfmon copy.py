import streamlit as st
import pandas as pd
import time
from config.config import set_page_config

set_page_config()

# Detail the minimum required columns for the Performance Monitor file
required_columns = []

with st.sidebar:
    st.title("Windows Performance Monitor Analysis")
    st.divider()
    # st.write("If you have a Performance Monitor file, you can upload it here have it correlated with other data.")
    # st.write("If you don't have a Performance Monitor file, you can skip this step by pressing the *Skip Step* button.") 
    info_text = "This file must be in the .CSV format produced by Perfmon."

    st.write(info_text)

    sidebar_l, sidebar_c, sidebar_r = st.columns([2,1,2])

    with sidebar_l:
        if st.button("Home"):
            st.switch_page("main.py")

    #  For now, skipping this data is not an option
                
    # with sidebar_r:
    #     if st.button("Skip Step"):
    #         st.switch_page("pages/summary.py")

main_l, main_c, main_r = st.columns([1,4,1])

with main_c:
    st.subheader("Performance Monitor (.CSV)")
    st.caption("JMeter JTL reports contain the performance test results and are in a .CSV format.")
   
    perfmon_file = st.file_uploader(" ", type=['csv'], key="perfmon", accept_multiple_files=False)
    
    # If a jmeter file has been selected, process it
    if perfmon_file:
        continue_processing = True
        
        with st.status("Uploading Perfmon File",  state="running", expanded=False) as status:
            # Transfer the file to the uploaded_data directory
            try:
                with open(f"uploaded_data/perfmon.csv", "wb") as f:
                    f.write(perfmon_file.getbuffer())
            except Exception as e:
                status.update(label="Error loading the Perfmon File", state="error", expanded=True)
                st.error(f"Error loading the Perfmon File: {e}")
                continue_processing=False
        
            if continue_processing:  
                status.update(label="Moving contents into a dataframe", state="running", expanded=False)
                try:
                    formatted_perfmon_data = pd.read_csv('uploaded_data/perfmon.csv')
                except Exception as e:
                    status.update(label="Error moving contents into a dataframe", state="error", expanded=True)
                    st.error(f"Error moving contents into a dataframe: {e}")
                    continue_processing=False
                    
            # Verify mandatory column information
            if continue_processing:  
                status.update(label="Checking for mandatory columns", state="running", expanded=False)
                if not all(column in formatted_perfmon_data.columns for column in required_columns):
                    status.update(label="Required columns are missing", state="error", expanded=True)
                    missing_columns = [column for column in required_columns if column not in formatted_perfmon_data.columns]
                    st.error(f"The following required columns are missing from the Perfmon file: {', '.join(missing_columns)}")
                    continue_processing=False
                    
            if continue_processing:
                # Remove empty columns
                try:
                    status.update(label="Removing columns with no data", state="running", expanded=False)
                    formatted_perfmon_data = formatted_perfmon_data.dropna(axis=1, how='all')
                except Exception as e:
                    status.update(label="Error removing columns with no data", state="error", expanded=True)
                    st.error(f"Error removing columns with no data: {e}")
                    continue_processing=False
            
            if continue_processing:  
                # Remove columns that contain only zeros
                try:
                    status.update(label="Removing zero-filled columns", state="running", expanded=False)
                    formatted_perfmon_data = formatted_perfmon_data.loc[:, (formatted_perfmon_data != 0).any(axis=0)]
                except Exception as e:
                    status.update(label="Error removing zero-filled columns", state="error", expanded=True)
                    st.error(f"Error removing zero-filled columns: {e}")
                    continue_processing=False

            if continue_processing:
                # Remove rows that contain only zeros
                try:
                    status.update(label="Removing rows with all zeros", state="running", expanded=False)
                    formatted_perfmon_data = formatted_perfmon_data.loc[~(formatted_perfmon_data==0).all(axis=1)]
                except Exception as e:
                    status.update(label="Error removing rows with all zeros", state="error", expanded=True)
                    st.error(f"Error removing rows with all zeros: {e}")
                    continue_processing=False
                    
            if continue_processing:
                # Round the data to 3 decimal places
                try:
                    status.update(label="Rounding to 3 decimal places", state="running", expanded=False)
                    formatted_perfmon_data = formatted_perfmon_data.round(3)
                except Exception as e:
                    status.update(label="Error rounding to 3 decimal places", state="error", expanded=True)
                    st.error(f"Error rounding to 3 decimal places: {e}")
                    continue_processing=False
            
            if continue_processing:
                try:
                    # Format the date format.
                    status.update(label="Formatting dates", state="running", expanded=False)
                    formatted_perfmon_data = formatted_perfmon_data.rename(columns={formatted_perfmon_data.columns[0]: "timeStamp"})
                    # Convert the data in this column to datetime
                    formatted_perfmon_data['timeStamp'] = pd.to_datetime(formatted_perfmon_data['timeStamp'])
                    # Round the data in this column to the nearest minute
                    formatted_perfmon_data['timeStamp'] = formatted_perfmon_data['timeStamp'].dt.round('min')
                except Exception as e:
                    status.update(label="Error formatting dates", state="error", expanded=True)
                    st.error(f"Error formatting dates: {e}")
                    continue_processing=False 
                
            if continue_processing:
                status.update(label="Finalising the process", state="error", expanded=True)
                
                # Set the index as the timeStamp
                formatted_perfmon_data.set_index('timeStamp', inplace=True)  
                
                # Save the formatted data to a CSV file and into the session state
                try:                  
                    status.update(label="Saving Processed Results", state="running", expanded=False)
                    
                    # Save the formatted data to the session state
                    st.session_state["formatted_perfmon_data"] = formatted_perfmon_data
                    
                    # Save the formatted data to a CSV file                   
                    formatted_perfmon_data.to_csv('formatted_data/perfmon.csv')
                    
                except Exception as e:
                    status.update(label="Error saving processed results", state="error", expanded=True)
                    st.error(f"Error saving processed results: {e}")
                    continue_processing=False
                    
            if continue_processing:
                status.update(label="Process Completed", state="complete", expanded=True)
                st.success("Perfmon data has been successfully processed.")
                # set the sessions state to indicate that data is available
                st.session_state["dataAvailable"] = True

            st.switch_page("pages/filter.py")            
            