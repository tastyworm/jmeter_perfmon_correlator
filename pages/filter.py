import streamlit as st
import pandas as pd
import time
from config.config import set_page_config
from datetime import datetime
import tkinter as tk

set_page_config()

def format_seconds_to_text(seconds):
    # Convert the duration to hours, minutes, and seconds
    duration_hours, remainder = divmod(seconds, 3600)
    duration_minutes, duration_seconds = divmod(remainder, 60)
    
    duration_text = ""
    
    if duration_hours>0:
        if duration_hours==1:
            duration_text = f"{int(duration_hours)} hour, "
        else:
            duration_text = f"{int(duration_hours)} hours, "
    
    if duration_minutes>0:
        if duration_minutes == 1:
            duration_text += f"{int(duration_minutes)} minute"
        else:
            duration_text += f"{int(duration_minutes)} minutes"
    
    if (duration_hours>0 or duration_minutes>0):
            duration_text += " and "
    
    if duration_seconds==1:
        duration_text += f"{int(duration_seconds)} second"
    else:
        duration_text += f"{int(duration_seconds)} seconds"
    
    return duration_text

def extract_min_max_time(data):
    # Calculate the min/max dates of the data provided
    min_date = data.index.min().strftime("%d %B %Y")
    min_time = data.index.min().strftime("%H:%M")
    max_date = data.index.max().strftime("%d %B %Y")
    max_time = data.index.max().strftime("%H:%M")
    
    # Parse the min and max dates and times into datetime objects
    min_datetime = datetime.strptime(min_date + ' ' + min_time, "%d %B %Y %H:%M")
    max_datetime = datetime.strptime(max_date + ' ' + max_time, "%d %B %Y %H:%M")
    
    # Calculate the duration in seconds
    duration_seconds_total = (max_datetime - min_datetime).total_seconds()
    
    
    return min_date, min_time, max_date, max_time, min_datetime, max_datetime, duration_seconds_total

if "display_error" not in st.session_state:
    st.session_state["display_error"] = None
    
# Make sure there is data available to summarise
if ('formatted_jmeter_data' not in st.session_state) or ('formatted_perfmon_data' not in st.session_state):
    st.switch_page("main.py")
    
formatted_jmeter_data=st.session_state.formatted_jmeter_data
formatted_perfmon_data=st.session_state.formatted_perfmon_data

jmeter_min_date, jmeter_min_time, jmeter_max_date, jmeter_max_time, jmeter_min_datetime, jmeter_max_datetime, jmeter_duration_seconds_total = extract_min_max_time(formatted_jmeter_data)
perfmon_min_date, perfmon_min_time, perfmon_max_date, perfmon_max_time, perfmon_min_datetime, perfmon_max_datetime, perfmon_duration_seconds_total = extract_min_max_time(formatted_perfmon_data)

# Find the common min-max time period between jmeter and perfmon using perfmon_min_datetime, permon_max_datetime, jmeter_min_datetime, jmeter_max_datetime
common_min_datetime = max(jmeter_min_datetime, perfmon_min_datetime)
common_max_datetime = min(jmeter_max_datetime, perfmon_max_datetime)

# Calculate the minimum date and the maximum date without the time
common_min_date = common_min_datetime.strftime("%d %B %Y")
common_max_date = common_max_datetime.strftime("%d %B %Y")
common_min_time = common_min_datetime.strftime("%H:%M")
common_max_time = common_max_datetime.strftime("%H:%M")

#calculate the time period in seconds, mintes or hours between the common min and max datetime
common_duration_seconds_total = (common_max_datetime - common_min_datetime).total_seconds()

