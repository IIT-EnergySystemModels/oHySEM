# Developed by Erik Alvarez, Andrés Ramos, Pedro Sánchez
# Jan. 17, 2025

#    Andres Ramos
#    Instituto de Investigacion Tecnologica
#    Escuela Tecnica Superior de Ingenieria - ICAI
#    UNIVERSIDAD PONTIFICIA COMILLAS
#    Alberto Aguilera 23
#    28015 Madrid, Spain
#    Andres.Ramos@comillas.edu
#    https://pascua.iit.comillas.edu/aramos/Ramos_CV.html

import datetime
import streamlit as st
import pandas as pd
import altair as alt
import os
import subprocess
import matplotlib.pyplot as plt

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
st.title("Arguments")

# Arguments
arg_defaults = {
    'dir_name': DirName,
    'case_name': CaseName,
    'solver': 'gurobi',
    'date': datetime.datetime.now().replace(second=0, microsecond=0),
    'raw_results': False,
    'plot_results': False,
    'time_steps': 168,
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

#To show/hide text for help
if 'show_text' not in st.session_state:
    st.session_state.show_text = False
def toggle_text():
    st.session_state.show_text = not st.session_state.show_text


with col1:
    handle_input("Directory path:", DirName, 'dir_name', placeholder="Enter the path")
    button_text = f"Path: {st.session_state.get('dir_name', 'No path selected')}"
    if st.button(button_text, on_click=toggle_text): pass
    if st.session_state.show_text:
        st.markdown('<p style="color:red;">Location Path of oHySEM</p>', unsafe_allow_html=True)


    handle_input("Initial date:", arg_defaults['date'], 'date', placeholder="Enter initial date (YYYY-MM-DD HH:MM:SS)")
    st.write("Date: ", st.session_state['date'])

    handle_input("Number of hours or time steps:", arg_defaults['time_steps'], 'time_steps', input_type=int)
    st.write("Time steps: ", st.session_state['time_steps'])

with col2:
    handle_input("Case Name:", CaseName, 'case_name', placeholder="Enter case")
    st.write("Case: ", st.session_state['case_name'])
    button_text = f"Case: {st.session_state.get('case_name', 'No case selected')}"
    if st.button(button_text, on_click=toggle_text): pass
    if st.session_state.show_text:
        st.markdown('<p style="color:red;">Folder Name where the output will be located in the Directory path</p>', unsafe_allow_html=True)

    st.session_state['raw_results'] = st.checkbox("Save the raw results:", value=st.session_state['raw_results'])
    st.write("Raw results: ", st.session_state['raw_results'])

    # handle_input("H2 Target Demand", arg_defaults['h2_target'], 'h2_target', input_type=float)
    # st.write("H2 Target Demand: ", st.session_state['h2_target'])

with col3:
    handle_input("Solver", "gurobi", 'solver', placeholder="Enter solver (e.g., gurobi, glpk)")
    button_text = f"Solver: {st.session_state.get('solver', 'No solver selected')}"
    if st.button(button_text, on_click=toggle_text): pass
    if st.session_state.show_text:
        st.markdown('<p style="color:red;">Solvers available: gurobi/cplex/highs/glpk</p>', unsafe_allow_html=True)

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
hour_of_year = (st.session_state['date'].timetuple().tm_yday-1) * 24 + st.session_state['date'].timetuple().tm_hour + 1
loadlevel = f't{hour_of_year:04d}'
# Printing initial loadlevel and its button
col1, col2 = st.columns([0.10, 0.95])
with col1:
    st.write("Initial loadlevel: ", loadlevel)
with col2:
    button_text = "❓"
    if st.button(button_text, on_click=toggle_text, key= "initial hour of the optimization"): pass
    if st.session_state.show_text:
       st.markdown('<p style="color:red;">Initial Hour of the Optimization Scope</p>', unsafe_allow_html=True)

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

# reading, modifying and saving the electricity cost data considering the electricity price
st.title("Electricity Cost Data")
st.header("Tariff activation")
button_text = "❓"
if st.button(button_text, on_click=toggle_text, key="Tariff_activation_button"): pass
if st.session_state.show_text:
    st.markdown('<p style="color:green;">Selection of available Tariffs to buy electricity</p>', unsafe_allow_html=True)


# activation of tariffs
col1, col2, col3, col4, col5, col6 = st.columns(6)

activation_tariff = {}

with col1:
    # checkbox
    activation_tariff[1] = st.checkbox("P1", value=True)
    st.write("P1: ", activation_tariff[1])
with col2:
    # checkbox
    activation_tariff[2] = st.checkbox("P2", value=True)
    st.write("P2: ", activation_tariff[2])
with col3:
    # checkbox
    activation_tariff[3] = st.checkbox("P3", value=True)
    st.write("P3: ", activation_tariff[3])
with col4:
    # checkbox
    activation_tariff[4] = st.checkbox("P4", value=True)
    st.write("P4: ", activation_tariff[4])
with col5:
    # checkbox
    activation_tariff[5] = st.checkbox("P5", value=True)
    st.write("P5: ", activation_tariff[5])
with col6:
    # checkbox
    activation_tariff[6] = st.checkbox("P6", value=True)
    st.write("P6: ", activation_tariff[6])


df_ele_cost = load_csv('oH_Data_ElectricityCost_{}.csv'.format(st.session_state['case_name']), 3)
df_ele_price = load_csv('oH_Data_ElectricityPrice_{}.csv'.format(st.session_state['case_name']), 3)
df_tariff = load_csv('oH_Data_Tariff_{}.csv'.format(st.session_state['case_name']), 3)

# modify the electricity cost data
for i in range(hour_of_year, hour_of_year+time_steps+1):
    value = df_tariff.loc[(slice(None), slice(None), f't{i:04d}'), 'Tariff']
    if activation_tariff[value.iloc[0]] == True:  # If you expect one value
        df_ele_cost.loc[(slice(None), slice(None), f't{i:04d}'), 'Node1'] = df_ele_cost.loc[(slice(None), slice(None), f't{i:04d}'), 'Node1']
    else:
        df_ele_cost.loc[(slice(None), slice(None), f't{i:04d}'), 'Node1'] = 1000

# Save the modified dataset
if st.button('Save the modified electricity cost data'):
    df_ele_cost.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], 'oH_Data_ElectricityCost_{}.csv'.format(st.session_state['case_name'])), index=True)
    st.success("Electricity cost data saved successfully!")

