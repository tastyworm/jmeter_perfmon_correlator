import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config.config import set_page_config
import math
           
set_page_config()

# If perfmon_filter_array or jmeter_filter_array don't have any data, redirect to the main page
if 'perfmon_filter_array' not in st.session_state or 'jmeter_filter_label_array' not in st.session_state or 'jmeter_filter_responsecode_array' not in st.session_state:
    st.switch_page("main.py")
    
if 'formatted_perfmon_data' not in st.session_state and 'formatted_jmeter_data' not in st.session_state:
    st.switch_page("main.py")
    
if len(st.session_state["perfmon_filter_array"]) == 0:
    st.switch_page("main.py")

perfmon_filter_array = st.session_state["perfmon_filter_array"]
jmeter_filter_label_array = st.session_state["jmeter_filter_label_array"]
jmeter_filter_responsecode_array = st.session_state["jmeter_filter_responsecode_array"]
formatted_jmeter_data = st.session_state["formatted_jmeter_data"]
formatted_perfmon_data = st.session_state["formatted_perfmon_data"]

def translate_jmeter_filter(filter_array_row, filter_type):
    if filter_type=="label":
        return f'label_{filter_array_row}'
    if filter_type=="responsecode":
        return f'responseCode_{filter_array_row}'

def translate_perfmon_filter(filter_array_row):
    slash = "\\"
    if filter_array_row[2] == "":
        return f"{slash}{slash}{filter_array_row[0]}{slash}{filter_array_row[1]}{slash}{filter_array_row[3]}"
    else:
        return f"{slash}{slash}{filter_array_row[0]}{slash}{filter_array_row[1]}({filter_array_row[2]}){slash}{filter_array_row[3]}"


# Filter the JMeter Data to only retain what was previously selected
formatted_jmeter_data = formatted_jmeter_data.filter(items=[translate_jmeter_filter(row, "label") for row in jmeter_filter_label_array] + [translate_jmeter_filter(row, "responsecode") for row in jmeter_filter_responsecode_array])

# Filter the Performance Monitor Data to only retain what was previously selected
translated_filters = [translate_perfmon_filter(row) for row in perfmon_filter_array]
formatted_perfmon_data = formatted_perfmon_data[translated_filters]

continue_processing = True

with st.sidebar:
    st.title("Correlation Analysis")
    st.write("Correlation analysis is the process of establishing a relationship between two or more data sets to see if they are related.")
    sidebar_l, sidebar_c, sidebar_r = st.columns([1,1,2])

    with sidebar_l:
        if st.button("Back"):
            st.switch_page("pages/summary.py")

main_l, main_c, main_r = st.columns([1,8,1])

with main_c:
    st.header("Correlating Data...")
    with st.expander("***While you're waiting, why not learn more about correlation?***"):
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("<small>Correlation is the process of establishing a relationship (or connection) between two or more data sets to see if two sets of data are related.</small>", unsafe_allow_html=True)
        st.markdown("<small>The correlation coefficient is a value that indicates the strength and direction of a relationship between two variables and ranges from -1 to 1.</small>", unsafe_allow_html=True)
        st.markdown("<small>A correlation coefficient of 1 indicates a perfect positive correlation, a correlation coefficient of -1 indicates a perfect negative correlation and a correlation coefficient of 0 indicates that there is no correlation at all. Therefore the closer the correlation coefficient is to 1 or -1, the stronger the relationship between the two data sets and conversely the closer the correlation coefficient is to 0, the weaker the relationship is.</small>", unsafe_allow_html=True)
        st.markdown("<small>The correlation analysis is performed by calculating the correlation coefficient between the two data sets using the Pearson correlation coefficient formula.</small>", unsafe_allow_html=True)
        st.latex(r'''
        r = \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i - \bar{x})^2 \sum_{i=1}^{n}(y_i - \bar{y})^2}}
        ''')
        st.markdown("<small>Where:</small>", unsafe_allow_html=True)
        st.markdown("<small><em>r</em> is the Pearson correlation coefficient.</small>", unsafe_allow_html=True)
        st.markdown("<small><em>n</em> is the number of data points.</small>", unsafe_allow_html=True)