def calculate_jmeter_summary(display_table=False):        
    total_jmeter_transactions = formatted_jmeter_data.shape[0]   
    if jmeter_min_date == jmeter_max_date:
        jmeter_summary = {
            'Total Number of Transactions': total_jmeter_transactions,
                       
            'Date': jmeter_min_date,
            'Start Time': jmeter_min_time,
            'End Time': jmeter_max_time,
            'Data Duration': format_seconds_to_text(jmeter_duration_seconds_total)
        }
    else:
        jmeter_summary = {
            'Total Number of Transactions': total_jmeter_transactions,
                       
            'Start Date': jmeter_min_date,
            'Start Time': jmeter_min_time,
            'End Date': jmeter_max_date,
            'End Time': jmeter_max_time,
            'Data Duration': format_seconds_to_text(jmeter_duration_seconds_total)
        }
        
    # Save the summary to session state
    st.session_state["jmeter_summary"] = jmeter_summary
    
    if display_table:   
        st.subheader("JMeter")
        # Create a DataFrame with keys as index and an empty column name
        jmeter_summary = pd.DataFrame(jmeter_summary, index=[0]).T
        jmeter_summary.columns = ['']

        # Convert the DataFrame to HTML and remove the <thead> element
        table_html = jmeter_summary.to_html(header=False)
        table_html = table_html.replace('<thead>', '<thead style="display:none;">')

        # Display the table as markdown
        st.markdown(table_html, unsafe_allow_html=True)

def calculate_perfmon_summary(display_table=False):      
    total_perfmon_transactions = formatted_perfmon_data.shape[0]
   
    if perfmon_min_date == perfmon_min_date:
        perfmon_summary = {
            'Total Number of Transactions': total_perfmon_transactions,
                       
            'Date': perfmon_min_date,
            'Start Time': perfmon_min_time,
            'End Time': perfmon_max_time,
            'Data Duration': format_seconds_to_text(perfmon_duration_seconds_total)
        }
    else:
        perfmon_summary = {
            'Total Number of Transactions': total_perfmon_transactions,
                       
            'Start Date': perfmon_min_date,
            'Start Time': perfmon_min_time,
            'End Date': perfmon_max_date,
            'End Time': perfmon_max_time,
            'Data Duration': format_seconds_to_text(perfmon_duration_seconds_total)
        }
        
    # Save the summary to session state
    st.session_state["perfmon_summary"] = perfmon_summary
    
    if display_table:   
        st.subheader("Performance Monitor")
        # Create a DataFrame with keys as index and an empty column name
        perfmon_summary = pd.DataFrame(perfmon_summary, index=[0]).T
        perfmon_summary.columns = ['']

        # Convert the DataFrame to HTML and remove the <thead> element
        table_html = perfmon_summary.to_html(header=False)
        table_html = table_html.replace('<thead>', '<thead style="display:none;">')

        # Display the table as markdown
        st.markdown(table_html, unsafe_allow_html=True)

def calculate_common_summary(display_table=False):   
    if common_min_date == common_max_date:
        common_summary = {
            'Date': common_min_date,
            'Start Time': common_min_time,
            'End Time': common_max_time,
            'Data Duration': format_seconds_to_text(common_duration_seconds_total)
        }
    else:
        common_summary = {
            'Start Date': common_min_date,
            'Start Time': common_min_time,
            'End Date': common_max_date,
            'End Time': common_max_time,
            'Data Duration': format_seconds_to_text(common_duration_seconds_total)
        }
        
    # Save the summaries to session states
    st.session_state["common_summary"] = common_summary    

    if display_table:
        st.subheader("Common Summary")
        # Create a DataFrame with keys as index and an empty column name
        common_summary = pd.DataFrame(common_summary, index=[0]).T
        common_summary.columns = ['']
        
        # Convert the DataFrame to HTML and remove the <thead> element
        table_html = common_summary.to_html(header=False)
        table_html = table_html.replace('<thead>', '<thead style="display:none;">')
        
        # Display the table as markdown
        st.markdown(table_html, unsafe_allow_html=True)
 
if common_duration_seconds_total<=0:
    left_column, right_column = st.columns([1,1])
    with left_column:
        calculate_jmeter_summary(display_table=True)
    with right_column:
        calculate_perfmon_summary(display_table=True)
    st.write(" ")
    st.error("There is no common time period between the JMeter and Performance Monitor data. Please check the data and try again.")

    if st.button("Home"):
        st.switch_page("main.py")