# Dataset visualization
st.header("Time Series Data")

datasets = {
    'Electricity Cost [€/MWh]: Cost of buying electricity and maintenance': 'oH_Data_ElectricityCost_{}.csv',
    'Electricity Demand [MW] : Internal electric Demand of the plant': 'oH_Data_ElectricityDemand_{}.csv',
    'Electricity Price [€/MWh]: Day Ahead Electricity Price': 'oH_Data_ElectricityPrice_{}.csv',
    'Hydrogen Cost [€/kgH2] : Cost of producing Hydrogen': 'oH_Data_HydrogenCost_{}.csv',
    'Hydrogen Demand [kgH2] : Additional Hydrogen demand': 'oH_Data_HydrogenDemand_{}.csv',
    'Hydrogen Price [€/kgH2] : Hydrogen Selling Price': 'oH_Data_HydrogenPrice_{}.csv',
    'Variable Max Generation [MW] : Forecast of Renewable Productions': 'oH_Data_VarMaxGeneration_{}.csv'
}

# Dictionary of measuring units of each variable
y_axis_titles = {
    'Electricity Cost [€/MWh]: Cost of buying electricity and maintenance': 'Cost [€/MWh]',
    'Electricity Demand [MW] : Internal electric Demand of the plant': 'Demand [MW]',
    'Electricity Price [€/MWh]: Day Ahead Electricity Price': 'Price [€/MWh]',
    'Hydrogen Cost [€/kgH2] : Cost of producing Hydrogen': 'Cost [€/kgH2]',
    'Hydrogen Demand [kgH2] : Additional Hydrogen demand': 'Demand [kgH2]',
    'Hydrogen Price [€/kgH2] : Hydrogen Selling Price': 'Price [€/kgH2]',
    'Variable Max Generation [MW] : Forecast of Renewable Productions': 'Max Generation [MW]'
}

dataset = st.selectbox('Select a dataset to view:', list(datasets.keys()))

# Obtener el título del eje Y específico según el dataset seleccionado
y_axis_title = y_axis_titles[dataset]

df = load_csv(datasets[dataset].format(st.session_state['case_name']),3)
# filter the dataframe since the second index has to be equal betwen the range of loadlevel and loadlevel + time_steps. the dataframe has 3 levels of index
df = df.loc[(slice(None), slice(None), slice(loadlevel, f't{(hour_of_year+time_steps):04d}')), :]
# stack the dataframe
df = df.stack().reset_index().rename(columns={0: 'Value', 'level_3': 'Component'})

# Add DateTime column
df['DateTime'] = pd.date_range(start=st.session_state['date'], periods=len(df), freq='H')

