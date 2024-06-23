import streamlit as st
import pandas as pd
import time
from config.config import set_page_config
import pytz
from datetime import datetime

set_page_config()

# Detail the minimum required columns for the JMeter file
required_columns = ['timeStamp', 'elapsed', 'label', 'responseCode']

# Create the sidebar
with st.sidebar:
    st.title("JMeter Analysis")
    st.divider()
    info_text = "This file requires a minimum of the following data in order to be processed:\n"
    info_text += "\n".join(f"* {column}" for column in required_columns)
    
    st.write(info_text)

    sidebar_l, sidebar_c, sidebar_r = st.columns([2,1,2])

    with sidebar_l:
        if st.button("Home"):
            st.switch_page("main.py")
   
main_l, main_c, main_r = st.columns([1,4,1])

with main_c:
    st.subheader("JMeter (.JTL) Report")
    st.caption("JMeter JTL reports contain the performance test results and are in a .CSV format.")
   
    jmeter_file = st.file_uploader(" ", type=['jtl'], key="jmeter", accept_multiple_files=False)
    
    # If a jmeter file has been selected, process it
    if jmeter_file:
        st.session_state["do_not_show_skip_button"] = True
        continue_processing = True
        
        # Create a dataframe to store the formatted JMeter data
        formatted_jmeter_data = pd.DataFrame()
               
        with st.status("Uploading JMeter File",  state="running", expanded=False) as status:
            
            # Transfer the file to the uploaded_data directory
            try:
                with open(f"uploaded_data/jmeter.csv", "wb") as f:
                    f.write(jmeter_file.getbuffer())
            except Exception as e:
                status.update(label="Error loading the JMeter File", state="error", expanded=True)
                st.error(f"Error loading the JMeter File: {e}")
                continue_processing=False
            
            # Load the file into a dataframe
            if continue_processing:  
                status.update(label="Moving contents into a dataframe", state="running", expanded=False)
                try:
                    jmeter_df = pd.read_csv('uploaded_data/jmeter.csv')
                except Exception as e:
                    status.update(label="Error moving contents into a dataframe", state="error", expanded=True)
                    st.error(f"Error moving contents into a dataframe: {e}")
                    continue_processing=False
            
            # Verify mandatory column information
            if continue_processing:  
                status.update(label="Checking for mandatory columns", state="running", expanded=False)
                if not all(column in jmeter_df.columns for column in required_columns):
                    status.update(label="Required columns are missing", state="error", expanded=True)
                    missing_columns = [column for column in required_columns if column not in jmeter_df.columns]
                    st.error(f"The following required columns are missing from the JMeter file: {', '.join(missing_columns)}")
                    continue_processing=False
                               
            # Convert the timestamp to the correct format and round it to the nearest minute
            if continue_processing:
                try:
                    status.update(label="Translating timestamps", state="running", expanded=False)              
                    jmeter_df['timeStamp'] = pd.to_datetime(jmeter_df['timeStamp'], unit='ms')
                    jmeter_df['timeStamp'] = jmeter_df['timeStamp'].dt.round('min')
                    
                    # Add the translated timeStamp column to the formatted_jmeter_data dataframe
                    formatted_jmeter_data['timeStamp'] = jmeter_df['timeStamp']
                                   
                except Exception as e:
                    status.update(label="Error translating timestamps", state="error", expanded=True)
                    st.error(f"Error translating timestamps: {e}")
                    continue_processing=False
            
            try:
                unique_labels = jmeter_df['label'].unique()
                for columnlabel in unique_labels:
                    status.update(label="Formatting Label '{}'".format(columnlabel), state="running", expanded=False)
                    column_name = f"label_{columnlabel}"
                    label_data = jmeter_df[jmeter_df['label'] == columnlabel].groupby('timeStamp')['elapsed'].mean().reset_index().rename(columns={'elapsed': column_name})
                    formatted_jmeter_data = pd.merge(formatted_jmeter_data, label_data, on='timeStamp', how='left')
            except Exception as e:
                status.update(label="Error formatting labels", state="error", expanded=True)
                st.error(f"Error formatting labels: {e}")
                continue_processing=False
            
            if continue_processing:
                # For each unique value in the responseCode field, create a new column in the formatted_jmeter_data dataframe for each unique responseCode field called responseCode_xxx where xxx is the response code, and contains the count of that responseCode for each timestamp
                try:
                    unique_response_codes = jmeter_df['responseCode'].unique()
                    for code in unique_response_codes:
                        status.update(label="Formatting Response Code '{}'".format(code), state="running", expanded=False)
                        column_name = f"responseCode_{code}"
                        code_data = jmeter_df[jmeter_df['responseCode'] == code].groupby('timeStamp')['responseCode'].count().reset_index().rename(columns={'responseCode': column_name})
                        formatted_jmeter_data = pd.merge(formatted_jmeter_data, code_data, on='timeStamp', how='left')
                except Exception as e:
                    status.update(label="Error formatting response codes", state="error", expanded=True)
                    st.error(f"Error formatting response codes: {e}")
                    continue_processing=False
                    
            if continue_processing:
                # if the column 'success' exists in the jmeter data, create a new columns in the formatted_jmeter_data dataframe called 'success_true' and 'success_false' that contains the count of the number of times the 'success' column is true or false for each timestamp
                try:        
                    if 'success' in jmeter_df.columns:
                        status.update(label="Formatting Statuses", state="running", expanded=False)
                        formatted_jmeter_data['success_true'] = jmeter_df[jmeter_df['success'] == True].groupby('timeStamp')['success'].count().reset_index(drop=True).astype(int)
                        formatted_jmeter_data['success_false'] = jmeter_df[jmeter_df['success'] == False].groupby('timeStamp')['success'].count().reset_index(drop=True).astype(int)
                except Exception as e:
                    status.update(label="Error formatting statuses", state="error", expanded=True)
                    st.error(f"Error formatting statuses: {e}")
                    continue_processing=False
                    
            if continue_processing:
                # Retrieve the current time in UTC
                current_time = pd.to_datetime(time.time(), unit='s', origin='unix', utc=True)

                # Get the current time in the local timezone
                current_time_local = datetime.now().replace(tzinfo=pytz.utc)

                # Calculate the difference in hours between the current time in UTC and the current time in the local timezone
                time_difference = (current_time_local - current_time).seconds / 3600

                # Add the time difference to the timeStamp column
                formatted_jmeter_data['timeStamp'] = formatted_jmeter_data['timeStamp'] + pd.DateOffset(hours=time_difference)
            
        
                status.update(label="Finalising the process", state="error", expanded=True)
                    
                # Set the timeStamp as the dataframe index
                formatted_jmeter_data.set_index('timeStamp', inplace=True) 
                
                try:
                    status.update(label="Saving Processed Results", state="running", expanded=False)
                    
                    # Save the formatted data to the session state
                    st.session_state["formatted_jmeter_data"] = formatted_jmeter_data
                    
                    # Save the formatted data to a CSV file
                    formatted_jmeter_data.to_csv('formatted_data/jmeter.csv')
                    
                except Exception as e:
                    status.update(label="Error saving processed results", state="error", expanded=True)
                    st.error(f"Error saving processed results: {e}")
                    continue_processing=False
                    
            if continue_processing:
                status.update(label="Process Completed", state="complete", expanded=True)
                st.success("JMeter data has been successfully processed.")
                
                # set the sessions state to indicate that data is available
                st.session_state["dataAvailable"] = True
                                
                st.switch_page("pages/perfmon.py")
                