else:
    # Extract jmeter_columns from formatted_jmeter_data
    jmeter_responsetime_columns = [column for column in formatted_jmeter_data.columns if column.startswith('label_')]
    jmeter_responsecode_columns= [column for column in formatted_jmeter_data.columns if column.startswith('responseCode_')]

    # Remove "label_" prefix from each column in the list
    formatted_jmeter_jmeter_responsetime_columns = [column.replace("label_", "") for column in jmeter_responsetime_columns]

    # Remove "responseCode_" prefix from each column in the list
    formatted_jmeter_responsecode_columns = [column.replace("responseCode_", "") for column in jmeter_responsecode_columns]


    # Extract perfmon_columns from formatted_perfmon_data
    perfmon_data_columns = [column for column in formatted_perfmon_data.columns]

    main_tabs = st.tabs(["JMeter Information", "Performance Monitor Counters"])

    # JMeter Transaction tab
    with main_tabs[0]:
        
        jmeter_tabs = st.tabs(["Response Times", "Response Codes"])
        
        # Initialize jmeter_data_dict as a dictionary outside the loop
        jmeter_data_dict = {}
        
        # Initialize lists to store selected labels and response codes
        selected_labels = []
        selected_response_codes = []
        
        with jmeter_tabs[0]:
            jmeter_labels = []
        
            for column in formatted_jmeter_data.columns:
                if column.startswith('label_'):
                    label = column.split('label_')[1]
                    if label not in jmeter_labels:
                        jmeter_labels.append(label)
            
            # Add a "Select All" checkbox and store its state
            select_all = st.checkbox("SELECT ALL", key="select_all", value=True)
        
            # List all of the jmeter_labels as checkboxes
            for label in jmeter_labels:
                # Use the state of the "Select All" checkbox to control the default state
                selected = st.checkbox(label, key=label, value=select_all)
                if selected:
                    selected_labels.append(label)
                    jmeter_data_dict[label] = formatted_jmeter_data[formatted_jmeter_data[f'label_{label}'] == 1]
                    
        
        with jmeter_tabs[1]:
            
            select_all_response_codes = st.checkbox("SELECT ALL", key="select_all_response_codes", value=True)
        
            jmeter_responsecodes = []
        
            for column in formatted_jmeter_data.columns:
                if column.startswith('responseCode_'):
                    responseCode = column.split('responseCode_')[1]
                    if responseCode not in jmeter_responsecodes:
                        jmeter_responsecodes.append(responseCode)
        
            # List all of the jmeter_responsecodes as checkboxes
            for responseCode in jmeter_responsecodes:
                # Use the state of the "Select All" checkbox to control the default state
                selected = st.checkbox(responseCode, key=responseCode, value=select_all_response_codes)
                if selected:
                    selected_response_codes.append(responseCode)
                    jmeter_data_dict[responseCode] = formatted_jmeter_data[formatted_jmeter_data[f'responseCode_{responseCode}'] == 1]
        
        # Combine selected labels and response codes into a single filter array
        jmeter_filter_label_array = selected_labels
        jmeter_filter_responsecode_array = selected_response_codes
        st.session_state["jmeter_filter_label_array"] = jmeter_filter_label_array
        st.session_state["jmeter_filter_responsecode_array"] = jmeter_filter_responsecode_array       
         
    # Performance Monitor Tab
    with main_tabs[1]:
        # Extract unique server names
        perfmon_counter_data_array = []
        
        for column in perfmon_data_columns:
            server_name = column.split("\\")[2]
            if "(" in column.split("\\")[3]:
                counter_topic = column.split("\\")[3].split("(")[0]
                counter_subtopic = column.split("\\")[3].split("(")[1].replace(")", "")
            else:
                counter_topic = column.split("\\")[3]
                counter_subtopic = ""
            counter_name = column.split("\\")[4]
            perfmon_counter_data_array.append([server_name, counter_topic, counter_subtopic, counter_name])
            

        # Organize data into a nested dictionary for easier access
        perfmon_data_dict = {}
        for entry in perfmon_counter_data_array:
            server_name, counter_topic, counter_subtopic, counter_name = entry
            if server_name not in perfmon_data_dict:
                perfmon_data_dict[server_name] = {}
            if counter_topic not in perfmon_data_dict[server_name]:
                perfmon_data_dict[server_name][counter_topic] = {}
            if counter_subtopic not in perfmon_data_dict[server_name][counter_topic]:
                perfmon_data_dict[server_name][counter_topic][counter_subtopic] = []
            perfmon_data_dict[server_name][counter_topic][counter_subtopic].append(counter_name)

        server_tabs = st.tabs(list(perfmon_data_dict.keys()))

    
        # Adjusted section for adding checkboxes and collecting selected counter names into a filter array

        filter_array = []

        # Adjusted section for adding a 'Select All' option in the final child tab

        for server_name in perfmon_data_dict:
            with server_tabs[list(perfmon_data_dict.keys()).index(server_name)]:
                # Create tabs for each counter topic under the current server
                if perfmon_data_dict[server_name]:  # Check if there are topics for the server
                    topic_tabs = st.tabs(list(perfmon_data_dict[server_name].keys()))
                    for counter_topic in perfmon_data_dict[server_name]:
                        with topic_tabs[list(perfmon_data_dict[server_name].keys()).index(counter_topic)]:
                            # Check if there are subtopics for the current topic
                            if perfmon_data_dict[server_name][counter_topic]:
                                # If there's only one subtopic and it's empty, list counter names directly under the topic
                                if len(perfmon_data_dict[server_name][counter_topic]) == 1 and "" in perfmon_data_dict[server_name][counter_topic]:
                                    select_all = st.checkbox("``` SELECT  ALL```", key=f"{server_name}_{counter_topic}_select_all") 
                                    for counter_name in perfmon_data_dict[server_name][counter_topic][""]:
                                        # Create a checkbox for each counter name
                                        selected = st.checkbox(f"{counter_name}", value=select_all, key=f"{server_name}_{counter_topic}_{counter_name}")
                                        if selected:
                                            filter_array.append((server_name, counter_topic, "", counter_name))
                                else:
                                    # Create tabs for each counter subtopic under the current topic
                                    subtopic_tabs = st.tabs(list(perfmon_data_dict[server_name][counter_topic].keys()))
                                    for counter_subtopic in perfmon_data_dict[server_name][counter_topic]:
                                        with subtopic_tabs[list(perfmon_data_dict[server_name][counter_topic].keys()).index(counter_subtopic)]:
                                            # Add a 'Select All' option for the current subtopic
                                            select_all = st.checkbox('``` SELECT  ALL```', key=f"{server_name}_{counter_topic}_{counter_subtopic}_select_all")
                                            # List all counter names under the current subtopic with checkboxes
                                            for counter_name in perfmon_data_dict[server_name][counter_topic][counter_subtopic]:
                                                selected = st.checkbox(f"{counter_name}", value=select_all, key=f"{server_name}_{counter_topic}_{counter_subtopic}_{counter_name}")
                                                if selected:
                                                    filter_array.append((server_name, counter_topic, counter_subtopic, counter_name))
            
            st.session_state["perfmon_filter_array"] = filter_array
            if (len(filter_array) == 0):
                st.session_state["display_error"] = "No Performance Monitor counters have been selected. Please select at least one item to correlate."
            else:
                st.session_state["display_error"] = None          
                
            calculate_common_summary()
        
        with st.sidebar:
            st.header("Filter Your Data")
            st.divider()
            st.write("If there is any information you don't need to correlate, it will save time by excluding it.  \n   \n Select which items you would like to include in the correlation analysis and then press the button below to continue.")    
            
            sidebar_l, sidebar_c, sidebar_r = st.columns([3,1,5])

            with sidebar_l:
                if st.button("Back"):
                    st.switch_page("pages/perfmon.py")

            with sidebar_r:
                if st.button("Correlate the Data"):
                     # if perfmon_filter_array does not contain any data, write a message saying that the data is not selected
                    if len(st.session_state["perfmon_filter_array"]) == 0:
                        st.session_state["display_error"] = "No Performance Monitor counters have been selected. Please select at least one item to correlate."
                    else:
                        st.session_state["display_error"] = None
                        st.switch_page("pages/correlate.py")

if "first_run" not in st.session_state:
    st.session_state["first_run"] = True
else:
    if st.session_state["display_error"] != None:
        st.error(st.session_state["display_error"])
