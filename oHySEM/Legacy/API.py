from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import os

DirName = os.path.dirname(__file__)
CaseName = 'VPP1'

# Load CSV files
hydrogen_balance = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rHydrogenBalance_VPP1.csv'))
hydrogen_flows = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rHydrogenNetworkFlows_VPP1.csv'))
reserves_offers = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rReservesOffers_VPP1.csv'))
tech_generation = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rTechnologyGeneration_VPP1.csv'))
total_cost = pd.read_csv(os.path.join(DirName, CaseName, 'oH_Result_rTotalCost_VPP1.csv'))

# Streamlit UI elements
st.title('oHySEM Results Explorer')

# Dropdown to select dataset
dataset = st.selectbox('Select a dataset to view:',
                       ['Hydrogen Balance', 'Hydrogen Flows', 'Reserves Offers',
                        'Technology Generation', 'Total Cost'])

if dataset == 'Hydrogen Balance':
    df = hydrogen_balance
elif dataset == 'Hydrogen Flows':
    df = hydrogen_flows
elif dataset == 'Reserves Offers':
    df = reserves_offers
elif dataset == 'Technology Generation':
    df = tech_generation
elif dataset == 'Total Cost':
    df = total_cost

# Assume each row represents one hour, and set a start date
start_date = st.date_input('Select start date:', datetime(2024, 1, 1).date())

# Generate a DateTime index assuming hourly intervals
time_index = pd.date_range(start=start_date, periods=len(df), freq='H')

# Select Date, Hour, Day, and Week
selected_date = st.date_input('Select a start date:', start_date)
selected_hour = st.slider('Select the hour of the day:', 0, 23, 12)
selected_day = st.slider('Select the day within the week:', 1, 7, 1)
selected_week = st.slider('Select the week within the year:', 1, 52, 1)

st.write(f'Selected Date: {selected_date}, Hour: {selected_hour}, Day: {selected_day}, Week: {selected_week}')

df['DateTime'] = time_index
filtered_data = df[df['DateTime'].dt.date == selected_date]
st.subheader('Filtered Data')
st.write(filtered_data)
if st.button('Generate Plot'):
    st.write(f'Plotting {dataset} for {selected_date} at Hour {selected_hour}')
    filtered_data.plot(x='DateTime')
    plt.title(f'{dataset} Over Time')
    st.pyplot(plt)

# # Display the selected dataset
# if dataset == 'Hydrogen Balance':
#     # st.subheader('Hydrogen Balance')
#     # st.write(hydrogen_balance)
#     hydrogen_balance['DateTime'] = time_index
#     filtered_data = hydrogen_balance[hydrogen_balance['DateTime'].dt.date == selected_date]
#     st.subheader('Filtered Hydrogen Balance Data')
#     st.write(filtered_data)
#     if st.button('Generate Plot'):
#         st.write(f'Plotting Hydrogen Balance for {selected_date} at Hour {selected_hour}')
#         filtered_data.plot(x='DateTime')
#         plt.title('Hydrogen Balance Over Time')
#         st.pyplot(plt)
# elif dataset == 'Hydrogen Flows':
#     # st.subheader('Hydrogen Network Flows')
#     # st.write(hydrogen_flows)
#     hydrogen_flows['DateTime'] = time_index
#     filtered_data = hydrogen_flows[hydrogen_flows['DateTime'].dt.date == selected_date]
#     st.subheader('Filtered Hydrogen Flows Data')
#     st.write(filtered_data)
#     if st.button('Generate Plot'):
#         st.write(f'Plotting Hydrogen Flows for {selected_date} at Hour {selected_hour}')
#         filtered_data.plot(x='DateTime')
#         plt.title('Hydrogen Flows Over Time')
#         st.pyplot(plt)
# elif dataset == 'Reserves Offers':
#     # st.subheader('Reserves Offers')
#     # st.write(reserves_offers)
#     reserves_offers['DateTime'] = time_index
#     filtered_data = reserves_offers[reserves_offers['DateTime'].dt.date == selected_date]
#     st.subheader('Filtered Reserves Offers Data')
#     st.write(filtered_data)
#     if st.button('Generate Plot'):
#         st.write(f'Plotting Reserves Offers for {selected_date} at Hour {selected_hour}')
#         filtered_data.plot(x='DateTime')
#         plt.title('Reserves Offers Over Time')
#         st.pyplot(plt)
# elif dataset == 'Technology Generation':
#     # st.subheader('Technology Generation')
#     # st.write(tech_generation)
#     tech_generation['DateTime'] = time_index
#     filtered_data = tech_generation[tech_generation['DateTime'].dt.date == selected_date]
#     st.subheader('Filtered Technology Generation Data')
#     st.write(filtered_data)
#     if st.button('Generate Plot'):
#         st.write(f'Plotting Technology Generation for {selected_date} at Hour {selected_hour}')
#         filtered_data.plot(x='DateTime')
#         plt.title('Technology Generation Over Time')
#         st.pyplot(plt)
# elif dataset == 'Total Cost':
#     # st.subheader('Total Cost')
#     # st.write(total_cost)
#     total_cost['DateTime'] = time_index
#     filtered_data = total_cost[total_cost['DateTime'].dt.date == selected_date]
#     st.subheader('Filtered Total Cost Data')
#     st.write(filtered_data)
#     if st.button('Generate Plot'):
#         st.write(f'Plotting Total Cost for {selected_date} at Hour {selected_hour}')
#         filtered_data.plot(x='DateTime')
#         plt.title('Total Cost Over Time')
#         st.pyplot(plt)

# # Add the time index to the data (for example, to the Hydrogen Balance DataFrame)
# hydrogen_balance['DateTime'] = time_index


#
# # Filter data based on selected date and time
# filtered_data = hydrogen_balance[hydrogen_balance['DateTime'].dt.date == selected_date]
#
# # Display the filtered dataset
# st.subheader('Filtered Hydrogen Balance Data')
# st.write(filtered_data)

# # Plot the filtered dataset
# if st.button('Generate Plot'):
#     st.write(f'Plotting Hydrogen Balance for {selected_date} at Hour {selected_hour}')
#     filtered_data.plot(x='DateTime')
#     plt.title('Hydrogen Balance Over Time')
#     st.pyplot(plt)