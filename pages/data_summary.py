import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


st.set_page_config(page_title="Performance Analysis Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    .very-small-font {
    font-size: 12px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


st.title("Performance Analysis Tool")
left_column, spacer, right_column= st.columns([1,2,1], gap="large")
with right_column:
    if st.button("Start Over"):
        st.switch_page("pages/index.py")

# If there is raw_jmeter_data in the session state, add a tab for JMeter data
if st.session_state.get('raw_jmeter_data', None) is not None:
    isJMeterData = True
else:
    isJMeterData = False
    
# If there is perfmon_data in the session state, add a tab for Perfmon data
if st.session_state.get('perfmon_data', None) is not None:
    isPerfmonData = True
else:
    isPerfmonData = False
    
if isJMeterData:
    if isPerfmonData:
        tab_jmeter, tab_perfmon, tab_correlation = st.tabs(["JMeter Data", "Perfmon Data", "Correlation Results"])
        warning_message= ""
    else:
        tab_jmeter, no_tab = st.tabs(["JMeter Data"," "])
        warning_message = "Only JMeter data was provided. Correlation results are not available."
else:
    if isPerfmonData:
        tab_perfmon, tab_correlation = st.tabs(["Perfmon Data","Correlation Results"])

        
if isJMeterData:
    with tab_jmeter:
        tab_jmeter_tables, tab_jmeter_charts, tab_jmeter_sampledata = st.tabs(["Tables", "Charts", "Data Extract"])
        if len(warning_message) > 0:
            st.warning(warning_message)
        with tab_jmeter_tables:
            
            # Group the data by 'label'
            grouped_data = st.session_state['raw_jmeter_data'].groupby('label')
            
            # Calculate the required statistics for each group
            table_data = grouped_data.agg(
                Total_Transactions=('elapsed', 'count'),
                Success=('responseMessage', lambda x: (x == 'OK').sum()),
                Failed=('responseMessage', lambda x: (x != 'OK').sum()),
                Response_Time_Min=('elapsed', 'min'),
                Response_Time_Avg=('elapsed', 'mean'),
                Response_Time_Max=('elapsed', 'max'),
                Response_Time_90th=('elapsed', lambda x: np.percentile(x, 90)),
                Response_Time_95th=('elapsed', lambda x: np.percentile(x, 95)),
                Response_Time_99th=('elapsed', lambda x: np.percentile(x, 99))
            )

            # Rename the columns
            table_data = table_data.rename(columns={'Response_Time_90th':'90%','Response_Time_Max':'Max','Response_Time_Avg':'Avg','Response_Time_Min':'Min','Total_Transactions': '#', 'Success': 'Pass','Failed': 'Fail','Response_Time_95th': '95%', 'Response_Time_99th': '99%'})

            # Calculate the percentage of successful and failed transactions
            table_data['% Success'] = ((table_data['Pass'] / table_data['#']) * 100).round(0)
            table_data['% Failed'] = ((table_data['Fail'] / table_data['#']) * 100).round(0)

            response_time_columns = ['Min', 'Avg', 'Max', '90%', '95%', '99%']
            table_data[response_time_columns] = table_data[response_time_columns] / 1000

            # Apply rounding here
            table_data = table_data.round(2)

            st.table(table_data)
        
        with tab_jmeter_charts:
            tab_jmeter_charts_rt,  tab_jmeter_charts_rc, tab_jmeter_charts_rb, tab_jmeter_charts_perc = st.tabs(["Response Times", "Response Codes", "Received Bytes", "Percentile"])
            with tab_jmeter_charts_rt:
                # Aggregate the data to get the average 'elapsed' time for each 'timeStamp' and 'label' combination
                aggregated_data = st.session_state['raw_jmeter_data'].groupby(['timeStamp', 'label'])['elapsed'].mean().reset_index()
                
                # Pivot the aggregated data
                chart_data = aggregated_data.pivot(index='timeStamp', columns='label', values='elapsed')
                
                # Get a list of all unique labels
                all_labels = chart_data.columns.tolist()
                
                # Create a multiselect widget for label selection
                rt_selected_labels = st.multiselect('Select labels to display', all_labels, default=all_labels)
                
                # Filter the chart data based on the selected labels
                filtered_chart_data = chart_data[rt_selected_labels]
                
                st.caption("Transaction Response Times")
                st.line_chart(filtered_chart_data, use_container_width=True)
            
            with tab_jmeter_charts_rc:
                # Filter the raw data based on the selected labels
                filtered_data = st.session_state['raw_jmeter_data'][st.session_state['raw_jmeter_data']['label'].isin(rt_selected_labels)]
                
                # Count the total number of 'responseCode' for each unique response code and label
                grouped_data = filtered_data.groupby(['responseCode', 'label']).size().reset_index(name='count')
                
                # Pivot the grouped data so that each label becomes a separate column
                chart_data = grouped_data.pivot(index='responseCode', columns='label', values='count').fillna(0)
                
                st.caption("Response Codes")
                st.bar_chart(chart_data, use_container_width=True)
            
            with tab_jmeter_charts_rb:
                # Aggregate the data to get the average 'bytes' for each 'timeStamp' and 'label' combination
                aggregated_data = st.session_state['raw_jmeter_data'].groupby(['timeStamp', 'label'])['bytes'].mean().reset_index()

                # Pivot the aggregated data  
                chart_data = aggregated_data.pivot(index='timeStamp', columns='label', values='bytes')

                # Add a 'total_bytes' column that is the sum of all other columns
                chart_data['TOTAL BYTES'] = chart_data.sum(axis=1)

                # Get a list of all unique labels plus 'total_bytes'
                all_labels = chart_data.columns.tolist()

                # Create a multiselect widget for label selection with a unique key
                rb_selected_labels = st.multiselect('Select labels to display', all_labels, default=all_labels, key='rb_select')

                # Filter the chart data based on the selected labels
                filtered_chart_data = chart_data[rb_selected_labels]

                st.caption("Received Bytes")
                st.line_chart(filtered_chart_data, use_container_width=True)
                
            with tab_jmeter_charts_perc:
                # Create percentile charts for each label
                # Generate a sequence of percentiles from 0.01 to 1.00
                # Remove 'TOTAL_BYTES' from the list of labels
                all_labels = [label for label in all_labels if label != 'TOTAL BYTES']
            
                percentiles = np.arange(0.01, 1.01, 0.01)
            
                # Initialize an empty DataFrame to store the percentile values for each label
                percentile_values = pd.DataFrame({'percentile': percentiles})
            
                # Create a select box for time unit selection
                time_unit = st.selectbox('Select time unit', ['milliseconds', 'seconds'], key='time_unit_select')
            
                for label in all_labels:
                    # Filter the raw data based on the selected label
                    filtered_data = st.session_state['raw_jmeter_data'][st.session_state['raw_jmeter_data']['label'] == label]
                    
                    # Convert the 'elapsed' column to seconds if the user selects 'seconds'
                    if time_unit == 'seconds':
                        filtered_data['elapsed'] = filtered_data['elapsed'] / 1000
            
                    # Calculate the corresponding percentile values for the 'elapsed' column
                    label_percentile_values = filtered_data['elapsed'].quantile(percentiles)
                    
                    # Add the percentile values to the DataFrame
                    percentile_values[label] = label_percentile_values.values
            
                # Multiply the 'percentile' column by 100 and convert it to an integer
                percentile_values['percentile'] = (percentile_values['percentile'] * 100).astype(int)
            
                # Create a multiselect widget for label selection with a unique key
                selected_labels = st.multiselect('Select labels to display', all_labels, default=all_labels, key='percentile_select')
            
                # Filter the percentile values based on the selected labels
                filtered_percentile_values = percentile_values[['percentile'] + selected_labels]
            
                # Display the percentile chart
                st.caption(f"Response Time Percentile Range ({time_unit})")
                st.area_chart(filtered_percentile_values.set_index('percentile'), use_container_width=True)
                
if isPerfmonData:
    with tab_perfmon:
        pass
      
                
    with tab_correlation:
        # Load the perfmon data from the session state
        perfmon_data = st.session_state['perfmon_data']
                
        # Convert each column to float with 3 decimal places
        numeric_columns = perfmon_data.columns
        perfmon_data[numeric_columns] = perfmon_data[numeric_columns].apply(pd.to_numeric, errors='coerce')
        perfmon_data[numeric_columns] = perfmon_data[numeric_columns].round(3)
        
        # Aggregate the data by 'timeStamp' minute
        aggregated_data = perfmon_data.resample('min').mean()
        
        # Standardise the data
        standardised_data = (aggregated_data - aggregated_data.mean()) / aggregated_data.std()
        
        # Correlate each column against the other columns and present the top 10 correlated value pairs in a table
        correlation_matrix = standardised_data.corr()
        correlation_pairs = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates()
        correlation_pairs = correlation_pairs[correlation_pairs != 1]
        correlation_pairs = correlation_pairs.reset_index()
        correlation_pairs.columns = ['Metric A', 'Metric B', 'Correlation Value']
        
        # Convert the correlation value to a percentage and round to 3 decimal places
        correlation_pairs['Correlation Value'] = (correlation_pairs['Correlation Value'] * 100).round(3)

        left_column, middle_column, right_column = st.columns([1,2,1])
        
        # Filter the correlation pairs
        with middle_column:
            with st.container(border=1):
                # Get the minimum and maximum percentage from the user
                min_percentage, max_percentage = st.slider('Select a range of correlation values you want to view', min_value=0, max_value=100, value=(95, 100))      

                pos_filtered_correlation_pairs = correlation_pairs[(correlation_pairs['Correlation Value'] >= min_percentage) & (correlation_pairs['Correlation Value'] <= max_percentage)]
                neg_filtered_correlation_pairs = correlation_pairs[(correlation_pairs['Correlation Value'] <= (min_percentage * -1)) & (correlation_pairs['Correlation Value'] >= (max_percentage * -1))]
                positive_pair_count = len(pos_filtered_correlation_pairs)
                negative_pair_count = len(neg_filtered_correlation_pairs)
                # st.write(f"There are {positive_pair_count} positive and {negative_pair_count} negative correlations between {min_percentage}% and {max_percentage}%")
        
        
        positive_correlations, negative_correlations= st.tabs([f"{positive_pair_count} Positive Correlations", f"{negative_pair_count} Negative Correlations"])
        
        with positive_correlations:
            st.subheader(f"{ 'No' if positive_pair_count == 0 else positive_pair_count } Positive Correlations{ '.' if positive_pair_count == 0 else ':' } ")
            # Create a list to store the positive_pair columns
            pos_columns = [st.columns(2) for _ in range(positive_pair_count + 1 // 2)]
        

            # Iterate over the positive filtered correlation pairs
            for i, (_, row) in enumerate(pos_filtered_correlation_pairs.iterrows()):
                # Get the pair of metrics
                metric_a = row['Metric A']
                metric_b = row['Metric B']
            
                # Create a DataFrame with the pair of metrics
                pos_pair_data = standardised_data[[metric_a, metric_b]]
            
                # Create a line chart for the pair of metrics in the appropriate column
                with pos_columns[i // 2][i % 2]:
                    
                    # Create a line chart for the pair of metrics in the appropriate column
                    posfig = go.Figure()
                    
                    # Add an annotation to the chart of the correlation value and make the font 
                    posfig.add_annotation(
                        x=1,
                        y=1.1,
                        xref='paper',
                        yref='paper',
                        text=f"Correlation Score: {row['Correlation Value']}%",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="white"
                        )
                    )
                    posfig.update_layout(
                        # Update the layout to place the legend at the bottom
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        ),
                            # Add a white border around the plot area
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    ) 
                    
                    # Add a white border around the x and y axes
                    posfig.update_xaxes(showline=True, linewidth=1, linecolor='white', mirror=True)
                    posfig.update_yaxes(showline=True, linewidth=1, linecolor='white', mirror=True)


                    posfig.add_trace(go.Scatter(x=pos_pair_data.index, y=pos_pair_data[metric_a], mode='lines', name=metric_a))
                    posfig.add_trace(go.Scatter(x=pos_pair_data.index, y=pos_pair_data[metric_b], mode='lines', name=metric_b))

                    st.plotly_chart(posfig)
        
        with negative_correlations:
            st.subheader(f"{ 'No' if negative_pair_count == 0 else negative_pair_count } Negative Correlations{ '.' if negative_pair_count == 0 else ':' } ")
            neg_columns = [st.columns(2) for _ in range(negative_pair_count + 1 // 2)]
            
            # Iterate over the negative filtered correlation pairs
            for i, (_, row) in enumerate(neg_filtered_correlation_pairs.iterrows()):
                # Get the pair of metrics
                metric_a = row['Metric A']
                metric_b = row['Metric B']
            
                # Create a DataFrame with the pair of metrics
                neg_pair_data = standardised_data[[metric_a, metric_b]]
            
                # Create a line chart for the pair of metrics in the appropriate column
                with neg_columns[i // 2][i % 2]:
                    # Create a line chart for the pair of metrics in the appropriate column
                    negfig = go.Figure()
                    
                    # Add an annotation to the chart of the correlation value and make the font 
                    
                    negfig.add_annotation(
                        x=1,
                        y=1.1,
                        xref='paper',
                        yref='paper',
                        text=f"Correlation Score: {row['Correlation Value']}%",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="white"
                        )
                    )
                    negfig.update_layout(
                        # Update the layout to place the legend at the bottom
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        ),
                            # Add a white border around the plot area
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    ) 
                    
                    # Add a white border around the x and y axes
                    negfig.update_xaxes(showline=True, linewidth=1, linecolor='white', mirror=True)
                    negfig.update_yaxes(showline=True, linewidth=1, linecolor='white', mirror=True)

                    negfig.add_trace(go.Scatter(x=neg_pair_data.index, y=neg_pair_data[metric_a], mode='lines', name=metric_a))
                    negfig.add_trace(go.Scatter(x=neg_pair_data.index, y=neg_pair_data[metric_b], mode='lines', name=metric_b))

                    st.plotly_chart(negfig)