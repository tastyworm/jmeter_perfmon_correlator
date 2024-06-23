import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import os
import base64

from config.config import set_page_config

set_page_config()

chart_display_width = 500
chart_display_height = 300

def cleanup_header_names(correlation_data):
    correlation_data[0] = correlation_data[0].str.replace('jmeter_label_','')
    correlation_data[0] = correlation_data[0].str.replace('jmeter_responseCode_','')
    correlation_data[1] = correlation_data[1].str.replace('perfmon_','')
    return correlation_data
    
# Check for cached data

if "merged_data" in st.session_state:
    merged_data = st.session_state["merged_data"]
    # st.write(merged_data.head())
else:
    st.switch_page("main.py")
    

if "correlation_pairs" in st.session_state:
    correlation_pairs = st.session_state["correlation_pairs"]
else:
    st.switch_page("pages/correlate.py")
    
with st.sidebar:
        st.title("Results")
        # create a slider with a min-max option for a number between 0 and 100
        min_val, max_val = st.slider("Select the minimum and maximum correlation values to display ", 0.0, 100.0, (80.0, 100.0))
        # Convert the slider values from percentage to decimal
        min_val = min_val / 100
        max_val = max_val / 100
        
        # Calculate the number of correlations that will be returned based on the min/max slider value
        correlations = []
        for jmeter_column in merged_data.filter(like='jmeter_').columns:
            for perfmon_column in merged_data.filter(like='perfmon_').columns:
                correlation = merged_data[jmeter_column].corr(merged_data[perfmon_column])
                if min_val <= abs(correlation) <= max_val:
                    correlations.append((jmeter_column, perfmon_column, correlation))

        # Sort the correlations in descending order
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # Reset the index
        correlations = pd.DataFrame(correlations).reset_index(drop=True)   
                    
        # Create a toggle here for "Display Charts" that defaults to off
        display_charts = st.checkbox("Display Charts", value=False)  
        st.warning("More correlations found mean a longer time to process the charts.")   
        
        # Reindex correlations
        correlations = correlations.reset_index(drop=True)
        
        if len(correlations) == 1:
            correlation_text = "correlation"
        else:
            correlation_text = "correlations"
       
        st.write(f"{len(correlations)} {correlation_text} found.")
        if display_charts: 
            # Initialise the progress bar
            progress_bar = st.progress(0)
            total_charts = len(correlations)
            for i in range(total_charts):
                # Update the progress bar
                progress_percentage = int((i / total_charts) * 100)
                progress_bar.progress(progress_percentage)
                
                jmeter_column = correlations[0][i]
                perfmon_column = correlations[1][i]
                correlation = correlations[2][i]
                fig_filename = f"{jmeter_column}_{perfmon_column}.png".replace("\\", "_").replace("%", "_").replace("/", "_")
                fig_filename = os.path.join("chart_data", fig_filename)

                
                # Check if the file already exists
                if not os.path.exists(fig_filename):
                    jmeter_column_name = f"(JMeter) {jmeter_column.replace('jmeter_', '')}"
                    perfmon_column_name = f"(Perfmon) {perfmon_column.replace('perfmon_', '')}"
                    if min_val <= abs(correlation) <= max_val:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.lineplot(data=merged_data, x=merged_data.index, y=jmeter_column, ax=ax, label=jmeter_column_name)
                        sns.lineplot(data=merged_data, x=merged_data.index, y=perfmon_column, ax=ax, label=perfmon_column_name)
                        if correlation < 0:
                            ax.set_title(f"{correlation*100:.2f}% (Negative Correlation)")
                        elif correlation == 0:
                            ax.set_title(f"{correlation*100:.2f}% (Correlation)")
                        else:
                            ax.set_title(f"{correlation*100:.2f}% (Positive Correlation)")
                        ax.set_xlabel("Time") 
                        ax.set_ylabel("Normalised Value")
                        ax.legend()
                        # Format x-axis to display time as hh:mm
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                        fig.savefig(fig_filename, format='png')
            progress_bar.progress(100) 
                
        
        sidebar_l, sidebar_c, sidebar_r = st.columns([1,1,2])

        with sidebar_l:
            if st.button("Back"):
                st.switch_page("pages/filter.py")

st.subheader("Common Data Summary")
topl, topc, topr = st.columns([1,20,1])

common_summary = st.session_state["common_summary"]

# Add a column to the dataframe called "# Correlations Identified with specified Range"
common_summary["# Correlations Identified"] = len(correlations) 


common_summary = pd.DataFrame(common_summary, index=[0])
st.write(common_summary.to_html(index=False), unsafe_allow_html=True)

st.divider()

# Charts


if len(correlations) == 0:
    st.write(f"No correlations found for the correlation range selected ({min_val*100}% to {max_val*100}%)")
