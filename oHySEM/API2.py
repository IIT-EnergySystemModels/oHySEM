import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import os
import subprocess

# Set the page config to use the full width of the screen
st.set_page_config(page_title="oHySEM Results Dashboard", layout="wide")

DirName = os.path.dirname(__file__)
CaseName = 'VPP1'

# Set up dashboard title
st.title("oHySEM Dashboard")
st.write("This dashboard provides a workflow for analysing some input data, executing the oHySEM model, and visualizing the results.")

# st.header("Metadata")
# st.subheader("Path")


st.header("oHySEM Execution")
st.subheader("Arguments")

arg1 = DirName
arg2 = CaseName
arg3 = ""
arg4 = datetime.datetime.now().replace(second=0, microsecond=0)
arg5 = ""
arg6 = ""
arg7 = 24

# Store the initial state of widgets in session state if not already initialized
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled_col1_row1 = False
    st.session_state.disabled_col1_row2 = False
    st.session_state.disabled_col1_row3 = False
    st.session_state.disabled_col2_row1 = False
    st.session_state.disabled_col2_row2 = False
    st.session_state.disabled_col3_row1 = False
    st.session_state.disabled_col3_row2 = False

# Define the columns
col1, col2, col3 = st.columns(3)

with col1:
    # Checkbox to control the disabled state of the input widget in column 1, row 1
    checkbox_text_1_row1 = st.checkbox("Adopt default value for the dir name", key="disable_widget_col1_row1")

    # Update session state for disabled status of col1
    st.session_state.disabled_col1_row1 = checkbox_text_1_row1

    # Set the default value if the checkbox is checked, otherwise allow the user to input their own value
    if st.session_state.disabled_col1_row1:
        input_text_1_row1 = st.text_input(
            "Enter path 👇",
            value="Default",
            label_visibility=st.session_state.visibility,
            disabled=True,
        )
    else:
        input_text_1_row1 = st.text_input(
            "Enter path 👇",
            label_visibility=st.session_state.visibility,
            disabled=False,
            placeholder="Enter the path",
        )
    if input_text_1_row1 != "Default":
        arg1 = input_text_1_row1
    st.write("Path: ", arg1)

    # Checkbox to control the disabled state of the input widget in column 1, row 2
    checkbox_text_1_row2 = st.checkbox("Adopt default value for the date", key="disable_widget_col1_row2")

    # Update session state for disabled status of col1
    st.session_state.disabled_col1_row2 = checkbox_text_1_row2

    # Set the default value if the checkbox is checked, otherwise allow the user to input their own value
    if st.session_state.disabled_col1_row2:
        input_text_1_row2 = st.text_input(
            "Enter date 👇: (YYYY-MM-DD HH:MM:SS)",
            value="Default",
            label_visibility=st.session_state.visibility,
            disabled=True,
        )
    else:
        input_text_1_row2 = st.text_input(
            "Enter date 👇: (YYYY-MM-DD HH:MM:SS)",
            label_visibility=st.session_state.visibility,
            disabled=False,
            placeholder="Enter the date",
        )
    if input_text_1_row2 != "Default":
        arg4 = input_text_1_row2
    st.write("Date: ", arg4)

    # Checkbox to control the disabled state of the input widget in column 1, row 3
    checkbox_text_1_row3 = st.checkbox("Adopt default value for the raw results", key="disable_widget_col1_row3")

    # Update session state for disabled status of col1
    st.session_state.disabled_col1_row3 = checkbox_text_1_row3

    # Set the default value if the checkbox is checked, otherwise allow the user to input their own value
    if st.session_state.disabled_col1_row3:
        input_text_1_row3 = st.text_input(
            "Enter the number of time steps or hour 👇: (Default: 24)",
            value="Default",
            label_visibility=st.session_state.visibility,
            disabled=True,
        )
    else:
        input_text_1_row3 = st.text_input(
            "Enter the number of time steps or hour 👇: (Default: 24)",
            label_visibility=st.session_state.visibility,
            disabled=False,
            placeholder="Enter the number of time steps or hour",
        )
    if input_text_1_row3 != "Default":
        arg7 = input_text_1_row3
    st.write("Number of time steps: ", arg7)

    # # Assume each row represents one hour, and set a start date
    # start_date = st.date_input('Select start date:', datetime(2024, 1, 1).date())
    #
    # # Select Date, Hour, Day, and Week
    # selected_hour = st.slider('Select the hour of the day:', 0, 23, 12)
    # selected_day = st.slider('Select the day within the week:', 1, 7, 1)
    # selected_week = st.slider('Select the week within the year:', 1, 52, 1)
    #
    # st.write(f'Selected Date: {start_date}, Hour: {selected_hour}, Day: {selected_day}, Week: {selected_week}')

