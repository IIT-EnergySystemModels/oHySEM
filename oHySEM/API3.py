import datetime
import streamlit as st
import pandas as pd
import altair as alt
import os
import subprocess

# Set the page config
st.set_page_config(page_title="oHySEM Dashboard", layout="wide")

# Display an image from a URL
image_url = "https://pascua.iit.comillas.edu/aramos/oHySEM_v2.png"
st.image(image_url, caption="")

DirName = os.path.dirname(__file__)
CaseName = 'VPP1'

title_fontsize = 20
subtitle_fontsize = 19
text_fontsize = 18
label_fontsize = 16

st.write("This dashboard provides a workflow for analyzing input data, executing the oHySEM model, and visualizing the results.")

# Set up dashboard title
st.title("Model's Arguments")

# Arguments
arg_defaults = {
    'dir_name': DirName,
    'case_name': CaseName,
    'solver': 'gurobi',
    'date': datetime.datetime.now().replace(second=0, microsecond=0),
    'raw_results': False,
    'plot_results': False,
    'time_steps': 24,
    # 'h2_target': 3.0,
    # 'delivery_type': 'Daily'
}

# Initialize session states with defaults
for key, value in arg_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Helper function for default handling
def handle_input(label, default_value, state_key, input_type=str, placeholder=None, disabled_label="Adopt default"):
    checkbox = st.checkbox(f"{disabled_label} for {label.lower()}", key=f"disable_{state_key}")
    if checkbox:
        st.session_state[state_key] = default_value
    else:
        st.session_state[state_key] = st.text_input(label, value=str(st.session_state[state_key]), placeholder=placeholder, disabled=False) if input_type == str else st.number_input(label, value=st.session_state[state_key])

# User inputs
col1, col2, col3 = st.columns(3)

with col1:
    handle_input("Directory Path", DirName, 'dir_name', placeholder="Enter the path")
    st.write("Path: ", st.session_state['dir_name'])

    handle_input("Date", arg_defaults['date'], 'date', placeholder="Enter initial date (YYYY-MM-DD HH:MM:SS)")
    st.write("Date: ", st.session_state['date'])

    handle_input("Time Steps", arg_defaults['time_steps'], 'time_steps', input_type=int)
    st.write("Time Steps: ", st.session_state['time_steps'])

with col2:
    handle_input("Case Name", CaseName, 'case_name', placeholder="Enter case")
    st.write("Case: ", st.session_state['case_name'])

    st.session_state['raw_results'] = st.checkbox("Save the raw results", value=st.session_state['raw_results'])
    st.write("Save raw results: ", st.session_state['raw_results'])

    # handle_input("H2 Target Demand", arg_defaults['h2_target'], 'h2_target', input_type=float)
    # st.write("H2 Target Demand: ", st.session_state['h2_target'])

with col3:
    handle_input("Solver", "gurobi", 'solver', placeholder="Enter solver (e.g., gurobi, glpk)")
    st.write("Solver: ", st.session_state['solver'])

    st.session_state['plot_results'] = st.checkbox("Save the plot results", value=st.session_state['plot_results'])
    st.write("Save plot results: ", st.session_state['plot_results'])
    # # handle_input with dropdown menu
    # handle_input("H2 Delivery Type", arg_defaults['delivery_type'], 'delivery_type', input_type=str, placeholder="Enter delivery type (e.g., hourly, daily, etc.)")
    # st.write("H2 Delivery Type: ", st.session_state['delivery_type'])

# Helper function to load CSVs
# @st.cache_data
def load_csv(file_name, idx_col):
    cols = []
    for i in range(idx_col):
        cols.append(i)
    return pd.read_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], file_name), index_col=cols)

df_duration = load_csv('oH_Data_Duration_{}.csv'.format(st.session_state['case_name']), 1)
df_hydrogen_demand = load_csv('oH_Data_HydrogenDemand_{}.csv'.format(st.session_state['case_name']), 3)

# if st.session_state['date'] is a string, transform it to a datetime object
if isinstance(st.session_state['date'], str):
    st.session_state['date'] = datetime.datetime.strptime(st.session_state['date'], '%Y-%m-%d %H:%M:%S')