#     ### PERFORMANCE MONITOR DATA ###


    with st.status(label="Preparing Performance Monitor Data for correlation", state="running", expanded=False) as status:
      
        # Replace any non-numeric data with NaN
        status.update(label="Converting non-numeric data to NaN", expanded=False)
        try:
            formatted_perfmon_data = formatted_perfmon_data.apply(pd.to_numeric, errors='coerce')
        except Exception as e:
            status.update(label="Error converting non-numeric data to NaN", state="error", expanded=True)
            st.error(f"Error converting non-numeric data to NaN: {e}")
            continue_processing=False
            
            
        status.update(label="Converting numeric data to 3 decimal places", expanded=False)
        # Change all of the data that is numeric (excluding the headers) to 3 decimal places
        try:
            # Convert each column to float with 3 decimal places
            numeric_columns = formatted_perfmon_data.columns
            formatted_perfmon_data[numeric_columns] = formatted_perfmon_data[numeric_columns].apply(pd.to_numeric, errors='coerce')
            formatted_perfmon_data[numeric_columns] = formatted_perfmon_data[numeric_columns].round(3)
        except Exception as e:
            status.update(label="Error rounding Perfmon data", state="error", expanded=True)
            st.error(f"Error rounding Perfmon data: {e}")
            continue_processing=False
            
        if continue_processing:
            # Aggregate the data into 1 minute intervals
            status.update(label="Averaging Perfmon data to 1 minute intervals", expanded=False)
            try:
                formatted_perfmon_data = formatted_perfmon_data.resample('min').mean()

            except Exception as e:
                status.update(label="Error aggregating Perfmon data", state="error", expanded=True)
                st.error(f"Error aggregating Perfmon data: {e}")
                continue_processing=False
                
        if continue_processing:
            # Remove any rows with all zeros
            status.update(label="Removing rows with all zeros", expanded=False)
            try:
                formatted_perfmon_data = formatted_perfmon_data.loc[~(formatted_perfmon_data==0).all(axis=1)]
            except Exception as e:
                status.update(label="Error removing rows with all zeros", state="error", expanded=True)
                st.error(f"Error removing rows with all zeros: {e}")
                continue_processing=False
                
        if continue_processing:
            # Remove any columns with all zeros
            status.update(label="Removing columns with all zeros", expanded=False)
            try:
                formatted_perfmon_data = formatted_perfmon_data.loc[:, (formatted_perfmon_data != 0).any(axis=0)]
            except Exception as e:
                status.update(label="Error removing columns with all zeros", state="error", expanded=True)
                st.error(f"Error removing columns with all zeros: {e}")
                continue_processing=False
                
        if continue_processing:
            # Remove any columns with all NaNs
            status.update(label="Removing columns with all NaNs", expanded=False)
            try:
                formatted_perfmon_data = formatted_perfmon_data.dropna(axis=1, how='all')
            except Exception as e:
                status.update(label="Error removing columns with all NaNs", state="error", expanded=True)
                st.error(f"Error removing columns with all NaNs: {e}")
                continue_processing=False
                
        if continue_processing:
            # Remove any rows with all NaNs
            status.update(label="Removing rows with all NaNs", expanded=True)
            try:
                formatted_perfmon_data = formatted_perfmon_data.dropna(axis=0, how='all')
            except Exception as e:
                status.update(label="Error removing rows with all NaNs", state="error", expanded=True)
                st.error(f"Error removing rows with all NaNs: {e}")
                continue_processing=False

        if continue_processing:
            # Initialize the progress bar
            progress_bar = st.progress(0)

            # Calculate the total number of columns
            total_columns = len(formatted_perfmon_data.columns)

            # add a prefix to each column of "perfmon_"
            status.update(label="Adding prefix to Perfmon data", expanded=False)
            try:
                for i, column in enumerate(formatted_perfmon_data.columns):
                    # Add the prefix to the current column
                    formatted_perfmon_data = formatted_perfmon_data.rename(columns={column: 'perfmon_' + column})

                    # Update the progress bar
                    progress_bar.progress((i + 1) / total_columns)
            except Exception as e:
                status.update(label="Error adding prefix to Perfmon data", state="error", expanded=True)
                st.error(f"Error adding prefix to Perfmon data: {e}")
                continue_processing=False
    
        if continue_processing:
            isPerfmonData = True
        else:
            isPerfmonData = False
                                
        
        
    ### JMETER DATA ###


    with st.status(label="Preparing JMeter Data for correlation", state="running", expanded=False) as status:        
        
        # Replace any non-numeric data with NaN
        status.update(label="Converting non-numeric data to NaN", expanded=False)
        try:
            formatted_jmeter_data = formatted_jmeter_data.apply(pd.to_numeric, errors='coerce')
        except Exception as e:
            status.update(label="Error converting non-numeric data to NaN", state="error", expanded=True)
            st.error(f"Error converting non-numeric data to NaN: {e}")
            continue_processing=False
            
        if continue_processing:
            status.update(label="Converting numeric data to 3 decimal places", expanded=False)
            # Change all of the data that is numeric (excluding the headers) to 3 decimal places
            try:
                # Convert each column to float with 3 decimal places
                numeric_columns = formatted_jmeter_data.columns
                formatted_jmeter_data[numeric_columns] = formatted_jmeter_data[numeric_columns].round(3)
            except Exception as e:
                status.update(label="Error rounding JMeter data", state="error", expanded=True)
                st.error(f"Error rounding JMeter data: {e}")
                continue_processing=False
                    
        
        if continue_processing:
            # Aggregate the data into 1 minute intervals
            status.update(label="Averaging JMeter data to 1 minute intervals", expanded=False)
            try:
                formatted_jmeter_data = formatted_jmeter_data.resample('min').mean()
            except Exception as e:
                status.update(label="Error aggregating JMeter data", state="error", expanded=True)
                st.error(f"Error aggregating JMeter data: {e}")
                continue_processing=False
        
        if continue_processing:
            # Remove any rows with all zeros
            status.update(label="Removing rows with all zeros", expanded=False)
            try:
                formatted_jmeter_data = formatted_jmeter_data.loc[~(formatted_jmeter_data==0).all(axis=1)]
            except Exception as e:
                status.update(label="Error removing rows with all zeros", state="error", expanded=True)
                st.error(f"Error removing rows with all zeros: {e}")
                continue_processing=False
                
        if continue_processing:
            # Remove any columns with all zeros
            status.update(label="Removing columns with all zeros", expanded=False)
            try:
                formatted_jmeter_data = formatted_jmeter_data.loc[:, (formatted_jmeter_data != 0).any(axis=0)]
            except Exception as e:
                status.update(label="Error removing columns with all zeros", state="error", expanded=True)
                st.error(f"Error removing columns with all zeros: {e}")
                continue_processing=False
                
        if continue_processing:
            # Remove any columns with all NaNs
            status.update(label="Removing columns with all NaNs", expanded=False)
            try:
                formatted_jmeter_data = formatted_jmeter_data.dropna(axis=1, how='all')
            except Exception as e:
                status.update(label="Error removing columns with all NaNs", state="error", expanded=True)
                st.error(f"Error removing columns with all NaNs: {e}")
                continue_processing=False
                
        if continue_processing:
            # Remove any rows with all NaNs
            status.update(label="Removing rows with all NaNs", expanded=False)
            try:
                formatted_jmeter_data = formatted_jmeter_data.dropna(axis=0, how='all')
            except Exception as e:
                status.update(label="Error removing rows with all NaNs", state="error", expanded=True)
                st.error(f"Error removing rows with all NaNs: {e}")
                continue_processing=False
        
        if continue_processing:
            # add a prefix to each column of "jmeter_"
            status.update(label="Adding prefix to JMeter data", expanded=False)
            try:
                formatted_jmeter_data = formatted_jmeter_data.add_prefix('jmeter_')
            except Exception as e:
                status.update(label="Error adding prefix to JMeter data", state="error", expanded=True)
                st.error(f"Error adding prefix to JMeter data: {e}")
                continue_processing=False
        
        if continue_processing:
            isJMeterData = True
        else:
            isJMeterData = False
            
        # If there is both perfmon and jmeter data...   
        if isPerfmonData and isJMeterData:

    
        # Merge the data into a single dataframe

            status.update(label="Merging Perfmon and JMeter data", expanded=False)
            try:
                merged_data = pd.merge(formatted_perfmon_data, formatted_jmeter_data, how='inner', left_index=True, right_index=True)
            except Exception as e:
                status.update(label="Error merging Perfmon and JMeter data", state="error", expanded=True)
                st.error(f"Error merging Perfmon and JMeter data: {e}")
                continue_processing=False
                
        if continue_processing:
            # Normalise each column
            status.update(label="Normalising Merged data", expanded=False)
            try:
                merged_data = (merged_data - merged_data.mean()) / merged_data.std()
            except Exception as e:
                status.update(label="Error normalising Merged data", state="error", expanded=True)
                st.error(f"Error normalising Merged data: {e}")
                continue_processing=False
                

        # Initialize correlation_pairs if it doesn't exist in session state
        if "correlation_pairs" not in st.session_state:
            st.session_state.correlation_pairs = {}

        # For each column starting with jmeter_ calculate the correlation with each column starting with perfmon_
        if continue_processing:
            status.update(label="Calculating Correlation Coefficients", expanded=False)
            # Calculate the correlation coefficients for each column against each other column and display the data as it processes
            for jmeter_column in merged_data.filter(like='jmeter_').columns:
                for perfmon_column in merged_data.filter(like='perfmon_').columns:
                    try:
                        correlation = merged_data[jmeter_column].corr(merged_data[perfmon_column])
                        # Save correlation pair and value to session state
                        st.session_state.correlation_pairs[f"{jmeter_column} vs {perfmon_column}"] = correlation
                    except Exception as e:
                        status.update(label="Error calculating correlation coefficients", state="error", expanded=True)
                        st.error(f"Error calculating correlation coefficients: {e}")
                        continue_processing=False
                        break
                    
        # Save the merged data to a session state for future use
        st.session_state["merged_data"] = merged_data
        
        # Navigate to the display page
        if continue_processing:
            st.switch_page("pages/display.py")
        

            # # st.table(merged_data.head(5))
            
            # # Display the number of correlations that have a value of > 90%
            # # st.write(f"Number of correlations with an absolute value of > 90%: {len(merged_data[abs(merged_data) > 0.9].stack())}")
            
            
            # # create a slider with a min-max option for a number between 0 and 100
            # min_val, max_val = st.slider("Select the minimum and maximum correlation values to display ", 0.0, 100.0, (0.0, 100.0))

            # # Convert the slider values from percentage to decimal
            # min_val = min_val / 100
            # max_val = max_val / 100

            # # Calculate the the amount of data that will be returned based on the min/max slider value
            # st.write(f"Number of correlations with an absolute value between {min_val} and {max_val}: {len(merged_data[(abs(merged_data) >= min_val) & (abs(merged_data) <= max_val)].stack())}")
            # continue_processing = False
            
            # if continue_processing:                
            #     status.update(label="Creating Correlation Data", expanded=True)

            #     # Create a DataFrame to store the correlation pairs, correlation values, and filenames
            #     reference_data = pd.DataFrame(columns=['Correlation Pair', 'Correlation Value', 'Filename'])

            #     # Calculate the factorial of the column numbers
            #     data_combinations = factorial_value = math.factorial(len(merged_data.columns))

            #     # Initialize reference_data as a DataFrame
            #     reference_data = pd.DataFrame(columns=['Correlation Pair', 'Correlation Value', 'Filename'])

            #     # Initialize a counter
            #     counter = 0

            #     # Initialize a Streamlit progress bar
            #     progress_bar = st.progress(0)

            #     for column1 in merged_data.columns:
            #         for column2 in merged_data.columns:
            #             status.update(label=f"Creating Correlation Data ({counter}/{data_combinations})", expanded=True)
            #             try:
            #                 correlation = merged_data[column1].corr(merged_data[column2])
                            
            #                 # If the correlation is greater than 0.90, create a chart
            #                 if correlation > 0.98:
                                
            #                     chart_data = merged_data[[column1, column2]]
                                
            #                     # Save the chart data to a CSV file with a sequential number as the filename
            #                     filename = f"chart_data/{counter}.csv"
            #                     chart_data.to_csv(filename, index=False)
                                
            #                     # Add a row to the reference data
            #                     new_row = pd.DataFrame({
            #                         'Correlation Pair': [f"{column1} vs {column2}"],
            #                         'Correlation Value': [round(correlation, 1)],
            #                         'Filename': [filename]
            #                     })
            #                     reference_data = pd.concat([reference_data, new_row], ignore_index=True)
                            
            #                 # Increment the counter
            #                 counter += 1

            #                 # Update the Streamlit progress bar
            #                 progress_bar.progress(counter / data_combinations)
            #             except Exception as e:
            #                 st.error(f"Error creating correlation charts: {e}")
            #                 break

            #     # Save the reference data to a CSV file
            #     reference_data.to_csv('chart_data/reference_data.csv', index=False)

                