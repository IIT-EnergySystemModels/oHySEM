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

# # Set up dashboard title
# st.title("oHySEM Results Dashboard")
# st.subheader("Hydrogen-Based Virtual Power Plant (H-VPP) Operational Overview")
#
# # Key Performance Indicators (KPIs)
# st.header("Key Performance Indicators")
# total_cost_value = total_cost['MEUR'].sum()
# total_hydrogen = hydrogen_balance['tH2'].sum()
# total_electricity = electricity_generation['MW'].sum()
#
# kpi1, kpi2, kpi3 = st.columns(3)
# kpi1.metric(label="Total Cost (MEUR)", value=f"{total_cost_value:.2f}")
# kpi2.metric(label="Total Hydrogen Storage (tH2)", value=f"{total_hydrogen:.2f}")
# kpi3.metric(label="Total Electricity Generation (MW)", value=f"{total_electricity:.2f}")
#
# # Energy Balance Section
# st.header("Energy Balances")
#
# # Hydrogen Balance Line Chart
# st.subheader("Hydrogen Balance Over Time")
# hydrogen_chart = alt.Chart(hydrogen_balance).mark_bar().encode(
#     x='Date:T',
#     y='tH2:Q',
#     color='Component:N'
# ).properties(width=700, height=400)
# st.altair_chart(hydrogen_chart, use_container_width=True)
#
# # Electricity Balance Line Chart
# st.subheader("Electricity Balance Over Time")
# electricity_chart = alt.Chart(electricity_balance).mark_bar().encode(
#     x='Date:T',
#     y='GWh:Q',
#     color='Component:N'
# ).properties(width=700, height=400)
# st.altair_chart(electricity_chart, use_container_width=True)
#
# # Network Flows Section
# st.header("Network Flows")
#
# # Hydrogen Network Flows
# st.subheader("Hydrogen Network Flows")
# hydrogen_flows_chart = alt.Chart(hydrogen_flows).mark_line().encode(
#     x='Date:T',
#     y='MW:Q',
#     color='InitialNode:N'
# ).properties(width=700, height=400)
# st.altair_chart(hydrogen_flows_chart, use_container_width=True)
#
# # Electricity Network Flows
# st.subheader("Electricity Network Flows")
# electricity_flows_chart = alt.Chart(electricity_flows).mark_line().encode(
#     x='Date:T',
#     y='MW:Q',
#     color='InitialNode:N'
# ).properties(width=700, height=400)
# st.altair_chart(electricity_flows_chart, use_container_width=True)
#
# # Reserve Offers Section
# st.header("Reserve Offers")
# reserve_chart = alt.Chart(reserves_offers).mark_bar().encode(
#     x='Date:T',
#     y='MW:Q',
#     color='Component:N'
# ).properties(width=700, height=400)
# st.altair_chart(reserve_chart, use_container_width=True)
#
# # Total Cost Breakdown
# st.header("Total Cost Breakdown")
# cost_breakdown = total_cost.copy()
# cost_breakdown['MEUR'] = cost_breakdown['MEUR'].apply(lambda x: max(x, 0))  # Replace negative with 0
# cost_breakdown = cost_breakdown.groupby('Component')['MEUR'].sum().reset_index()
#
# fig, ax = plt.subplots()
# ax.pie(cost_breakdown['MEUR'], labels=cost_breakdown['Component'], autopct='%1.1f%%', startangle=90)
# ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
# st.pyplot(fig)


# Set up dashboard title
st.title("oHySEM Results Dashboard")
st.subheader("Operational Overview")

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
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %B %d, %H:%M", tickCount=20)),
            y='MEUR:Q',
            color='Component:N'
        ).properties(width=700, height=400)
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
        labels = alt.Chart(cost_breakdown).mark_text(radius=90, size=18).encode(
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
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %B %d, %H:%M", tickCount=20)),
            y='tH2:Q',
            color='Component:N'
        ).properties(width=700, height=400)
        st.altair_chart(hydrogen_chart, use_container_width=True)

        # Hydrogen Network Flows
        st.subheader("Hydrogen Network Flows")
        hydrogen_flows_chart = alt.Chart(hydrogen_flows).mark_bar().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %B %d, %H:%M", tickCount=20)),
            y='MW:Q',
            color='InitialNode:N'
        ).properties(width=700, height=400)
        st.altair_chart(hydrogen_flows_chart, use_container_width=True)

        # Reserve Offers Section
        st.subheader("Reserve Offers Overview")
        reserve_chart = alt.Chart(reserves_offers).mark_bar().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %B %d, %H:%M", tickCount=20)),
            y='MW:Q',
            color='Component:N'
        ).properties(width=1400, height=400)
        st.altair_chart(reserve_chart, use_container_width=True)

    # Electricity Balance Line Chart
    with col2:
        st.subheader("Electricity Balance Over Time")
        electricity_chart = alt.Chart(electricity_balance).mark_bar().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %B %d, %H:%M", tickCount=20)),
            y='GWh:Q',
            color='Component:N'
        ).properties(width=700, height=400)
        st.altair_chart(electricity_chart, use_container_width=True)

        # Electricity Network Flows
        st.subheader("Electricity Network Flows")
        electricity_flows_chart = alt.Chart(electricity_flows).mark_bar().encode(
            x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %B %d, %H:%M", tickCount=20)),
            y='MW:Q',
            color='InitialNode:N'
        ).properties(width=700, height=400)
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