with col2:
    # Checkbox to control the disabled state of the input widget in column 2
    checkbox_text_2_row1 = st.checkbox("Adopt default value for case name", key="disable_widget_col2_row1")

    # Update session state for disabled status of col2
    st.session_state.disabled_col2_row1 = checkbox_text_2_row1

    # Set the default value if the checkbox is checked, otherwise allow the user to input their own value
    if st.session_state.disabled_col2_row1:
        input_text_2_row1 = st.text_input(
            "Enter case 👇",
            value="Default",
            label_visibility=st.session_state.visibility,
            disabled=True,
        )
    else:
        input_text_2_row1 = st.text_input(
            "Enter case 👇",
            label_visibility=st.session_state.visibility,
            disabled=False,
            placeholder="Enter the case",
        )
    if input_text_2_row1 != "Default":
        arg2 = input_text_2_row1
    st.write("Case: ", arg2)

    # Checkbox to control the disabled state of the input widget in column 2, row 2
    checkbox_text_2_row2 = st.checkbox("Save the raw results: True or False ", key="disable_widget_col2_row2")

    # Update session state for disabled status of col2
    st.session_state.disabled_col2_row2 = checkbox_text_2_row2

    st.write("Value: ", st.session_state.disabled_col2_row2)
    arg5 = st.session_state.disabled_col2_row2

with col3:
    # Checkbox to control the disabled state of the input widget in column 3
    checkbox_text_3_row1 = st.checkbox("Adopt default value for the solver name", key="disable_widget_col3_row1")

    # Update session state for disabled status of col3
    st.session_state.disabled_col3_row1 = checkbox_text_3_row1

    # Set the default value if the checkbox is checked, otherwise allow the user to input their own value
    if st.session_state.disabled_col3_row1:
        input_text_3_row1 = st.text_input(
            "Enter solver 👇: (gurobi, glpk, appsi_highs,etc.)",
            value="Default",
            label_visibility=st.session_state.visibility,
            disabled=True,
        )
    else:
        input_text_3_row1 = st.text_input(
            "Enter solver 👇: (gurobi, glpk, appsi_highs,etc.)",
            label_visibility=st.session_state.visibility,
            disabled=False,
            placeholder="Enter the model",
        )
    if input_text_3_row1 == "Default":
        arg3 = ""
    else:
        arg3 = input_text_3_row1
    st.write("Solver: ", arg3)

    # Checkbox to control the disabled state of the input widget in column 3, row 2
    checkbox_text_3_row2 = st.checkbox("Save the plot results: True or False", key="disable_widget_col3_row2")

    # Update session state for disabled status of col3
    st.session_state.disabled_col3_row2 = checkbox_text_3_row2

    st.write("Value: ", st.session_state.disabled_col3_row2)
    arg6 = st.session_state.disabled_col3_row2

st.subheader("Visualizing the Input Data")

# Load CSV files
ele_cost = pd.read_csv(os.path.join(DirName, CaseName, f'oH_Data_ElectricityCost_{arg2}.csv'), index_col=[0,1,2])
ele_demand = pd.read_csv(os.path.join(DirName, CaseName, f'oH_Data_ElectricityDemand_{arg2}.csv'), index_col=[0,1,2])
ele_price = pd.read_csv(os.path.join(DirName, CaseName, f'oH_Data_ElectricityPrice_{arg2}.csv'), index_col=[0,1,2])
hyd_cost = pd.read_csv(os.path.join(DirName, CaseName, f'oH_Data_HydrogenCost_{arg2}.csv'), index_col=[0,1,2])
hyd_demand = pd.read_csv(os.path.join(DirName, CaseName, f'oH_Data_HydrogenDemand_{arg2}.csv'), index_col=[0,1,2])
hyd_price = pd.read_csv(os.path.join(DirName, CaseName, f'oH_Data_HydrogenPrice_{arg2}.csv'), index_col=[0,1,2])
var_max_gen = pd.read_csv(os.path.join(DirName, CaseName, f'oH_Data_VarMaxGeneration_{arg2}.csv'), index_col=[0,1,2])

# Dropdown to select dataset
dataset = st.selectbox('Select a dataset to view:',
                       ['Electricity Cost', 'Electricity Demand', 'Electricity Price',
                        'Hydrogen Cost', 'Hydrogen Demand', 'Hydrogen Price', 'Variable Max Generation'])