# Plotting input data
st.subheader(f"{dataset}")
line_chart = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(filled=False, fill="white")).encode(
    x=alt.X('DateTime:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
    y=alt.Y('Value:Q', axis=alt.Axis(title=y_axis_title)),
    color='Component:N'
).properties(width=700, height=400).configure_axis(
                    labelFontSize=label_fontsize,
                    titleFontSize=title_fontsize
                )

st.altair_chart(line_chart, use_container_width=True)

# reading, modifying and saving the input data
st.title("Contracted H2 Demand Conditions")

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
modified_df = df.copy()
# Option of demand type by default
demand_options = ['Hourly', 'Daily', 'Weekly']
default_demand_type = modified_df['DemandType'][0]
default_index = demand_options.index(default_demand_type) if default_demand_type in demand_options else 0

# User inputs
col1, col2, col3 = st.columns(3)

with col1:
    modified_df['DemandType'] = st.selectbox('Select a Demand Schedule:', demand_options, index=default_index)

with col2:
    modified_df['TargetDemand'] = st.number_input("Enter the Scheduled Demand [kgH2]:", value=modified_df['TargetDemand'][0])

with col3:
    modified_df['RampDemand'] = st.number_input("Enter the Maximum H2 Up/Down Delivery Ramp [kgH2/h]:", value=modified_df['RampDemand'][0])

#Explanation of Contracted H2 Demand Conditions
col1, col2 = st.columns([0.80, 0.95])

with col1:
    with st.expander("Contracted H2 Demand Conditions?"):
         st.write("""
         - **Demand Schedule**: Time Duration for scheduling the H2 demand delivery (Hourly/Daily/Weekly)
         - **Schedule Demand**: H2 Demand Scheduled in kilograms 
         - **Maximum H2 Up/Down Delivery Ramp**: Maximum delivery change of H2 kilograms per hour  
       """)

# H2 Market Conditions
st.title("H2 Market Conditions")
# User inputs
col1, col2 = st.columns(2)

with col1:
    modified_df['PriceH2'] = st.number_input("Enter (TO SELL) the Market H2 Price  [€/kgH2]:", value=modified_df['PriceH2'][0])

with col2:
    modified_df['CostH2'] = st.number_input("Enter (TO BUY) the Market H2 Cost  [€/kgH2]:", value=modified_df['CostH2'][0])

#Explanation of Contracted H2 Demand Conditions
col1, col2 = st.columns([0.80, 0.95])

with col1:
    with st.expander("H2 Market Conditions?"):
         st.write("""
         - **Market H2 *Price***: Market Price to *sell* H2 in € per H2 kilogram
         - **Market H2 *Cost***: Market Cost to *buy* H2 in € per H2 kilogram 
       """)


# Save the modified dataset
if st.button('Save the modified data of **H2 Demand & Market Conditions**'):
    modified_df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_par[dataset_par]), index=True)
    st.success("Dataset saved successfully!")
    st.write(modified_df[['DemandType', 'TargetDemand', 'RampDemand', 'PriceH2', 'CostH2']].head())

# reading, modifying and saving the input data
st.title("Electrolyzer Data")

datasets_gen = {
    'Electrolyzer': f'oH_Data_Generation_{st.session_state["case_name"]}.csv',
}

# modify the dataset
df = load_csv(datasets_gen['Electrolyzer'], 1)

modified_df = df.copy()

# list of electrolyzer units, select the unit from df index if the column 'Technology' is equal to 'Electrolyzer'
list_electrolizer_units = df[df['Technology'] == 'Electrolyzer'].index

# select the unit
unit = st.selectbox('Modify the dataset below, select a unit:', list(list_electrolizer_units))

# User inputs
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    modified_df.loc[unit, 'MaximumCharge'] = st.number_input("Enter the Maximum Consumption [MW]:", value=modified_df.loc[unit, 'MaximumCharge'])

with col2:
    modified_df.loc[unit, 'MinimumCharge'] = st.number_input("Enter the Minimum Consumption [MW]:", value=modified_df.loc[unit, 'MinimumCharge'])

with col3:
    modified_df.loc[unit, 'ProductionFunction'] = st.number_input("Enter the Production Function [kWh/kgH2]:", value=modified_df.loc[unit, 'ProductionFunction'])

with col4:
    modified_df.loc[unit, 'StartUpCost'] = st.number_input("Enter the Start Up Cost [€]:", value=modified_df.loc[unit, 'StartUpCost'])

with col5:
    modified_df.loc[unit, 'ShutDownCost'] = st.number_input("Enter the Shut Down Cost [€]:", value=modified_df.loc[unit, 'ShutDownCost'])

with col6:
    modified_df.loc[unit, 'StandByStatus'] = st.selectbox("Enter the Stand By status [Yes or No]:", list(['Yes','No']))

with col7:
    modified_df.loc[unit, 'StandByPower'] = st.number_input("Enter the Stand By Power [MW]:", value=modified_df.loc[unit, 'StandByPower'])

#Explanation of Electrolyzer Data
col1, col2 = st.columns([0.80, 0.95])

with col1:
    with st.expander("Electrolyzer Data?"):
         st.write("""
         - **Maximum Electricity consumption**: Maximum Consumption of the Electrolyzer in MW
         - **Minimum Electricity Consumption**: Minimum Consumption of the Electrolyzer in MW
         - **Production Function**: kWh consumed to produce 1 kg of Hydrogen
         - **Start Up Cost:** Cost of Starting Up the electrolyzer to its minimum consumption value in €
         - **Shut Down Cost:** Cost of Shutting Down the electrolyzer from its minimum consumption value to zero in €
         - **Stand By Status:** To let the electrolyzer to be at Stand By state (no H2 production)
         - **Stand By Power:** The electrolyzer consumption in MW
         """)

