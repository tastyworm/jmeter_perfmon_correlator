import streamlit as st
import pandas as pd
import time
from config.config import set_page_config
from datetime import datetime

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


def display_jmeter_summary():        
    total_jmeter_transactions = formatted_jmeter_data.shape[0]

    st.subheader("JMeter")
   
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
        
    # Create a DataFrame with keys as index and an empty column name
    jmeter_summary = pd.DataFrame(jmeter_summary, index=[0]).T
    jmeter_summary.columns = ['']

    # Convert the DataFrame to HTML and remove the <thead> element
    table_html = jmeter_summary.to_html(header=False)
    table_html = table_html.replace('<thead>', '<thead style="display:none;">')

    # Display the table as markdown
    st.markdown(table_html, unsafe_allow_html=True)

def display_perfmon_summary():   
    st.subheader("Performance Monitor")
    
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
    
    # Create a DataFrame with keys as index and an empty column name
    perfmon_summary = pd.DataFrame(perfmon_summary, index=[0]).T
    perfmon_summary.columns = ['']

    # Convert the DataFrame to HTML and remove the <thead> element
    table_html = perfmon_summary.to_html(header=False)
    table_html = table_html.replace('<thead>', '<thead style="display:none;">')

    # Display the table as markdown
    st.markdown(table_html, unsafe_allow_html=True)


def display_common_summary():
    st.subheader("Common Summary")
    
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

    # Create a DataFrame with keys as index and an empty column name
    common_summary = pd.DataFrame(common_summary, index=[0]).T
    common_summary.columns = ['']
    
    # Convert the DataFrame to HTML and remove the <thead> element
    table_html = common_summary.to_html(header=False)
    table_html = table_html.replace('<thead>', '<thead style="display:none;">')
    
    # Display the table as markdown
    st.markdown(table_html, unsafe_allow_html=True)
    
    
if 'dataAvailable' in st.session_state:
    with st.sidebar:
        st.title("Data Summary")
        st.write("Here is a summary of the data you have provided:")
        
        sidebar_l, sidebar_c, sidebar_r = st.columns([3,1,3])

        with sidebar_l:
            if st.button("Start Over"):
                st.switch_page("main.py")
        
        with sidebar_r:
            if st.button("Correlate Data"):
                st.switch_page("pages/correlate.py")

else:
    with st.sidebar:
        st.title("Data Summary")
        st.write("Here is a summary of the data you have provided.")
        sidebar_l, sidebar_c, sidebar_r = st.columns([1,1,2])
                 
main_l, main_cl, main_cr, main_r = st.columns([1,11,11,1])

with main_cl:
    display_jmeter_summary()

with main_cr:
    display_perfmon_summary()
    
st.divider()
   
main_l2, main_c2, main_r2 = st.columns([2,2,2])

with main_c2:
    display_common_summary()