if dataset == 'Electricity Cost':
    df = ele_cost
elif dataset == 'Electricity Demand':
    df = ele_demand
elif dataset == 'Electricity Price':
    df = ele_price
elif dataset == 'Hydrogen Cost':
    df = hyd_cost
elif dataset == 'Hydrogen Demand':
    df = hyd_demand
elif dataset == 'Hydrogen Price':
    df = hyd_price
elif dataset == 'Variable Max Generation':
    df = var_max_gen

# select the first 'arg7' rows of df
df = df.head(int(arg7))

df = df.stack().reset_index()

# rename column 0 to 'Value', and level_3 to 'Component'
df = df.rename(columns={0: 'Value', 'level_3': 'Component'})

# Assume each row represents one hour, and set a start date for the x-axis which is the arg4
start_date = arg4

# Generate a DateTime index assuming hourly intervals
time_index = pd.date_range(start=start_date, periods=len(df), freq='H')

df['DateTime'] = time_index

# Plot the selected dataset
st.subheader(f"{dataset} Over Time")
st.write(df)

# Create a line chart using Altair
line_chart = alt.Chart(df).mark_line().encode(
    x=alt.X('DateTime:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
    y=alt.Y('Value:Q', axis=alt.Axis(title='Value')),
    color='Component:N'
).properties(width=700, height=400).configure_axis(
    labelFontSize=16,
    titleFontSize=20
)

# Display the chart in Streamlit
st.altair_chart(line_chart, use_container_width=True)


st.subheader("Problem Solving")
if st.button('Launch the model'):
    st.write(f'Solving oHySEM with the following arguments: {arg1}, {arg2}, {arg3}, {arg4}, {arg5}, {arg6}')

    # Convert the boolean arg6 to a string ('True' or 'False')
    arg4 = str(arg4)
    arg5 = str(arg5)
    arg6 = str(arg6)

    # Create the command string
    command = [
        'python', 'oHySEM.py',
        '--dir', arg1,
        '--case', arg2,
        '--solver', arg3,
        '--date', arg4,
        '--rawresults', arg5,
        '--plots', arg6
    ]

    # Run the command using subprocess
    result = subprocess.run(command, capture_output=True, text=True)

    # Check the result of the command
    if result.returncode == 0:
        st.success("oHySEM finished running successfully!")
        # st.write(result.stdout)
    else:
        st.error(f"Error executing oHySEM: {result.stderr}")

    # # Show a message indicating that the script finished running
    # st.info("The Python script has finished executing.")
    if result.returncode == 0:
        st.header("Operational Overview")

        # Load CSV files
        hydrogen_balance = pd.read_csv(os.path.join(arg1, arg2, f'oH_Result_rHydrogenBalance_{arg2}.csv'))
        hydrogen_flows = pd.read_csv(os.path.join(arg1, arg2, f'oH_Result_rHydrogenNetworkFlows_{arg2}.csv'))
        reserves_offers = pd.read_csv(os.path.join(arg1, arg2, f'oH_Result_rReservesOffers_{arg2}.csv'))
        total_cost = pd.read_csv(os.path.join(arg1, arg2, f'oH_Result_rTotalCost_{arg2}.csv'))
        electricity_balance = pd.read_csv(os.path.join(arg1, arg2, f'oH_Result_rElectricityBalance_{arg2}.csv'))
        electricity_flows = pd.read_csv(os.path.join(arg1, arg2, f'oH_Result_rElectricityNetworkFlows_{arg2}.csv'))
        electricity_generation = pd.read_csv(os.path.join(arg1, arg2, f'oH_Result_rElectricityTechnologyGeneration_{arg2}.csv'))

        # remove rows with 'HydrogenFlowIn' and 'HydrogenFlowOut' from hydrogen_balance
        hydrogen_balance = hydrogen_balance[~hydrogen_balance['Component'].isin(['HydrogenFlowIn', 'HydrogenFlowOut'])]
        # remove rows with 'ElectricityFlowIn' and 'ElectricityFlowOut' from electricity_balance
        electricity_balance = electricity_balance[~electricity_balance['Component'].isin(['PowerFlowIn', 'PowerFlowOut'])]

        # filter number different from zero
        total_cost = total_cost[total_cost['MEUR'] != 0]

        title_fontsize = 20
        subtitle_fontsize = 19
        text_fontsize = 18
        label_fontsize = 16

        # Key Performance Indicators (KPIs)
        st.subheader("Key Performance Indicators")

        total_cost_value = total_cost['MEUR'].sum()
        # sum of hydrogen storage in tH2 from rows with 'H2ESS' in 'Component' column
        total_hydrogen = hydrogen_balance[hydrogen_balance['Component'] == 'H2ESS']['tH2'].sum()
        # total_hydrogen = hydrogen_balance['tH2'].sum()
        total_electricity = electricity_generation['MW'].sum()

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Total Cost (MEUR)", value=f"{total_cost_value:.2f}")
        kpi2.metric(label="Total Hydrogen Storage (tH2)", value=f"{total_hydrogen:.2f}")
        kpi3.metric(label="Total Electricity Generation (MW)", value=f"{total_electricity:.2f}")

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

                # # Filter out negative values
                # cost_breakdown = total_cost[total_cost['MEUR'] >= 0].groupby('Component')['MEUR'].sum().reset_index()
                #
                # # Calculate percentage values
                # cost_breakdown['Percentage'] = cost_breakdown['MEUR'] / cost_breakdown['MEUR'].sum() * 100
                #
                # # Create a donut chart using Altair
                # donut_chart = alt.Chart(cost_breakdown).mark_arc(innerRadius=50).encode(
                #     theta=alt.Theta(field="MEUR", type="quantitative"),
                #     color=alt.Color(field="Component", type="nominal"),
                #     tooltip=['Component', 'MEUR', 'Percentage']
                # ).properties(
                #     width=400,
                #     height=300
                # )
                #
                # # Add percentage labels in the center of each arc with increased font size
                # labels = alt.Chart(cost_breakdown).mark_text(radius=90, size=text_fontsize).encode(
                #     theta=alt.Theta(field="MEUR", type="quantitative"),
                #     text=alt.Text(field="Percentage", type="quantitative", format=".1f"),  # Format as percentage with 1 decimal
                #     color=alt.value('black')
                # )
                #
                # # Combine the donut chart and percentage labels
                # donut_with_labels = donut_chart + labels
                #
                # # Display the chart in Streamlit
                # st.altair_chart(donut_with_labels)

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


        st.header("Energy and Network Flows Overview")
        with st.container():
            # Two columns: One for hydrogen balance and flows, one for electricity balance and flows
            col1, col2 = st.columns(2)

            # Hydrogen Balance Line Chart
            with col1:
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

                # # Hydrogen Network Flows
                # st.subheader("Hydrogen Network Flows")
                # hydrogen_flows_chart = alt.Chart(hydrogen_flows).mark_bar().encode(
                #     x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                #     y='MW:Q',
                #     color='InitialNode:N'
                # ).properties(width=700, height=400).configure_axis(
                #     labelFontSize=label_fontsize,
                #     titleFontSize=title_fontsize
                # )
                # st.altair_chart(hydrogen_flows_chart, use_container_width=True)
                #
                # # Reserve Offers Section
                # st.subheader("Reserve Offers Overview")
                # reserve_chart = alt.Chart(reserves_offers).mark_bar().encode(
                #     x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                #     y='MW:Q',
                #     color='Component:N'
                # ).properties(width=1400, height=400).configure_axis(
                #     labelFontSize=label_fontsize,
                #     titleFontSize=title_fontsize
                # )
                # st.altair_chart(reserve_chart, use_container_width=True)

            # Electricity Balance Line Chart
            with col2:
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

                # # Electricity Network Flows
                # st.subheader("Electricity Network Flows")
                # electricity_flows_chart = alt.Chart(electricity_flows).mark_bar().encode(
                #     x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                #     y='MW:Q',
                #     color='InitialNode:N'
                # ).properties(width=700, height=400).configure_axis(
                #     labelFontSize=label_fontsize,
                #     titleFontSize=title_fontsize
                # )
                # st.altair_chart(electricity_flows_chart, use_container_width=True)
                #
                # # # Total Cost Breakdown with handling of negative values
                # # st.header("Total Cost Breakdown")
                # # cost_breakdown = total_cost[total_cost['MEUR'] >= 0].groupby('Component')['MEUR'].sum().reset_index()
                # #
                # # fig, ax = plt.subplots(figsize=(2, 1.5))
                # # ax.pie(cost_breakdown['MEUR'], labels=cost_breakdown['Component'], autopct='%1.1f%%', startangle=90)
                # # ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                # # st.pyplot(fig)

# Footer
st.write("Dashboard created for analyzing oHySEM results.")