# save the modified dataset
if st.button('Save the modified data of the electrolyzer'):
    modified_df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_gen['Electrolyzer']), index=True)
    st.success("Dataset saved successfully!")
    st.write(modified_df[['MaximumCharge', 'MinimumCharge', 'ProductionFunction', 'StartUpCost', 'ShutDownCost','StandByStatus','StandByPower']].head())

# List of Wind Farm
st.title("Wind Data")

datasets_gen = {
    'Wind': f'oH_Data_Generation_{st.session_state["case_name"]}.csv',
}

# modify the dataset
df = load_csv(datasets_gen['Wind'], 1)

modified_df = df.copy()
aux_df      = df.copy()

# list of wind units, select the unit from df index if the column 'Technology' is equal to 'Wind'
list_wind_units = df[df['Technology'] == 'Wind'].index

# select the unit
unit = st.selectbox('Modify the dataset below, select a unit:', list(list_wind_units))

# User inputs
col1, col2= st.columns(2)

with col1:
    modified_df.loc[unit, 'MaximumPower'] = st.number_input("Enter the maximum installed Wind power [MW]:", value=modified_df.loc[unit, 'MaximumPower'])

with col2:
    modified_df.loc[unit, 'MustRun'] = st.selectbox("Enter the must run status [Yes or No]:", list(['Yes','No']))


# save the modified dataset
if st.button('Save the modified Wind Data'):
    modified_df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_gen['Wind']), index=True)
    st.success("Dataset saved successfully!")
    st.write(modified_df[['MaximumPower', 'MustRun']].head())

# modify the VarMaxGeneration based on the MaximumPower value
    datasets_gen = {
        'WindMaxGeneration': f'oH_Data_VarMaxGeneration_{st.session_state["case_name"]}.csv',
    }

    df = load_csv('oH_Data_VarMaxGeneration_{}.csv'.format(st.session_state['case_name']), 3)
    df[unit] = df[unit] * (modified_df.loc[unit, 'MaximumPower']/aux_df.loc[unit, 'MaximumPower'])
    st.write(df)
    df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_gen['WindMaxGeneration']), index=True)

####################

# List of Solar_PV Data
st.title("Solar PV Data")

datasets_gen = {
    'Solar_PV': f'oH_Data_Generation_{st.session_state["case_name"]}.csv',
}

# modify the dataset
df = load_csv(datasets_gen['Solar_PV'], 1)

modified_df = df.copy()
aux_df      = df.copy()

# list of Solar_PV units, select the unit from df index if the column 'Technology' is equal to 'Wind'
list_Solar_PV_units = df[df['Technology'] == 'Solar_PV'].index

# select the unit
unit = st.selectbox('Modify the dataset below, select a unit:', list(list_Solar_PV_units))

# User inputs
col1, col2= st.columns(2)

with col1:
    modified_df.loc[unit, 'MaximumPower'] = st.number_input("Enter the maximum installed Solar PV power [MW]:", value=modified_df.loc[unit, 'MaximumPower'])

with col2:
    modified_df.loc[unit, 'MustRun'] = st.selectbox("Enter the must run status [Yes or No]:", list(['Yes','No']), key=f"must_run_{unit}")


# save the modified dataset
if st.button('Save the modified Solar PV Data'):
    modified_df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_gen['Solar_PV']), index=True)
    st.success("Dataset saved successfully!")
    st.write(modified_df[['MaximumPower', 'MustRun']].head())
   # modify the VarMaxGeneration based on the MaximumPower value
    datasets_gen = {
        'SolarPVMaxGeneration': f'oH_Data_VarMaxGeneration_{st.session_state["case_name"]}.csv',
    }

    df = load_csv('oH_Data_VarMaxGeneration_{}.csv'.format(st.session_state['case_name']), 3)
    df[unit] = df[unit] * (modified_df.loc[unit, 'MaximumPower']/aux_df.loc[unit, 'MaximumPower'])
    st.write(df)
    df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_gen['SolarPVMaxGeneration']), index=True)

#######################

# List of Battery Units
st.title("Battery Data (BESS)")

datasets_gen = {
    'BESS': f'oH_Data_Generation_{st.session_state["case_name"]}.csv',
}

# modify the dataset
df = load_csv(datasets_gen['BESS'], 1)

modified_df = df.copy()
aux_df      = df.copy()

# list of Battery units, select the unit from df index if the column 'Technology' is equal to 'BESS'
list_battery_units = df[df['Technology'] == 'BESS'].index

# select the unit
unit = st.selectbox('Modify the dataset below, select a unit:', list(list_battery_units))

# User inputs
col1, col2, col3, col4 = st.columns(4)

with col1:
    modified_df.loc[unit, 'MaximumPower'] = st.number_input("Enter the Maximum Power Output  [MW]:", value=modified_df.loc[unit, 'MaximumPower'])