# transform arg_defaults['date'] to a string loadlevel of format 't{hour}:04d'
hour_of_year = st.session_state['date'].timetuple().tm_yday * 24 + st.session_state['date'].timetuple().tm_hour
loadlevel = f't{hour_of_year:04d}'

# fill zeros in column 'Duration' from index 't0001' to index equal to loadlevel
df_duration.loc['t0001':loadlevel, 'Duration'] = 0

time_steps = st.session_state['time_steps']

# fill ones in column 'Duration' from index equal to number of hours in a year to index equal to loadlevel + time_step
df_duration.loc[loadlevel:f't{(hour_of_year+time_steps):04d}', 'Duration'] = 1

# fill zeros from hour_of_year + time_step to the end of the dataframe
df_duration.loc[f't{(hour_of_year+time_steps):04d}':, 'Duration'] = 0

# fill blank in all the columns of df_hydrogen_demand
df_hydrogen_demand.loc[(slice(None), slice(None), slice(None))] = ''

# modify in all the columns of df_hydrogen_demand in the third level of the index equal to loadlevel
df_hydrogen_demand.loc[(slice(None), slice(None), loadlevel), 'Node4'] = 0.1

# Save the modified dataset
if st.button('Save the modified time steps'):
    df_duration.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], 'oH_Data_Duration_{}.csv'.format(st.session_state['case_name'])), index=True)
    df_hydrogen_demand.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], 'oH_Data_HydrogenDemand_{}.csv'.format(st.session_state['case_name'])), index=True)
    st.success("Time steps saved successfully!")

# Dataset visualization
st.title("Visualizing the Time Series Data")

datasets = {
    'Electricity Cost': 'oH_Data_ElectricityCost_{}.csv',
    'Electricity Demand': 'oH_Data_ElectricityDemand_{}.csv',
    'Electricity Price': 'oH_Data_ElectricityPrice_{}.csv',
    'Hydrogen Cost': 'oH_Data_HydrogenCost_{}.csv',
    'Hydrogen Demand': 'oH_Data_HydrogenDemand_{}.csv',
    'Hydrogen Price': 'oH_Data_HydrogenPrice_{}.csv',
    'Variable Max Generation': 'oH_Data_VarMaxGeneration_{}.csv'
}

dataset = st.selectbox('Select a dataset to view:', list(datasets.keys()))

df = load_csv(datasets[dataset].format(st.session_state['case_name']),3)
# filter the dataframe since the second index has to be equal betwen the range of loadlevel and loadlevel + time_steps. the dataframe has 3 levels of index
df = df.loc[(slice(None), slice(None), slice(loadlevel, f't{(hour_of_year+time_steps):04d}')), :]
# stack the dataframe
df = df.stack().reset_index().rename(columns={0: 'Value', 'level_3': 'Component'})

# Add DateTime column
df['DateTime'] = pd.date_range(start=st.session_state['date'], periods=len(df), freq='H')

# Plotting input data
st.subheader(f"{dataset} Over Time")
line_chart = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(filled=False, fill="white")).encode(
    x=alt.X('DateTime:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
    y='Value:Q',
    color='Component:N'
).properties(width=700, height=400).configure_axis(
                    labelFontSize=label_fontsize,
                    titleFontSize=title_fontsize
                )

st.altair_chart(line_chart, use_container_width=True)

# reading, modifying and saving the input data
st.title("Modification H2 Delivery Data")

# Helper function to load CSVs
# @st.cache_data

datasets_par = {
    'Parameter': f'oH_Data_Parameter_{st.session_state["case_name"]}.csv',
}

dataset_par = st.selectbox('Select a dataset to modify:', list(datasets_par.keys()))

df = load_csv(datasets_par[dataset_par], 1)

# # Display the columns ('DemandType', 'TargetDemand', 'RampDemand') of the dataset and the first few rows
# st.write(df[['DemandType', 'TargetDemand', 'RampDemand']].head())

# Modify the dataset
st.write("Modify the dataset below:")
modified_df = df.copy()
# User inputs
col1, col2, col3 = st.columns(3)

with col1:
    # modified_df['DemandType'] = st.text_input("Enter the demand type", value=modified_df['DemandType'][0])
    modified_df['DemandType'] = st.selectbox('Select a demand type:', list(['Hourly', 'Daily', 'Weekly']))

with col2:
    modified_df['TargetDemand'] = st.number_input("Enter the target demand", value=modified_df['TargetDemand'][0])

with col3:
    modified_df['RampDemand'] = st.number_input("Enter H2 Demand Ramp", value=modified_df['RampDemand'][0])

# Save the modified dataset
if st.button('Save the modified dataset'):
    modified_df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_par[dataset_par]), index=True)
    st.success("Dataset saved successfully!")
    st.write(modified_df[['DemandType', 'TargetDemand', 'RampDemand']].head())