else:

    # Utilising the data available in correlations, create a list of unique transaction names from the column names that include the string "jmeter_label_" and place them in a new list called transaction_names
    transaction_names = list(set([x.split('jmeter_label_')[1] for x in correlations[0] if 'jmeter_label_' in x]))

    # Utilising the data available in correlations, create a list of unique response codes from the column names that include the string "jmeter_responseCode_" and place them in a new list called response_codes
    response_codes = list(set([x.split('jmeter_responseCode_')[1] for x in correlations[0] if 'jmeter_responseCode_' in x]))
    response_codes.sort(reverse=False)

    main_tabs = st.tabs(["Transactions","Response Codes"])

    # Generate the correlation charts and save them to the chart_data folder

    # Transactions
    with main_tabs[0]:
        # List all of the transaction names as tabs
        if len(transaction_names) > 0:
            transaction_tabs = st.tabs(transaction_names)
            for i, transaction_tab in enumerate(transaction_tabs):
                if transaction_tab:
                    with transaction_tab:
                        # left_column, right_column = st.columns([1,1])
                        # Assign column names                
                        transaction_correlations = correlations[correlations[0].str.contains(f'{transaction_names[i]}')]
                        
                        # Remove the string of "perfmon_" from the data
                        transaction_column_original = transaction_correlations[1]
                        transaction_correlations[1] = transaction_correlations[1].str.replace('perfmon_','')
                        
                        # Create a new dataframe that contains just the final 2 columns from transaction_correlations
                        transaction_correlations = transaction_correlations.iloc[:,1:3]
                        raw_correlation = transaction_correlations.iloc[:,1]
                        transaction_correlations.columns=["Performance Counter","Correlation %"]
                                                
                        # Format the correlation values to display only two decimal places
                        transaction_correlations["Correlation %"] = transaction_correlations["Correlation %"] * 100
                        transaction_correlations["Correlation %"] = transaction_correlations["Correlation %"].map("{:.2f}%".format)


                        # Create a table, with two columns if the display charts toggle is false, or three columns if the display charts toggle is true
                        # The first and second columms are the transaction_correlation.columns and the third column will contain the correlation chart if the display charts toggle is clicked

                        table_html = "<table><tr><td>Performance Counter</td><td>Correlation %</td>"
                        if display_charts:
                            table_html += "<td>Chart</td>"
                        table_html += "</tr>"

                        for index, row in transaction_correlations.iterrows():
                            jmeter_column = correlations[0][index]
                            perfmon_column = correlations[1][index]
                            correlation = correlations[2][index]
                            table_html += f"<tr><td>{row['Performance Counter']}</td><td>{row['Correlation %']}</td>"
                            if display_charts:

                                fig_filename = f"{jmeter_column}_{perfmon_column}.png".replace("\\", "_").replace("%", "_").replace("/", "_")
                                fig_filename = os.path.join("chart_data", fig_filename)
                                
                                # Convert the image to a Base64 string
                                with open(fig_filename, "rb") as image_file:
                                    base64_string = base64.b64encode(image_file.read()).decode('utf-8')
                                
                                # Embed the Base64 string directly into the HTML
                                table_html += f"<td><img width='{chart_display_width}' height='{chart_display_height}' src='data:image/png;base64,{base64_string}' /></td>"
                            table_html += "</tr>"

                        table_html += "</table>"
                        st.write(table_html, unsafe_allow_html=True)


                    
        else:
            transaction_tabs=[]
            st.write("No transaction codes found for the correlation range selected")
        
            
    # Response Codes
    with main_tabs[1]:
        # List all of the response codes as tabs
        if len(response_codes) > 0:
            responseCode_tabs = st.tabs(response_codes)
            for i, responseCode_tab in enumerate(responseCode_tabs):
                if responseCode_tab:
                    with responseCode_tab:
                        # Assign column names                
                        responseCode_correlations = correlations[correlations[0].str.contains(f'responseCode_{response_codes[i]}')]
                        
                        # Remove the string of "perfmon_" from the data
                        responseCode_correlations[1] = responseCode_correlations[1].str.replace('perfmon_','')
                        
                        # Create a new dataframe that contains just the final 2 columns from responseCode_correlations
                        responseCode_correlations = responseCode_correlations.iloc[:,1:3]
                        responseCode_correlations.columns=["Performance Counter","Correlation %"]
                        # Format the correlation values to display only two decimal places
                        responseCode_correlations["Correlation %"] = responseCode_correlations["Correlation %"] * 100
                        responseCode_correlations["Correlation %"] = responseCode_correlations["Correlation %"].map("{:.2f}%".format)
                        
                         # Create a table, with two columns if the display charts toggle is false, or three columns if the display charts toggle is true
                        # The first and second columms are the transaction_correlation.columns and the third column will contain the correlation chart if the display charts toggle is clicked

                        table_html = "<table><tr><td>Performance Counter</td><td>Correlation %</td>"
                        if display_charts:
                            table_html += "<td>Chart</td>"
                        table_html += "</tr>"

                        for index, row in responseCode_correlations.iterrows():
                            jmeter_column = correlations[0][index]
                            perfmon_column = correlations[1][index]
                            correlation = correlations[2][index]
                            table_html += f"<tr><td>{row['Performance Counter']}</td><td>{row['Correlation %']}</td>"
                            if display_charts:

                                fig_filename = f"{jmeter_column}_{perfmon_column}.png".replace("\\", "_").replace("%", "_").replace("/", "_")
                                fig_filename = os.path.join("chart_data", fig_filename)
                                
                                # Convert the image to a Base64 string
                                with open(fig_filename, "rb") as image_file:
                                    base64_string = base64.b64encode(image_file.read()).decode('utf-8')
                                
                                # Embed the Base64 string directly into the HTML
                                table_html += f"<td><img width='{chart_display_width}' height='{chart_display_height}' src='data:image/png;base64,{base64_string}' /></td>"
                            table_html += "</tr>"

                        table_html += "</table>"
                        st.write(table_html, unsafe_allow_html=True)
            
        else:
            responseCode_tabs=[]
            st.write("No response codes found for the correlation range selected")