with col2:
    modified_df.loc[unit, 'MinimumStorage'] = st.number_input("Enter the Minimum Storage  [GWh]:", value=modified_df.loc[unit, 'MinimumStorage'], format="%.3f")

with col3:
    modified_df.loc[unit, 'MaximumStorage'] = st.number_input("Enter the Maximum Storage  [GWh]:", value=modified_df.loc[unit, 'MaximumStorage'], format="%.3f")

with col4:
    modified_df.loc[unit, 'InitialStorage'] = st.number_input("Enter the Initial Storage  [GWh]:", value=modified_df.loc[unit, 'InitialStorage'], format="%.3f")

# save the modified battery dataset
if st.button('Save the modified Battery Data'):
    modified_df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_gen['BESS']), index=True)
    st.success("Dataset saved successfully!")
    st.write(modified_df[['MaximumPower', 'MinimumStorage','MaximumStorage', 'InitialStorage']].head())

# List of Battery Units
st.title("Hydrogen Tank Data (H2ESS)")

datasets_gen = {
    'H2ESS': f'oH_Data_Generation_{st.session_state["case_name"]}.csv',
}

# modify the dataset
df = load_csv(datasets_gen['H2ESS'], 1)

modified_df = df.copy()
aux_df      = df.copy()

# list of Battery units, select the unit from df index if the column 'Technology' is equal to 'H2ESS'
list_h2ess_units = df[df['Technology'] == 'H2ESS'].index

# select the unit
unit = st.selectbox('Modify the dataset below, select a unit:', list(list_h2ess_units))

# User inputs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    modified_df.loc[unit, 'MaximumPower'] = st.number_input("Enter the Maximum H2 OutFlow  [kg/h]:", value=modified_df.loc[unit, 'MaximumPower'])

with col2:
    modified_df.loc[unit, 'MaximumCharge'] = st.number_input("Enter the Maximum H2 InFlow  [kg/h]:", value=modified_df.loc[unit, 'MaximumCharge'])

with col3:
    modified_df.loc[unit, 'MinimumStorage'] = st.number_input("Enter the Minimum Storage  [tH2]:", value=modified_df.loc[unit, 'MinimumStorage'], format="%.3f")

with col4:
    modified_df.loc[unit, 'MaximumStorage'] = st.number_input("Enter the Maximum Storage  [tH2]:", value=modified_df.loc[unit, 'MaximumStorage'], format="%.3f")

with col5:
    modified_df.loc[unit, 'InitialStorage'] = st.number_input("Enter the Initial Storage  [tH2]:", value=modified_df.loc[unit, 'InitialStorage'], format="%.3f")

#Explanation of H2ESS Data
col1, col2 = st.columns([0.50, 0.95])

with col1:
    with st.expander("H2ESS Data?"):
         st.write("""
         - **Maximum Power OutFlow**: Maximum H2 flow FROM the H2ESS in kilograms per hour
         - **Maximum Power InFlow**: Maximum H2 flow INTO the H2ESS in kilograms per hour
         - **Initial/Minimum/Maximum Storage**: H2 stored in the H2ESS in tons of H2
         """)


