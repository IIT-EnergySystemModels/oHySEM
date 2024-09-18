from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import os

# Set the page config to use the full width of the screen
st.set_page_config(page_title="oHySEM Results Dashboard", layout="wide")

DirName = os.path.dirname(__file__)
CaseName = 'VPP1'

# Load CSV files
hydrogen_balance = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rHydrogenBalance_VPP1.csv'))
hydrogen_flows = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rHydrogenNetworkFlows_VPP1.csv'))
reserves_offers = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rReservesOffers_VPP1.csv'))
total_cost = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rTotalCost_VPP1.csv'))
electricity_balance = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rElectricityBalance_VPP1.csv'))
electricity_flows = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rElectricityNetworkFlows_VPP1.csv'))
electricity_generation = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rElectricityTechnologyGeneration_VPP1.csv'))

# remove rows with 'HydrogenFlowIn' and 'HydrogenFlowOut' from hydrogen_balance
hydrogen_balance = hydrogen_balance[~hydrogen_balance['Component'].isin(['HydrogenFlowIn', 'HydrogenFlowOut'])]
# remove rows with 'ElectricityFlowIn' and 'ElectricityFlowOut' from electricity_balance
electricity_balance = electricity_balance[~electricity_balance['Component'].isin(['PowerFlowIn', 'PowerFlowOut'])]

title_fontsize = 20
subtitle_fontsize = 19
text_fontsize = 18
label_fontsize = 16

# Set up dashboard title
st.title("oHySEM Dashboard")

st.header("oHySEM Execution")
st.subheader("Arguments")

arg1 = ""
arg2 = ""
arg3 = ""
arg4 = ""
arg5 = ""

# Assume each row represents one hour, and set a start date
start_date = st.date_input('Select start date:', datetime(2024, 1, 1).date())

# Select Date, Hour, Day, and Week
selected_date = st.date_input('Select a start date:', start_date)
selected_hour = st.slider('Select the hour of the day:', 0, 23, 12)
selected_day = st.slider('Select the day within the week:', 1, 7, 1)
selected_week = st.slider('Select the week within the year:', 1, 52, 1)

st.write(f'Selected Date: {selected_date}, Hour: {selected_hour}, Day: {selected_day}, Week: {selected_week}')

# Store the initial state of widgets in session state if not already initialized
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled_col1_row1 = False
    st.session_state.disabled_col1_row2 = False
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
    st.write("Path: ", input_text_1_row1)
    if input_text_1_row1 == "Default":
        arg1 = ""
    else:
        arg1 = input_text_1_row1

    # Checkbox to control the disabled state of the input widget in column 1, row 2
    checkbox_text_1_row2 = st.checkbox("Adopt default value for the date", key="disable_widget_col1_row2")

    # Update session state for disabled status of col1
    st.session_state.disabled_col1_row2 = checkbox_text_1_row2

    # Set the default value if the checkbox is checked, otherwise allow the user to input their own value
    if st.session_state.disabled_col1_row2:
        input_text_1_row2 = st.text_input(
            "Enter date 👇",
            value="Default",
            label_visibility=st.session_state.visibility,
            disabled=True,
        )
    else:
        input_text_1_row2 = st.text_input(
            "Enter date 👇",
            label_visibility=st.session_state.visibility,
            disabled=False,
            placeholder="Enter the date",
        )
    st.write("Date: ", input_text_1_row2)
    if input_text_1_row2 == "Default":
        arg4 = ""
    else:
        arg4 = input_text_1_row2

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
    st.write("Case: ", input_text_2_row1)
    if input_text_2_row1 == "Default":
        arg2 = ""
    else:
        arg2 = input_text_2_row1

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
            "Enter solver 👇",
            value="Default",
            label_visibility=st.session_state.visibility,
            disabled=True,
        )
    else:
        input_text_3_row1 = st.text_input(
            "Enter solver 👇",
            label_visibility=st.session_state.visibility,
            disabled=False,
            placeholder="Enter the model",
        )
    st.write("Solver: ", input_text_3_row1)
    if input_text_3_row1 == "Default":
        arg3 = ""
    else:
        arg3 = input_text_3_row1

    # Checkbox to control the disabled state of the input widget in column 3, row 2
    checkbox_text_3_row2 = st.checkbox("Save the plot results: True or False", key="disable_widget_col3_row2")

    # Update session state for disabled status of col3
    st.session_state.disabled_col3_row2 = checkbox_text_3_row2

    st.write("Value: ", st.session_state.disabled_col3_row2)
    arg6 = st.session_state.disabled_col3_row2