# reading, modifying and saving the input data
st.title("Modification Electrolyzer Data")

datasets_gen = {
    'Electrolyzer': f'oH_Data_Generation_{st.session_state["case_name"]}.csv',
}

# modify the dataset
df = load_csv(datasets_gen['Electrolyzer'], 1)

st.write("Modify the dataset below:")
modified_df = df.copy()

# select the unit
unit = st.selectbox('Select a unit:', list(modified_df.index))

# User inputs
col1, col2, col3, col4, col5 = st.columns(5)

# Model execution
st.title("Problem Solving")
if st.button('Launch the model'):
    st.write(f'Solving oHySEM with the following arguments: ')
    st.write(f'Directory: {st.session_state["dir_name"]}')
    st.write(f'Case: {st.session_state["case_name"]}')
    st.write(f'Solver: {st.session_state["solver"]}')
    st.write(f'Date: {st.session_state["date"]}')
    st.write(f'Save raw results: {st.session_state["raw_results"]}')
    st.write(f'Save plot results: {st.session_state["plot_results"]}')


    # Basic validation (example, customize based on your needs)
    def validate_input(input_str):
        # Check for forbidden characters or patterns
        if any(char in input_str for char in [';', '&', '|', '$']):
            raise ValueError(f"Invalid input detected: {input_str}")
        return input_str


    # Validate inputs
    dir_name = validate_input(st.session_state['dir_name'])
    case_name = validate_input(st.session_state['case_name'])
    solver = validate_input(st.session_state['solver'])

    command = [
        'python', 'oHySEM.py',
        '--dir', dir_name,
        '--case', case_name,
        '--solver', solver,
        '--date', str(st.session_state['date']),
        '--rawresults', str(st.session_state['raw_results']),
        '--plots', str(st.session_state['plot_results'])
    ]

    # Run the subprocess
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        st.success("oHySEM finished running successfully!")
    else:
        st.error(f"Error executing oHySEM: {result.stderr}")
    if result.returncode == 0:
        # Plotting Results
        st.title("Operational Overview")

        # Load result CSVs
        # @st.cache_data
        def load_result_csv(file_name):
            return pd.read_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], file_name))

        hydrogen_balance = load_result_csv(f'oH_Result_rHydrogenBalance_{st.session_state["case_name"]}.csv')
        electricity_balance = load_result_csv(f'oH_Result_rElectricityBalance_{st.session_state["case_name"]}.csv')
        total_cost = load_result_csv(f'oH_Result_rTotalCost_{st.session_state["case_name"]}.csv')

        # Filter unnecessary rows
        hydrogen_balance = hydrogen_balance[~hydrogen_balance['Component'].isin(['HydrogenFlowIn', 'HydrogenFlowOut', 'Wind', 'BESS'])]
        electricity_balance = electricity_balance[~electricity_balance['Component'].isin(['PowerFlowIn', 'PowerFlowOut'])]

        # Key Performance Indicators (KPIs)
        st.subheader("Key Performance Indicators")

        total_cost_value = total_cost['MEUR'].sum()
        total_hydrogen = hydrogen_balance[hydrogen_balance['Component'] == 'H2ESS']['tH2'].sum()
        total_electricity = electricity_balance['GWh'].sum()

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Total Cost (MEUR)", value=f"{total_cost_value:.2f}")
        kpi2.metric(label="Total Hydrogen Storage (tH2)", value=f"{total_hydrogen:.2f}")
        kpi3.metric(label="Total Electricity Generation (GWh)", value=f"{total_electricity:.2f}")

        # Creating a layout for energy balances and network flows
        st.subheader("Cost and Profits Overview")
        with st.container():
            # Two columns: One for the cost and profits along the date and one as a pie chart
            col1, col2 = st.columns(2)

            # Total Cost Line Chart
            with col1:
                st.subheader("Total Cost Over Time")
                cost_chart = alt.Chart(total_cost).mark_bar().encode(
                    x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                    y='MEUR:Q',
                    color='Component:N'
                ).properties(width=700, height=400).configure_axis(
                    labelFontSize=label_fontsize,
                    titleFontSize=title_fontsize
                )
                st.altair_chart(cost_chart, use_container_width=True)

            # Donut chart
            with col2:
                # Total Cost Breakdown with handling of negative values
                st.header("Total Cost and Profit Breakdown")

                def create_donut_charts(data):

                    # Filter positive values (costs)
                    costs = data[data['MEUR'] >= 0].groupby('Component')['MEUR'].sum().reset_index()
                    costs['Percentage'] = costs['MEUR'] / costs['MEUR'].sum() * 100

                    # Filter negative values (profits)
                    profits = data[data['MEUR'] < 0].groupby('Component')['MEUR'].sum().reset_index()
                    profits['Percentage'] = profits['MEUR'] / profits['MEUR'].sum() * 100
                    profits['MEUR'] = profits['MEUR'].abs()  # Convert profits to positive values for display

                    # Helper function to create individual donut chart with labels
                    def create_donut_chart(df, title):
                        # Create the donut chart
                        donut_chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
                            theta=alt.Theta(field="MEUR", type="quantitative"),
                            color=alt.Color(field="Component", type="nominal"),
                            tooltip=['Component', 'MEUR', 'Percentage']
                        ).properties(
                            width=400,
                            height=300,
                            title=title
                        )

                        # Add labels to the donut chart showing both percentage and MEUR
                        labels = alt.Chart(df).mark_text(radius=200, size=text_fontsize).encode(
                            theta=alt.Theta(field="MEUR", type="quantitative"),
                            text=alt.Text(field="label", type="nominal"),
                            color=alt.value('black')  # Ensures the label color is consistent
                        )

                        return donut_chart + labels

                    # Add a label column that combines MEUR and Percentage
                    costs['label'] = costs.apply(lambda row: f'{row["MEUR"]:.1f} MEUR ({row["Percentage"]:.1f}%)',
                                                 axis=1)
                    profits['label'] = profits.apply(lambda row: f'{row["MEUR"]:.1f} MEUR ({row["Percentage"]:.1f}%)',
                                                     axis=1)

                    # Create donut charts for costs and profits
                    cost_donut_chart = create_donut_chart(costs, "Costs")
                    profit_donut_chart = create_donut_chart(profits, "Profits")

                    # Display both charts side by side
                    chart = cost_donut_chart | profit_donut_chart

                    return chart

                # Display the chart in Streamlit
                st.altair_chart(create_donut_charts(total_cost))


        # Energy Balance and Network Flows
        st.subheader("Energy Balance Overview")
        col1, col2 = st.columns(2)

        # Hydrogen Balance Line Chart
        with col2:
            st.subheader("Hydrogen Balance Over Time")
            hydrogen_chart = alt.Chart(hydrogen_balance).mark_bar().encode(
                x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                y='tH2:Q',
                color='Component:N'
            ).properties(width=700, height=400).configure_axis(
                    labelFontSize=label_fontsize,
                    titleFontSize=title_fontsize
                )
            st.altair_chart(hydrogen_chart, use_container_width=True)

        # Electricity Balance Line Chart
        with col1:
            st.subheader("Electricity Balance Over Time")
            electricity_chart = alt.Chart(electricity_balance).mark_bar().encode(
                x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                y='GWh:Q',
                color='Component:N'
            ).properties(width=700, height=400).configure_axis(
                    labelFontSize=label_fontsize,
                    titleFontSize=title_fontsize
                )
            st.altair_chart(electricity_chart, use_container_width=True)

st.write("Dashboard created for analyzing oHySEM results.")