# save the modified h2ess dataset
if st.button('Save the modified H2ESS Data'):
    modified_df.to_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], datasets_gen['H2ESS']), index=True)
    st.success("Dataset saved successfully!")
    st.write(modified_df[['MaximumPower', 'MaximumCharge', 'MinimumStorage','MaximumStorage', 'InitialStorage']].head())



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
        st.title("OUTPUT ANALYSIS")

        # Load result CSVs
        # @st.cache_data
        def load_result_csv(file_name):
            return pd.read_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'], file_name))

        hydrogen_balance      = load_result_csv(f'oH_Result_rHydrogenBalance_{st.session_state["case_name"]}.csv')
        hydrogen_inventory    = load_result_csv(f'oH_Result_rHydInventory_{st.session_state["case_name"]}.csv')
        electricity_balance   = load_result_csv(f'oH_Result_rElectricityBalance_{st.session_state["case_name"]}.csv')
        electricity_inventory = load_result_csv(f'oH_Result_rEleInventory_{st.session_state["case_name"]}.csv')
        total_cost            = load_result_csv(f'oH_Result_rTotalCost_{st.session_state["case_name"]}.csv')
        commitment_hz         = load_result_csv(f'oH_Result_rCommitment_hz_{st.session_state["case_name"]}.csv')

        # Filter unnecessary rows
        hydrogen_balance = hydrogen_balance[~hydrogen_balance['Component'].isin(['HydrogenFlowIn', 'HydrogenFlowOut', 'Wind', 'BESS'])]
        electricity_balance = electricity_balance[~electricity_balance['Component'].isin(['PowerFlowIn', 'PowerFlowOut'])]

        # Key Performance Indicators (KPIs)
        st.subheader("Key Performance Indicators")

        total_cost_value = total_cost['kEUR'].sum()
        total_hydrogen = hydrogen_balance[hydrogen_balance['Component'] == 'Electrolyzer']['kgH2'].sum()
        total_hydrogen_storage = hydrogen_balance[(hydrogen_balance['Component'] == 'H2ESS') & (hydrogen_balance['kgH2'] > 0)]['kgH2'].sum()
        total_electricity_sell = electricity_balance[electricity_balance['Component'] == 'ElectricitySell']['MWh'].sum()
        total_electricity_buy = electricity_balance[electricity_balance['Component'] == 'ElectricityBuy']['MWh'].sum()


        def style_kpi(label, value, background_color):
            return f"""
            <div style="
                border: 1px solid #d3d3d3; 
                border-radius: 10px; 
                padding: 10px; 
                margin: 5px; 
                background-color: {background_color}; 
                text-align: center;">
                <h5 style="color: #555555; margin: 0;">{label}</h5>
                <h3 style="color: #333333; margin: 5px 0;">{value}</h3>
            </div>
            """

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

        # Mostrar KPIs con colores suaves
        with kpi1:
            st.markdown(style_kpi("Total Cost (kEUR)", f"{total_cost_value:.2f}", "#f0f8ff"),
                        unsafe_allow_html=True)  # AliceBlue
        with kpi2:
            st.markdown(style_kpi("Total Hydrogen Production (kgH2)", f"{total_hydrogen:.2f}", "#f5fffa"),
                        unsafe_allow_html=True)  # MintCream
        with kpi3:
            st.markdown(style_kpi("Hydrogen through Tank (kgH2)", f"{total_hydrogen_storage:.2f}", "#fafad2"),
                        unsafe_allow_html=True)  # LightGoldenRodYellow
        with kpi4:
            st.markdown(style_kpi("Total Electricity Sold (MWh)", f"{total_electricity_sell:.2f}", "#e6e6fa"),
                        unsafe_allow_html=True)  # Lavender
        with kpi5:
            st.markdown(style_kpi("Total Electricity Purchased (MWh)", f"{total_electricity_buy:.2f}", "#fff5ee"),
                        unsafe_allow_html=True)  # SeaShell

        # Creating a layout for energy balances and network flows
        st.subheader("TIME ANALYSIS")
        with st.container():
            # Two columns: One timeline for the cost and a pie chart for total cost and profits
            col1, col2 = st.columns(2)

            # Total Cost Line Chart
            with col1:
                st.subheader("Operating Costs")

                selection_cost = alt.selection_point(fields=['Component'], bind='legend')
                cost_chart = alt.Chart(total_cost).mark_bar().encode(
                    x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                    y='kEUR:Q',
                    color='Component:N',
                    opacity=alt.condition(selection_cost, alt.value(0.8), alt.value(0.2))
                ).properties(width=700, height=400, background='#000000').configure_axis(
                    labelFontSize=label_fontsize,
                    titleFontSize=title_fontsize
                ).add_params(selection_cost).interactive()
                st.altair_chart(cost_chart, use_container_width=True)

            with st.expander("Cost Components?"):
                st.markdown("""
                - **vTotalCCost**: Consumption Operation Cost = Electricity Consumption Cost of Batteries and Electrolyzer (mainly O&M)
                - **vTotalECost**: Emission Cost = **Electricity** Generation Emission Cost
                - **vTotalGCost**: Operation Cost = **Electricity** (Generation + Commitment + StartUp + ShutDown) Cost + **Hydrogen** (Commitment + Ramp + StartUp + ShutDown) Cost
                - **vTotalMCost**: Market Cost = **Electricity** Purchasing Cost **- Electricity** Selling Income **+ Hydrogen** Purchasing Cost **- Hydrogen** Selling Cost **+ Non supplied** Penalties           
                - **vTotalRCost**: Reserve Revenue = **Secondary Reserve Power** (Up + Down) Revenue + **Secondary Reserve Activation** (Up + Down) Revenue
                """)


            # Donut chart
            with col2:
                # Total Cost Breakdown with handling of negative values
                st.header("Total Costs and Profits")

                def create_donut_charts(data):

                    # Filter positive values (costs)
                    costs = data[data['kEUR'] >= 0].groupby('Component')['kEUR'].sum().reset_index()
                    costs['Percentage'] = costs['kEUR'] / costs['kEUR'].sum() * 100

                    # Filter negative values (profits)
                    profits = data[data['kEUR'] < 0].groupby('Component')['kEUR'].sum().reset_index()
                    profits['Percentage'] = profits['kEUR'] / profits['kEUR'].sum() * 100
                    profits['kEUR'] = profits['kEUR'].abs()  # Convert profits to positive values for display

                    # Helper function to create individual donut chart with labels
                    def create_donut_chart(df, title):
                        # Create the donut chart
                        donut_chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
                            theta=alt.Theta(field="kEUR", type="quantitative"),
                            color=alt.Color(field="Component", type="nominal"),
                            tooltip=['Component', 'kEUR', 'Percentage']
                        ).properties(
                            width=400,
                            height=300,
                            title=title
                        )

                        # Add labels to the donut chart showing both percentage and kEUR
                        labels = alt.Chart(df).mark_text(radius=200, size=text_fontsize).encode(
                            theta=alt.Theta(field="kEUR", type="quantitative"),
                            text=alt.Text(field="label", type="nominal"),
                            color=alt.value('black')  # Ensures the label color is consistent
                        )

                        return donut_chart + labels

                    # Add a label column that combines kEUR and Percentage
                    costs['label'] = costs.apply(lambda row: f'{row["kEUR"]:.1f} kEUR ({row["Percentage"]:.1f}%)',
                                                 axis=1)
                    profits['label'] = profits.apply(lambda row: f'{row["kEUR"]:.1f} kEUR ({row["Percentage"]:.1f}%)',
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
        st.subheader("*ENERGY BALANCE*")

        # Two figures in a row
        col1, col2 = st.columns(2)

        # Electricity Balance Line Chart
        with col1:
            st.subheader("Electricity")

            selection_ele_balance = alt.selection_point(fields=['Component'], bind='legend')
            electricity_chart = alt.Chart(electricity_balance).mark_bar().encode(
                    x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30,
                                                    labelLimit=1000)),
                    y='MWh:Q',
                    color=alt.Color('Component:N'),
                    opacity=alt.condition(selection_ele_balance, alt.value(0.8), alt.value(0.2))
                ).properties(width=700, height=400, background='#000000').configure_axis(
                    labelFontSize=label_fontsize,
                    titleFontSize=title_fontsize
                ).configure_view(strokeOpacity=0).add_params(selection_ele_balance).interactive()

            st.altair_chart(electricity_chart, use_container_width=True)

            with st.expander("Electricity & Hydrogen Components?"):
                    st.markdown("""
                    - **BESS**: Battery
                    - **ENS / HNS**:  Electricity/ Hydrogen Non-Supplied
                    - **ElectricityBuy**: Electricity purchased from the market
                    - **ElectricityDemand**: Auxiliary demand by the plant
                    - **ElectricitySell**: Electricity sold to the market
                    - **Electrolyzer**: Electricity consumed by the electrolyzer / Hydrogen produced by the electrolyzer
                    - **H2ESS**: Hydrogen stored in the Tank
                    - **Solar_PV**: Electricity produced by the PV plant
                    - **Wind**: Electricity produced by the Wind plant
                    - **HydrogenBuy**: Hydrogen bought from the market
                    - **HydrogenDemand**: Hydrogen demanded by the offtaker 
                    - **HydrogenSell**: Hydrogen sold to the market
                    """)

        # Hydrogen Balance Line Chart
        with col2:
            st.subheader("Hydrogen")

            selection_hyd_balance = alt.selection_point(fields=['Component'], bind='legend')

            hydrogen_chart = alt.Chart(hydrogen_balance).mark_bar().encode(
                x=alt.X('Date:T',  axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                y=alt.Y('kgH2:Q', title='kg H2'),
                color=alt.Color('Component:N', scale=alt.Scale(domain=['Electrolyzer', 'H2ESS', 'HNS', 'HydrogenBuy',
                                                                       'HydrogenDemand', 'HydrogenSell', 'Solar_PV'],
                                                               range=['#FF5733', '#33FF57', '#FF33A1', '#FFC300',
                                                                      '#33C1FF', '#FF914D', '#DAF7A6'])),
                opacity=alt.condition(selection_hyd_balance, alt.value(0.8), alt.value(0.2)),
                tooltip=['Date:T', 'kgH2:Q', 'Component:N']
            ).properties(width=700, height=400, background='#000000').configure_axis(
                labelFontSize=label_fontsize, titleFontSize=title_fontsize, labelColor='#FFFFFF'
            ).configure_legend(
                labelColor='#FFFFFF', titleColor='#FFFFFF'
            ).add_params(selection_hyd_balance).interactive()

            st.altair_chart(hydrogen_chart, use_container_width=True)


        # ESS and HSS Storage Levels
        st.subheader("*ENERGY STORAGE LEVELS*")

        # Electricity Storage Level Chart
        st.subheader("ELECTRICITY Storage Level (kWh)")

        selection = alt.selection_point(fields=['Component', 'ESS'], bind='legend')

        combined_chart = (alt.layer(
              alt.Chart(electricity_balance).mark_bar().encode(
                x=alt.X('Date:T', axis=alt.Axis( title='',
                            labelAngle=-90,format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                y=alt.Y('MWh:Q', title='MWh'),
                color=alt.Color('Component:N',
                                scale=alt.Scale(domain=['BESS', 'ENS', 'ElectricityBuy', 'ElectricityDemand',
                                                        'ElectricitySell', 'Electrolyzer', 'H2ESS', 'Solar_PV', 'Wind'],
                                                range=['#1F77B4', '#E377C2', '#FF0000', '#E377C2', '#2CA02C',
                                                       '#17BECF', '#1F77B4', '#FFBB78', '#9467BD'])),
                opacity=alt.condition(selection, alt.value(0.8), alt.value(0.2)),
                tooltip=['Date:T', 'MWh:Q', 'Component:N']
              ),
              alt.Chart(electricity_inventory).mark_line(strokeWidth=4, color='#FFFF00').encode(
                x=alt.X('Date:T', axis=alt.Axis(format="%A, %b %d, %H:%M", title='')),
                y=alt.Y('MWh:Q', title='MWh'),
                tooltip=['Date:T', 'MWh:Q', 'ESS:N']
              )
          ).add_params(selection).interactive().
             properties(width=700, height=400, background='#000000'
             ).configure_axis(
            labelFontSize=label_fontsize, titleFontSize=title_fontsize, labelColor='#FFFFFF', titleColor='#FFFFFF'
        ).configure_legend(
            labelColor='#FFFFFF', titleColor='#FFFFFF'
        ).configure_view(
            strokeOpacity=0
        ))

        st.altair_chart(combined_chart, use_container_width=True)


        # Hydrogen Storage Level Chart

        st.subheader("HYDROGEN Storage Level (kgH2)")


        selection_hydrogen = alt.selection_point(fields=['Component', 'HSS'], bind='legend')

        bar_chart = alt.Chart(hydrogen_balance).mark_bar().encode(
            x=alt.X('Date:T',
                    axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
            y=alt.Y('kgH2:Q', title='kg H2 (Bars)', axis=alt.Axis(titleColor='#FFFFFF')),
            color=alt.Color('Component:N', scale=alt.Scale(domain=['Electrolyzer', 'H2ESS', 'HNS', 'HydrogenBuy',
                                                                   'HydrogenDemand', 'HydrogenSell', 'Solar_PV'],
                                                           range=['#FF5733', '#33FF57', '#FF33A1', '#FFC300',
                                                                  '#33C1FF', '#FF914D', '#DAF7A6']),
                            legend=alt.Legend(title="Hydrogen Balance Components")),
            opacity=alt.condition(selection_hydrogen, alt.value(0.8), alt.value(0.2)),
            tooltip=['Date:T', 'kgH2:Q', 'Component:N']
        )

        line_chart = alt.Chart(hydrogen_inventory).mark_line(strokeWidth=4, color='#FFFF00').encode(
            x='Date:T',
            y=alt.Y('kgH2:Q', title='kg H2 (Line)', axis=alt.Axis(titleColor='#00BFFF', orient='right')),
            tooltip=['Date:T', 'kgH2:Q', 'HSS:N'],
            opacity=alt.condition(selection_hydrogen, alt.value(0.8), alt.value(0.2))
        )

        combined_chart = alt.layer(bar_chart, line_chart).add_params(selection_hydrogen).resolve_scale(
            y='independent'
        ).properties(
            width=700, height=400, background='#000000'
        ).configure_axis(
            labelFontSize=label_fontsize, titleFontSize=title_fontsize, labelColor='#FFFFFF'
        ).configure_legend(
            labelColor='#FFFFFF', titleColor='#FFFFFF'
        ).configure_view(
            strokeOpacity=0
        ).interactive()

        st.altair_chart(combined_chart, use_container_width=True)

    with st.expander("Energy Storage Components?"):
                st.markdown("""
                - **Yellow line** at the **Electricity** Storage Level: State of Charge (SoC) of the BESS
                - **Yellow line** at the **Hydrogen** Storage Level: Hydrogen stored in the HESS
                """)

    st.title("Electrolyzer Commitment Graph")
    commitment_hz = pd.read_csv(os.path.join(st.session_state['dir_name'], st.session_state['case_name'],
                                         f'oH_Result_rCommitment_hz_{st.session_state["case_name"]}.csv'))
    commitment_hz_filtered = commitment_hz[commitment_hz['Value'] != 0]


    # Crear el gráfico con Altair
    chart = alt.Chart(commitment_hz_filtered).mark_circle(size=100).encode(
                 x=alt.X('Date:T', axis=alt.Axis(title='', labelAngle=-90, format="%A, %b %d, %H:%M", tickCount=30, labelLimit=1000)),
                 y=alt.Y('Value:Q', title='Status'),
                          color=alt.Color('Status:N', title='Estado',scale=alt.Scale(domain=['StartUp', 'ShutDown', 'Commitment', 'Standby'],
                                    range=['green', 'red', 'blue', 'orange'])
                                    ),
                 tooltip=['Date:T', 'Value:Q', 'Status:N']  # Información en el hover
                 ).properties(
                 title="Commitment AEL_01",
                 width=800,
                 height=400
                 ).interactive()

                  # Mostrar el gráfico en Streamlit
    st.altair_chart(chart, use_container_width=True)




st.write("Dashboard created for analyzing oHySEM results.")