st.subheader("Problem Solving")
# if st.button('Launch the model'):
#     st.write(f'Plotting {dataset} for {selected_date} at Hour {selected_hour}')
#     filtered_data.plot(x='DateTime')
#     plt.title(f'{dataset} Over Time')
#     st.pyplot(plt)

# st.subheader("Operational Overview")

# Key Performance Indicators (KPIs)
st.header("Key Performance Indicators")
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
st.header("Cost and Profits Overview")
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
        st.header("Total Cost Breakdown")

        # Filter out negative values
        cost_breakdown = total_cost[total_cost['MEUR'] >= 0].groupby('Component')['MEUR'].sum().reset_index()

        # Calculate percentage values
        cost_breakdown['Percentage'] = cost_breakdown['MEUR'] / cost_breakdown['MEUR'].sum() * 100

        # Create a donut chart using Altair
        donut_chart = alt.Chart(cost_breakdown).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="MEUR", type="quantitative"),
            color=alt.Color(field="Component", type="nominal"),
            tooltip=['Component', 'MEUR', 'Percentage']
        ).properties(
            width=400,
            height=300
        )

        # Add percentage labels in the center of each arc with increased font size
        labels = alt.Chart(cost_breakdown).mark_text(radius=90, size=text_fontsize).encode(
            theta=alt.Theta(field="MEUR", type="quantitative"),
            text=alt.Text(field="Percentage", type="quantitative", format=".1f"),  # Format as percentage with 1 decimal
            color=alt.value('black')
        )

        # Combine the donut chart and percentage labels
        donut_with_labels = donut_chart + labels

        # Display the chart in Streamlit
        st.altair_chart(donut_with_labels)


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

        # Hydrogen Network Flows
        st.subheader("Hydrogen Network Flows")
        hydrogen_flows_chart = alt.Chart(hydrogen_flows).mark_bar().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
            y='MW:Q',
            color='InitialNode:N'
        ).properties(width=700, height=400).configure_axis(
            labelFontSize=label_fontsize,
            titleFontSize=title_fontsize
        )
        st.altair_chart(hydrogen_flows_chart, use_container_width=True)

        # Reserve Offers Section
        st.subheader("Reserve Offers Overview")
        reserve_chart = alt.Chart(reserves_offers).mark_bar().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
            y='MW:Q',
            color='Component:N'
        ).properties(width=1400, height=400).configure_axis(
            labelFontSize=label_fontsize,
            titleFontSize=title_fontsize
        )
        st.altair_chart(reserve_chart, use_container_width=True)

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

        # Electricity Network Flows
        st.subheader("Electricity Network Flows")
        electricity_flows_chart = alt.Chart(electricity_flows).mark_bar().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
            y='MW:Q',
            color='InitialNode:N'
        ).properties(width=700, height=400).configure_axis(
            labelFontSize=label_fontsize,
            titleFontSize=title_fontsize
        )
        st.altair_chart(electricity_flows_chart, use_container_width=True)

        # # Total Cost Breakdown with handling of negative values
        # st.header("Total Cost Breakdown")
        # cost_breakdown = total_cost[total_cost['MEUR'] >= 0].groupby('Component')['MEUR'].sum().reset_index()
        #
        # fig, ax = plt.subplots(figsize=(2, 1.5))
        # ax.pie(cost_breakdown['MEUR'], labels=cost_breakdown['Component'], autopct='%1.1f%%', startangle=90)
        # ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        # st.pyplot(fig)

# Footer
st.write("Dashboard created for analyzing H-VPP results.")
