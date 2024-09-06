# Developed by Erik Alvarez, Andrés Ramos

#    Andres Ramos
#    Instituto de Investigacion Tecnologica
#    Escuela Tecnica Superior de Ingenieria - ICAI
#    UNIVERSIDAD PONTIFICIA COMILLAS
#    Alberto Aguilera 23
#    28015 Madrid, Spain
#    Andres.Ramos@comillas.edu
#    https://pascua.iit.comillas.edu/aramos/Ramos_CV.htm

#%% Libraries
import argparse
import csv
import datetime
import os
import math
import time          # count clock time
import psutil        # access the number of CPUs
# import openpyxl
import altair            as alt
import pandas            as pd
import plotly.io         as pio
import plotly.graph_objs as go
# import pyomo.environ     as pyo
from   pyomo.environ     import Set, Param, Var, Binary, UnitInterval, NonNegativeIntegers, PositiveIntegers, NonNegativeReals, Reals, Any, Constraint, ConcreteModel, Objective, minimize, Suffix, DataPortal
from   pyomo.opt         import SolverFactory
from   pyomo.dataportal  import DataPortal
from   collections       import defaultdict
from   colour            import Color

for i in range(0, 117):
    print('-', end="")

print('\nProgram for Optimizing the Operation Scheduling of Hydrogen base virtual power plant in Short-Term Electricity Markets (HySTEM) - Version 1.0.0 - November 21, 2023')
print('#### Non-commercial use only ####')

parser = argparse.ArgumentParser(description='Introducing main arguments...')
parser.add_argument('--dir',    type=str, default=None)
parser.add_argument('--case',   type=str, default=None)
parser.add_argument('--solver', type=str, default=None)

default_DirName    = os.path.dirname(__file__)
default_CaseName   = 'sSEP'                              # To select the case
default_SolverName = 'gurobi'

#%% Model declaration
oHySTEM = ConcreteModel('Program for Optimizing the Operation Scheduling of Hydrogen base virtual power plant in Short-Term Electricity Markets (HySTEM) - Version 1.0.0 - November 21, 2023')

def main(cmodel):
    initial_time = time.time()
    args = parser.parse_args()
    # args.dir = default_DirName
    if args.dir is None:
        args.dir = input('Input Dir   Name (Default {}): '.format(default_DirName))
        if args.dir == '':
            args.dir = default_DirName
    if args.case is None:
        args.case = input('Input Case   Name (Default {}): '.format(default_CaseName))
        if args.case == '':
            args.case = default_CaseName
    args.solver = default_SolverName
    print(args.case)
    print(args.dir)
    print(args.solver)


    # reading and processing the data
    #
    print('- Initializing the model\n')
    model = data_processing(args.dir, args.case, cmodel)
    print('- Total time for reading and processing the data:                      {}  seconds\n'.format(round(time.time() - initial_time)))
    start_time = time.time()
    # defining the variables
    model = create_variables(model, model)
    print('- Total time for defining the variables:                               {}  seconds\n'.format(round(time.time() - start_time  )))
    start_time = time.time()
    # defining the objective function
    model = create_objective_function(model, model)
    print('- Total time for defining the objective function:                      {}  seconds\n'.format(round(time.time() - start_time  )))
    start_time = time.time()
    # defining components of the day-ahead objective function
    model = create_objective_function_market(model, model)
    print('- Total time for defining the objective function:                      {}  seconds\n'.format(round(time.time() - start_time  )))
    start_time = time.time()
    # # defining components of the intraday objective function
    # model = create_objective_function_id_market(model, model)
    # print('- Total time for defining the IDobjective function:                    {} seconds\n'.format(round(time.time() - start_time  )))
    # start_time = time.time()
    # # defining components of the real-time objective function
    # model = create_objective_function_rt_market(model, model)
    # print('- Total time for defining the RT objective function:                   {} seconds\n'.format(round(time.time() - start_time  )))
    # start_time = time.time()
    # defining the constraints
    model = create_constraints(model, model)
    # model.vHydStandBy['period1', 'sc01', 't5013', 'AEL_01'].fix(1.0)
    print('fixing standby')
    print('- Total time for defining the DA constraints:                          {}  seconds\n'.format(round(time.time() - start_time  )))
    start_time = time.time()
    # solving the model
    pWrittingLPFile = 1
    model = solving_model( args.dir, args.case, args.solver, model, pWrittingLPFile)
    print('- Total time for solving the model:                                    {}  seconds\n'.format(round(time.time() - start_time  )))
    start_time = time.time()
    model = OutputVariablesToCSV(args.dir, args.case, args.solver, model, model)
    print('- Total time for writing the results:                                  {}  seconds\n'.format(round(time.time() - start_time  )))
    start_time = time.time()
    model = saving_results(args.dir, args.case, args.solver, model, model)
    print('- Total time for saving the results:                                   {}  seconds\n'.format(round(time.time() - start_time  )))
    start_time = time.time()
    # network mapping
    # network_map(args.dir, args.case, model, model)
    # print('- Total time for network mapping:                                      {}  seconds\n'.format(round(time.time() - start_time  )))
    elapsed_time = round(time.time() - initial_time)
    print('Elapsed time: {} seconds'.format(elapsed_time))
    path_to_write_time = os.path.join(args.dir,args.case,"oH_ComputationTime"+args.case+".txt")
    with open(path_to_write_time, 'w') as f:
         f.write(str(elapsed_time))


def data_processing(DirName, CaseName, model):
    # %% Read the input data
    print('-- Reading the input data')
    # Defining the path
    path_to_read = os.path.join(DirName,CaseName)
    start_time = time.time()

    set_definitions = {
        'pp': ('Period',     'p' ), 'scc': ('Scenario', 'sc'), 'nn': ('LoadLevel',  'n' ),
        'st': ('Storage',    'st'), 'gt':  ('Technology', 'gt'),
        'nd': ('Node',       'nd'), 'ni':  ('Node',     'nd'), 'nf': ('Node',       'nd'),
        'zn': ('Zone',       'zn'), 'cc':  ('Circuit',  'cc'), 'c2': ('Circuit',    'cc'),
        'ndzn': ('NodeToZone', 'ndzn'),
        'gg': ('ElectricityGeneration', 'g' ), 'hh': ('HydrogenGeneration', 'h' )}

    dictSets = DataPortal()

    # Reading dictionaries from CSV and adding elements to the dictSets
    for set_name, (file_set_name, set_key) in set_definitions.items():
        filename = f'oH_Dict_{file_set_name}_{CaseName}.csv'
        dictSets.load(filename=os.path.join(path_to_read, filename), set=set_key, format='set')

    # Defining sets in the model
    for set_name, (file_set_name, set_key) in set_definitions.items():
        is_ordered = set_name not in {'gg', 'hh', 'st', 'gt', 'nd', 'ni', 'nf', 'cc', 'c2', 'ndzn'}
        setattr(model, set_name, Set(initialize=dictSets[set_key], ordered=is_ordered, doc=f'{file_set_name}'))

    #%% Reading the input data
    data_frames = {}

    files_list = [file.split("_")[2] for file in os.listdir(os.path.join(path_to_read)) if 'oH_Data' in file]

    for file_set_name in files_list:
        file_name = f'oH_Data_{file_set_name}_{CaseName}.csv'
        data_frames[f'df{file_set_name}'] = pd.read_csv(os.path.join(path_to_read, file_name))
        unnamed_columns = [col for col in data_frames[f'df{file_set_name}'].columns if 'Unnamed' in col]
        data_frames[f'df{file_set_name}'].set_index(unnamed_columns, inplace=True)
        data_frames[f'df{file_set_name}'].index.names = [None] * len(unnamed_columns)

    # substitute NaN by 0
    for df in data_frames.values():
        df.fillna(0.0, inplace=True)

    # Define prefixes and suffixes
    model.reserves_prefixes = ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']
    model.SR_reserves = ['Up_SR', 'Down_SR']
    model.TR_reserves = ['Up_TR', 'Down_TR']
    model.gen_frames_suffixes = ['VarMinGeneration', 'VarMaxGeneration',
                           'VarMinConsumption', 'VarMaxConsumption',
                           'VarMinStorage', 'VarMaxStorage',
                           'VarMinInflows', 'VarMaxInflows',
                           'VarMinOutflows', 'VarMaxOutflows',
                           'VarMinEnergy', 'VarMaxEnergy',
                           'VarMinFuelCost', 'VarMaxFuelCost',
                           'VarMinEmissionCost', 'VarMaxEmissionCost',
                           'VarPositionConsumption', 'VarPositionGeneration']
    model.nodal_frames_suffixes = ['ElectricityDemand', 'HydrogenDemand',
                             'ElectricityCost', 'ElectricityPrice', 'HydrogenPrice', 'HydrogenCost']

    # Apply the condition to each specified column
    for column in model.gen_frames_suffixes:
        data_frames[f'df{column}'] = data_frames[f'df{column}'].where(data_frames[f'df{column}'] > 0.0)

    reading_time = round(time.time() - start_time)
    print('--- Reading the CSV files:                                             {} seconds'.format(reading_time))
    start_time = time.time()

    # Constants
    factor1 = 1e-3  # Conversion factor

    # Option Indicators
    option_ind = data_frames['dfOption'].columns.to_list()

    # Extract and cast option indicators
    parameters_dict = {f'pOpt{indicator}': data_frames['dfOption'][indicator].iloc[0].astype('int') for indicator in option_ind}

    # Parameter Indicators
    parameter_ind = data_frames['dfParameter'].columns.to_list()

    # Extract, process parameter variables and add to parameters_dict
    for indicator in parameter_ind:
        if ('Cost' in indicator or 'Target' in indicator or 'Ramp' in indicator) and 'CO2' not in indicator:
            parameters_dict[f'pPar{indicator}'] = data_frames['dfParameter'][indicator].iloc[0] * factor1
        else:
            parameters_dict[f'pPar{indicator}'] = data_frames['dfParameter'][indicator].iloc[0]

    parameters_dict['pDuration'       ] = data_frames['dfDuration']['Duration'] * parameters_dict['pParTimeStep']
    #parameters_dict['pLevelToIDmarket'] = data_frames['dfDuration']['IDMarket'].astype('int')
    parameters_dict['pPeriodWeight'   ] = data_frames['dfPeriod']['Weight'].astype('int')
    parameters_dict['pScenProb'       ] = data_frames['dfScenario']['Probability'].astype('float')

    # Extract and cast nodal parameters
    for suffix in model.nodal_frames_suffixes:
        parameters_dict[f'p{suffix}'] = data_frames[f'df{suffix}'][model.nd] * factor1

    # Merging sets gg and hh
    model.gh = model.gg | model.hh
    # Extract and cast generation parameters
    for suffix in model.gen_frames_suffixes:
        parameters_dict[f'p{suffix}'] = data_frames[f'df{suffix}'][model.gh] * factor1

    # Extract and cast operating reserve parameters for RM and RT markets
    for ind in model.reserves_prefixes:
        parameters_dict[f'pOperatingReservePrice_{ind}'     ] = data_frames[f'dfOperatingReservePrice'     ][ind] * factor1
        parameters_dict[f'pOperatingReserveRequire_{ind}'   ] = data_frames[f'dfOperatingReserveRequire'   ][ind] * factor1
        parameters_dict[f'pOperatingReserveActivation_{ind}'] = data_frames[f'dfOperatingReserveActivation'][ind]

    # compute the Demand as the mean over the time step load levels and assign it to active load levels.
    # Idem for operating reserve, variable max power, variable min and max storage capacity and inflows and outflows
    for ind in model.gen_frames_suffixes + model.nodal_frames_suffixes:
        parameters_dict[f'p{ind}'] = parameters_dict[f'p{ind}'].rolling(parameters_dict['pParTimeStep']).mean()
        parameters_dict[f'p{ind}'].fillna(0.0, inplace=True)

    for idx in model.reserves_prefixes:
        parameters_dict[f'pOperatingReservePrice_{idx}'     ] = parameters_dict[f'pOperatingReservePrice_{idx}'     ].rolling(parameters_dict['pParTimeStep']).mean()
        parameters_dict[f'pOperatingReservePrice_{idx}'     ].fillna(0.0, inplace=True)
        parameters_dict[f'pOperatingReserveRequire_{idx}'   ] = parameters_dict[f'pOperatingReserveRequire_{idx}'   ].rolling(parameters_dict['pParTimeStep']).mean()
        parameters_dict[f'pOperatingReserveRequire_{idx}'   ].fillna(0.0, inplace=True)
        parameters_dict[f'pOperatingReserveActivation_{idx}'] = parameters_dict[f'pOperatingReserveActivation_{idx}'].rolling(parameters_dict['pParTimeStep']).mean()
        parameters_dict[f'pOperatingReserveActivation_{idx}'].fillna(0.0, inplace=True)

    if parameters_dict['pParTimeStep'] > 1:
        # assign duration 0 to load levels not being considered, active load levels are at the end of every pTimeStep
        for i in range(parameters_dict['pParTimeStep']-2,-1,-1):
            parameters_dict['pDuration'].iloc[[range(i, len(model.nn), parameters_dict['pParTimeStep'])]] = 0

    # generation indicators
    generation_ind = data_frames['dfGeneration'].columns.to_list()
    idx_factoring  = ['MaximumPower', 'MinimumPower', 'StandByPower', 'MaximumCharge', 'MinimumCharge', 'OMVariableCost', 'ProductionFunction', 'MaxCompressorConsumption',
                      'RampUp', 'RampDown', 'CO2EmissionRate', 'MaxOutflowsProd', 'MinOutflowsProd', 'MaxInflowsCons', 'MinInflowsCons', 'OutflowsRampDown', 'OutflowsRampUp']
    for idx in generation_ind:
        if idx in idx_factoring:
            parameters_dict[f'pGen{idx}'] = data_frames['dfGeneration'][idx] * factor1
        else:
            parameters_dict[f'pGen{idx}'] = data_frames['dfGeneration'][idx]

    parameters_dict['pGenLinearVarCost'     ] = parameters_dict['pGenLinearTerm'          ] * 1e-3 * parameters_dict['pGenFuelCost'] + parameters_dict['pGenOMVariableCost'] * 1e-3  # linear   term variable cost             [MEUR/GWh]
    parameters_dict['pGenConstantVarCost'   ] = parameters_dict['pGenConstantTerm'        ] * 1e-6 * parameters_dict['pGenFuelCost']                                                 # constant term variable cost             [MEUR/h]
    parameters_dict['pGenCO2EmissionCost'   ] = parameters_dict['pGenCO2EmissionRate'     ] * 1e-3 * parameters_dict['pParCO2Cost']                                                  # CO2 emission cost                       [MEUR/GWh]
    parameters_dict['pGenStartUpCost'       ] = parameters_dict['pGenStartUpCost'         ] * 1e-6                                                                                   # generation startup cost                 [MEUR]
    parameters_dict['pGenShutDownCost'      ] = parameters_dict['pGenShutDownCost'        ] * 1e-6                                                                                   # generation shutdown cost                [MEUR]
    parameters_dict['pGenInvestCost'        ] = parameters_dict['pGenFixedInvestmentCost' ]        * parameters_dict['pGenFixedChargeRate']                                          # generation fixed cost                   [MEUR]
    parameters_dict['pGenRetireCost'        ] = parameters_dict['pGenFixedRetirementCost' ]        * parameters_dict['pGenFixedChargeRate']                                          # generation fixed retirement cost        [MEUR]
    # parameters_dict['pGenOutflowsRampUp'    ] = parameters_dict['pGenOutflowsRampUp'      ] * 1e-3                                                                                   # H2 outflows ramp up   rate              [tonH2]
    # parameters_dict['pGenOutflowsRampDown'  ] = parameters_dict['pGenOutflowsRampDown'      ] * -1                                                                              # H2 outflows ramp down rate              [tonH2]

    parameters_dict['pNodeLat'              ] = data_frames['dfNodeLocation']['Latitude'          ]                                                                                  # node latitude                           [º]
    parameters_dict['pNodeLon'              ] = data_frames['dfNodeLocation']['Longitude'         ]                                                                                  # node longitude                          [º]

    # electricity network indicators
    electricity_network_ind = data_frames['dfElectricityNetwork'].columns.to_list()
    for idx in electricity_network_ind:
        parameters_dict[f'pEleNet{idx}'] = data_frames['dfElectricityNetwork'][idx]

    # hydrogen network indicators
    hydrogen_network_ind = data_frames['dfHydrogenNetwork'].columns.to_list()
    for idx in hydrogen_network_ind:
        parameters_dict[f'pHydNet{idx}'] = data_frames['dfHydrogenNetwork'][idx]

    for net in ['Electricity', 'Hydrogen']:
        parameters_dict[f'p{net[0:3]}NetTTC'                ] = parameters_dict[f'p{net[0:3]}NetTTC'                ] * factor1 * parameters_dict[f'p{net[0:3]}NetSecurityFactor' ]
        parameters_dict[f'p{net[0:3]}NetTTCBck'             ] = parameters_dict[f'p{net[0:3]}NetTTCBck'             ] * factor1 * parameters_dict[f'p{net[0:3]}NetSecurityFactor' ]
        parameters_dict[f'p{net[0:3]}NetFixedInvestmentCost'] = parameters_dict[f'p{net[0:3]}NetFixedInvestmentCost']           * parameters_dict[f'p{net[0:3]}NetFixedChargeRate']
        if net == 'Electricity':
            parameters_dict[f'p{net[0:3]}NetReactance'] = parameters_dict[f'p{net[0:3]}NetReactance'].sort_index()
            parameters_dict[f'p{net[0:3]}NetSwOnTime' ] = parameters_dict[f'p{net[0:3]}NetSwOnTime' ].astype('int')
            parameters_dict[f'p{net[0:3]}NetSwOffTime'] = parameters_dict[f'p{net[0:3]}NetSwOffTime'].astype('int')

    for net in ['Electricity', 'Hydrogen']:
        # replace p{net[0:3]}NetTTCBck = 0.0 by p{net[0:3]}NetTTC
        parameters_dict[f'p{net[0:3]}NetTTCBck'] = parameters_dict[f'p{net[0:3]}NetTTCBck'].where(parameters_dict[f'p{net[0:3]}NetTTCBck'] > 0.0, other=parameters_dict[f'p{net[0:3]}NetTTC'])
        # replace p{net[0:3]}NetTTC = 0.0 by p{net[0:3]}NetTTCBck
        parameters_dict[f'p{net[0:3]}NetTTC'   ] = parameters_dict[f'p{net[0:3]}NetTTC'   ].where(parameters_dict[f'p{net[0:3]}NetTTC'] > 0.0, other=parameters_dict[f'p{net[0:3]}NetTTCBck'])
        # replace p{net[0:3]}NetInvestmentUp= 0.0 by 1.0
        parameters_dict[f'p{net[0:3]}NetInvestmentUp'] = parameters_dict[f'p{net[0:3]}NetInvestmentUp'].where(parameters_dict[f'p{net[0:3]}NetInvestmentUp'] > 0.0, other=1.0)

    parameters_dict[f'pGenInvestmentUp'] = parameters_dict[f'pGenInvestmentUp'].where(parameters_dict[f'pGenInvestmentUp'] > 0.0, other=1.0)

    # minimum up- and downtime converted to an integer number of time steps
    parameters_dict[f'pEleNetSwOnTime' ] = round(parameters_dict[f'pEleNetSwOnTime' ] / parameters_dict['pParTimeStep']).astype('int')

    transforming_time = round(time.time() - start_time)
    print('--- Transforming the dataframes:                                       {} seconds'.format(transforming_time))
    start_time = time.time()

    # %% Getting the branches from the network data
    sEleBr = [(ni,nf) for (ni,nf,cc) in data_frames['dfElectricityNetwork'].index.to_list()]
    sHydBr = [(ni,nf) for (ni,nf,cc) in data_frames['dfHydrogenNetwork'].index.to_list()]
    # Dropping duplicate elements
    sEleBrList = [(ni,nf) for n, (ni,nf) in enumerate(sEleBr) if (ni,nf) not in sEleBr[:n]]
    sHydBrList = [(ni,nf) for n, (ni,nf) in enumerate(sHydBr) if (ni,nf) not in sHydBr[:n]]

    # %% defining subsets: active load levels (n,n2), thermal units (t), RES units (re), ESS units (es), candidate gen units (gc), candidate ESS units (ec), all the electric lines (la),
    # candidate electric lines (lc), electric lines with losses (ll), reference node (rf)
    model.p    = Set(initialize=model.pp                                           , ordered=True , doc='periods               ', filter=lambda model,pp  : pp     in model.pp          and  parameters_dict['pPeriodWeight']            [pp] >  0.0)
    model.sc   = Set(initialize=model.scc                                          , ordered=True , doc='scenarios             ', filter=lambda model,scc : scc    in model.scc                                                                     )
    model.ps   = Set(initialize=model.p*model.sc                                   , ordered=True , doc='periods/scenarios     ', filter=lambda model,p,sc: (p,sc) in model.p*model.sc  and  parameters_dict['pScenProb']              [p,sc] >  0.0)
    model.n    = Set(initialize=model.nn                                           , ordered=True , doc='load levels           ', filter=lambda model,nn  : nn     in model.nn          and  parameters_dict['pDuration']                [nn] >  0  )
    model.n2   = Set(initialize=model.nn                                           , ordered=True , doc='load levels           ', filter=lambda model,nn  : nn     in model.nn          and  parameters_dict['pDuration']                [nn] >  0  )
    model.g    = Set(initialize=model.gg                                           , ordered=False, doc='generating      units ', filter=lambda model,gg  : gg     in model.gg          and (parameters_dict['pGenMaximumPower']         [gg] >  0.0 or   parameters_dict['pGenMaximumCharge'] [gg]      > 0.0)  and parameters_dict['pGenInitialPeriod'][gg]  <= parameters_dict['pParEconomicBaseYear'] and parameters_dict['pGenFinalPeriod'][gg]  >= parameters_dict['pParEconomicBaseYear'])
    model.t    = Set(initialize=model.g                                            , ordered=False, doc='thermal         units ', filter=lambda model,g   : g      in model.g           and  parameters_dict['pGenConstantVarCost']       [g] >  0.0)
    model.re   = Set(initialize=model.g                                            , ordered=False, doc='RES             units ', filter=lambda model,g   : g      in model.g           and  parameters_dict['pGenConstantVarCost']       [g] == 0.0 and  parameters_dict['pGenMaximumStorage'][g]       == 0.0  and parameters_dict['pGenProductionFunction'] [g] == 0.0)
    model.es   = Set(initialize=model.g                                            , ordered=False, doc='ESS             units ', filter=lambda model,g   : g      in model.g           and  parameters_dict['pGenMaximumStorage']        [g]  > 0.0 and (parameters_dict['pVarMaxInflows'].sum()[g]  >  0.0  or  parameters_dict['pVarMaxOutflows'].sum()[g] > 0.0 or parameters_dict['pGenMaximumCharge'][g] > 0.0))
    model.h    = Set(initialize=model.hh                                           , ordered=False, doc='hydrogen        units ', filter=lambda model,hh  : hh     in model.hh          and (parameters_dict['pGenMaximumPower']         [hh]  > 0.0 or   parameters_dict['pGenMaximumCharge'] [hh]      >  0.0) and parameters_dict['pGenInitialPeriod'][hh]  <= parameters_dict['pParEconomicBaseYear'] and parameters_dict['pGenFinalPeriod'][hh]  >= parameters_dict['pParEconomicBaseYear'])
    model.hz   = Set(initialize=model.h                                            , ordered=False, doc='electrolyzer    units ', filter=lambda model,h   : h      in model.h           and                                                               parameters_dict['pGenProductionFunction'][h]   >  0.0)
    model.hs   = Set(initialize=model.h                                            , ordered=False, doc='storage         units ', filter=lambda model,h   : h      in model.h           and  parameters_dict['pGenMaximumStorage']        [h]  > 0.0 and  parameters_dict['pGenProductionFunction'][h]   == 0.0  and (parameters_dict['pVarMaxInflows'].sum()[h]  > 0.0 or parameters_dict['pVarMaxOutflows'].sum()[h]  > 0.0 or parameters_dict['pGenMaximumCharge'][h] > 0.0))
    model.gc   = Set(initialize=model.g                                            , ordered=False, doc='candidate       units ', filter=lambda model,g   : g      in model.g           and  parameters_dict['pGenInvestCost']            [g]  > 0.0)
    model.gd   = Set(initialize=model.g                                            , ordered=False, doc='retirement      units ', filter=lambda model,g   : g      in model.g           and  parameters_dict['pGenRetireCost']            [g] != 0.0)
    model.ec   = Set(initialize=model.es                                           , ordered=False, doc='candidate ESS   units ', filter=lambda model,es  : es     in model.es          and  parameters_dict['pGenInvestCost']           [es] >  0.0)
    model.hc   = Set(initialize=model.hs                                           , ordered=False, doc='candidate H2    units ', filter=lambda model,hs  : hs     in model.hs          and  parameters_dict['pGenInvestCost']           [hs] >  0.0)
    model.ebr  = Set(initialize=sEleBrList                                         , ordered=False, doc='all input    branches '                                                                                                                    )
    model.eln  = Set(initialize=data_frames['dfElectricityNetwork'].index.to_list(), ordered=False, doc='all input       lines '                                                                                                                    )
    model.ela  = Set(initialize=model.eln                                          , ordered=False, doc='all real        lines ', filter=lambda model, *eln: eln   in model.eln         and parameters_dict['pEleNetReactance']          [eln]!= 0.0 and  parameters_dict['pEleNetTTC'][eln]              > 0.0  and parameters_dict['pEleNetTTCBck'][eln] > 0.0 and parameters_dict['pEleNetInitialPeriod'][eln]  <= parameters_dict['pParEconomicBaseYear'] and parameters_dict['pEleNetFinalPeriod'][eln]  >= parameters_dict['pParEconomicBaseYear'])
    model.els  = Set(initialize=model.ela                                          , ordered=False, doc='all real switch lines ', filter=lambda model, *ela: ela   in model.ela         and parameters_dict['pEleNetSwitching']          [ela]      )
    model.elc  = Set(initialize=model.ela                                          , ordered=False, doc='candidate       lines ', filter=lambda model, *ela: ela   in model.ela         and parameters_dict['pEleNetFixedInvestmentCost'][ela]>  0.0)
    model.ell  = Set(initialize=model.ela                                          , ordered=False, doc='loss            lines ', filter=lambda model, *ela: ela   in model.ela         and parameters_dict['pEleNetLossFactor']         [ela]>  0.0 and  parameters_dict['pOptIndBinNetLosses']          > 0  )
    model.ndrf = Set(initialize=model.nd                                           , ordered=True , doc='reference node        ', filter=lambda model,nd  : nd     in                       parameters_dict['pParReferenceNode']                    )
    model.hbr  = Set(initialize=sHydBrList                                         , ordered=False, doc='all input    branches '                                                                                                                    )
    model.hpn  = Set(initialize=data_frames['dfHydrogenNetwork'].index.to_list()   , ordered=False, doc='all input H2 pipelines'                                                                                                                    )
    model.hpa  = Set(initialize=model.hpn                                          , ordered=False, doc='all real  H2 pipelines', filter=lambda model, *hpn: hpn     in model.hpn       and                                                               parameters_dict['pHydNetTTC'][hpn]               > 0.0 and parameters_dict['pHydNetTTCBck'][hpn] > 0.0 and parameters_dict['pHydNetInitialPeriod'][hpn]  <= parameters_dict['pParEconomicBaseYear'] and parameters_dict['pHydNetFinalPeriod'][hpn]  >= parameters_dict['pParEconomicBaseYear'])
    model.hpc  = Set(initialize=model.hpa                                          , ordered=False, doc='candidate H2 pipelines', filter=lambda model, *hpa: hpa     in model.hpa       and parameters_dict['pHydNetFixedInvestmentCost'][hpa] > 0.0)


    model.nr   = model.g   - model.re            # non-RES units, they can be committed and also contribute to the operating reserves
    model.ele  = model.ela - model.elc           # existing electric lines (le)
    model.hpe  = model.hpa - model.hpc           # existing hydrogen pipelines (pe)

    model.eh   = model.es | model.hz             # set for the electricity consumption
    model.he   = model.hs | model.t              # set for the hydrogen consumption
    model.ess  = model.es | model.hs             # set for the electricity and hydrogen ESS
    model.esc  = model.ec | model.hc             # set for the candidate ESS and hydrogen units


    print('--- Defining the sets:                                                 {} seconds'.format(round(time.time() - start_time)))

    # instrumental sets
    model.psc      = [(p, sc            )        for p, sc                    in model.p     * model.sc ]
    model.pn       = [(p, n             )        for p, n                     in model.p     * model.n  ]
    model.pes      = [(p, es            )        for p, es                    in model.p     * model.es ]
    model.pess     = [(p, ess           )        for p, ess                   in model.p     * model.ess]
    model.pngg     = [(p, n , g         )        for p, n , g                 in model.pn    * model.gg ]
    model.pngh     = [(p, n , g         )        for p, n , g                 in model.pn    * model.gh ]
    model.png      = [(p, n , g         )        for p, n , g                 in model.pn    * model.g  ]
    model.pnt      = [(p, n , t         )        for p, n , t                 in model.pn    * model.t  ]
    model.pnnd     = [(p, n , nd        )        for p, n , nd                in model.pn    * model.nd ]
    model.pnre     = [(p, n , re        )        for p, n , re                in model.pn    * model.re ]
    model.pnes     = [(p, n , es        )        for p, n , es                in model.pn    * model.es ]
    model.pnnr     = [(p, n , nr        )        for p, n , nr                in model.pn    * model.nr ]
    model.pngt     = [(p, n , gt        )        for p, n , gt                in model.pn    * model.gt ]
    model.pnhe     = [(p, n , he        )        for p, n , he                in model.pn    * model.he ]
    model.pneh     = [(p, n , eh        )        for p, n , eh                in model.pn    * model.eh ]
    model.pness    = [(p, n , es        )        for p, n , es                in model.pn    * model.ess]
    model.pnesc    = [(p, n , esc       )        for p, n , esc               in model.pn    * model.esc]
    model.pnh      = [(p, n , h         )        for p, n , h                 in model.pn    * model.h  ]
    model.pnhz     = [(p, n , hz        )        for p, n , hz                in model.pn    * model.hz ]
    model.pnhs     = [(p, n , hs        )        for p, n , hs                in model.pn    * model.hs ]
    model.pneln    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.eln]
    model.pnela    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.ela]
    model.pnele    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.ele]
    model.pnell    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.ell]
    model.pnels    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.els]
    model.pnhpa    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.hpa]
    model.pnhpc    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.hpc]
    model.pnhpe    = [(p, n , ni, nf, cc)        for p, n , ni, nf, cc        in model.pn    * model.hpe]
    model.psg      = [(p, sc, g         )        for p, sc, g                 in model.psc   * model.g  ]
    model.psnr     = [(p, sc, nr        )        for p, sc, nr                in model.psc   * model.nr ]
    model.pses     = [(p, sc, es        )        for p, sc, es                in model.psc   * model.es ]
    model.psess    = [(p, sc, ess       )        for p, sc, ess               in model.psc   * model.ess]

    model.psn      = [(p, sc, n            )     for p, sc, n                 in model.psc   * model.n  ]
    model.psng     = [(p, sc, n, g         )     for p, sc, n, g              in model.psn   * model.g  ]
    model.psngg    = [(p, sc, n, gg        )     for p, sc, n, gg             in model.psn   * model.gg ]
    model.psngh    = [(p, sc, n, gh        )     for p, sc, n, gh             in model.psn   * model.gh ]
    model.psnt     = [(p, sc, n, t         )     for p, sc, n, t              in model.psn   * model.t  ]
    model.psngc    = [(p, sc, n, gc        )     for p, sc, n, gc             in model.psn   * model.gc ]
    model.psnre    = [(p, sc, n, re        )     for p, sc, n, re             in model.psn   * model.re ]
    model.psnnr    = [(p, sc, n, nr        )     for p, sc, n, nr             in model.psn   * model.nr ]
    model.psnes    = [(p, sc, n, es        )     for p, sc, n, es             in model.psn   * model.es ]
    model.psnec    = [(p, sc, n, ec        )     for p, sc, n, ec             in model.psn   * model.ec ]
    model.psnhz    = [(p, sc, n, hz        )     for p, sc, n, hz             in model.psn   * model.hz ]
    model.psnnd    = [(p, sc, n, nd        )     for p, sc, n, nd             in model.psn   * model.nd ]
    model.psngt    = [(p, sc, n, gt        )     for p, sc, n, gt             in model.psn   * model.gt ]
    model.psneh    = [(p, sc, n, eh        )     for p, sc, n, eh             in model.psn   * model.eh ]
    model.psnhe    = [(p, sc, n, he        )     for p, sc, n, he             in model.psn   * model.he ]
    model.psness   = [(p, sc, n, es        )     for p, sc, n, es             in model.psn   * model.ess]
    model.psnesc   = [(p, sc, n, esc       )     for p, sc, n, esc            in model.psn   * model.esc]
    model.psnh     = [(p, sc, n, h         )     for p, sc, n, h              in model.psn   * model.h  ]
    model.psnhz    = [(p, sc, n, hz        )     for p, sc, n, hz             in model.psn   * model.hz ]
    model.psnhs    = [(p, sc, n, hs        )     for p, sc, n, hs             in model.psn   * model.hs ]
    model.psneln   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.eln]
    model.psnela   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.ela]
    model.psnele   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.ele]
    model.psnell   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.ell]
    model.psnels   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.els]
    model.psnhpn   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.hpn]
    model.psnhpa   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.hpa]
    model.psnhpe   = [(p, sc, n, ni, nf, cc)     for p, sc, n, ni, nf, cc     in model.psn   * model.hpe]

    # replacing string values by numerical values
    idxDict        = dict()
    idxDict[0    ] = 0
    idxDict[0.0  ] = 0
    idxDict['No' ] = 0
    idxDict['NO' ] = 0
    idxDict['no' ] = 0
    idxDict['N'  ] = 0
    idxDict['n'  ] = 0
    idxDict['Yes'] = 1
    idxDict['YES'] = 1
    idxDict['yes'] = 1
    idxDict['Y'  ] = 1
    idxDict['y'  ] = 1

    parameters_dict['pGenBinaryInvestment'   ] = parameters_dict['pGenBinaryInvestment'   ].map(idxDict)
    parameters_dict['pGenBinaryRetirement'   ] = parameters_dict['pGenBinaryRetirement'   ].map(idxDict)
    parameters_dict['pGenBinaryCommitment'   ] = parameters_dict['pGenBinaryCommitment'   ].map(idxDict)
    parameters_dict['pGenStorageInvestment'  ] = parameters_dict['pGenStorageInvestment'  ].map(idxDict)
    parameters_dict['pEleNetBinaryInvestment'] = parameters_dict['pEleNetBinaryInvestment'].map(idxDict)
    parameters_dict['pEleNetSwitching'       ] = parameters_dict['pEleNetSwitching'       ].map(idxDict)
    parameters_dict['pHydNetBinaryInvestment'] = parameters_dict['pHydNetBinaryInvestment'].map(idxDict)
    parameters_dict['pGenNoOperatingReserve' ] = parameters_dict['pGenNoOperatingReserve' ].map(idxDict)
    parameters_dict['pGenMaxCommitment'      ] = parameters_dict['pGenMaxCommitment'      ].map(idxDict)
    parameters_dict['pGenStandByStatus'      ] = parameters_dict['pGenStandByStatus'      ].map(idxDict)

    # define AC existing  lines
    model.elea = Set(initialize=model.ele, ordered=False, doc='AC existing  lines and non-switchable lines', filter=lambda model,*ele: ele in model.ele and not parameters_dict['pEleNetType'][ele] == 'DC')
    # define AC candidate lines
    model.elca = Set(initialize=model.ela, ordered=False, doc='AC candidate lines and     switchable lines', filter=lambda model,*elc: elc in model.elc and not parameters_dict['pEleNetType'][elc] == 'DC')

    model.elaa = model.elea | model.elca

    # define DC existing  lines
    model.eled = Set(initialize=model.ele, ordered=False, doc='DC existing  lines and non-switchable lines', filter=lambda model,*ele: ele in model.ele and     parameters_dict['pEleNetType'][ele] == 'DC')
    # define DC candidate lines
    model.elcd = Set(initialize=model.ela, ordered=False, doc='DC candidate lines and     switchable lines', filter=lambda model,*elc: elc in model.elc and     parameters_dict['pEleNetType'][elc] == 'DC')

    model.elad = model.eled | model.elcd

    # %% Getting the current year
    pCurrentYear = datetime.date.today().year
    if parameters_dict['pParEconomicBaseYear'] == 0:
        parameters_dict['pParEconomicBaseYear'] = pCurrentYear

    if parameters_dict['pParAnnualDiscountRate'] == 0.0:
        parameters_dict['pDiscountFactor'] = pd.Series(data=[                                                  parameters_dict['pPeriodWeight'][p]                                                                                                                                                                                       for p in model.p], index=model.p)
    else:
        parameters_dict['pDiscountFactor'] = pd.Series(data=[((1.0+parameters_dict['pParAnnualDiscountRate'])**parameters_dict['pPeriodWeight'][p]-1.0) / (parameters_dict['pParAnnualDiscountRate']*(1.0+parameters_dict['pParAnnualDiscountRate'])**(parameters_dict['pPeriodWeight'][p]-1+p-parameters_dict['pParEconomicBaseYear'])) for p in model.p], index=model.p)

    # %% inverse index node to electricity unit
    model.n2g        = Set(initialize=sorted((parameters_dict['pGenNode'][g], g)      for     g     in model.g                                                                 ), ordered=False, doc='node to generator'      )
    model.z2g        = Set(initialize=sorted((zn,g)                                   for (nd,g,zn) in model.n2g * model.zn if (nd,zn) in model.ndzn                           ), ordered=False, doc='zone to generator'      )

    # %% inverse index node to hydrogen unit
    model.n2h        = Set(initialize=sorted((parameters_dict['pGenNode'][h], h)      for     h     in model.h                                                                 ), ordered=False, doc='node to generator'      )
    model.z2h        = Set(initialize=sorted((zn,h)                                   for (nd,h,zn) in model.n2h * model.zn if (nd,zn) in model.ndzn                           ), ordered=False, doc='zone to generator'      )

    # inverse index generator to technology
    model.t2g        = Set(initialize=sorted((parameters_dict['pGenTechnology'][g],g) for     g     in model.g              if parameters_dict['pGenTechnology'][g] in model.gt), ordered=False, doc='technology to generator')
    model.t2h        = Set(initialize=sorted((parameters_dict['pGenTechnology'][h],h) for     h     in model.h              if parameters_dict['pGenTechnology'][h] in model.gt), ordered=False, doc='technology to generator')

    # ESS and RES technologies
    model.ot         = Set(initialize=model.gt, ordered=False, doc='Electricity ESS technologies', filter=lambda model, gt: gt in model.gt and sum(1 for es in model.es if (gt, es) in model.t2g))
    model.ht         = Set(initialize=model.gt, ordered=False, doc='Hydrogen    ESS technologies', filter=lambda model, gt: gt in model.gt and sum(1 for hs in model.hs if (gt, hs) in model.t2h))
    model.rt         = Set(initialize=model.gt, ordered=False, doc='RES technologies'            , filter=lambda model, gt: gt in model.gt and sum(1 for re in model.re if (gt, re) in model.t2g))

    model.psot  = [(p, sc, ot)    for p, sc, ot    in model.ps  * model.ot]
    model.psht  = [(p, sc, ht)    for p, sc, ht    in model.ps  * model.ht]
    model.psrt  = [(p, sc, rt)    for p, sc, rt    in model.ps  * model.rt]
    model.psnot = [(p, sc, n, ot) for p, sc, n, ot in model.psn * model.ot]
    model.psnht = [(p, sc, n, ht) for p, sc, n, ht in model.psn * model.ht]
    model.psnrt = [(p, sc, n, rt) for p, sc, n, rt in model.psn * model.rt]

    print('--- Defining the instrumental sets:                                    {} seconds'.format(round(time.time() - start_time)))

    # minimum and maximum variable power, charge, and storage capacity
    parameters_dict[f'pMinPower'   ] = parameters_dict[f'pVarMinGeneration'  ].replace(0.0, parameters_dict['pGenMinimumPower'   ])
    parameters_dict[f'pMaxPower'   ] = parameters_dict[f'pVarMaxGeneration'  ].replace(0.0, parameters_dict['pGenMaximumPower'   ])
    parameters_dict[f'pMinCharge'  ] = parameters_dict[f'pVarMinConsumption' ].replace(0.0, parameters_dict['pGenMinimumCharge'  ])
    parameters_dict[f'pMaxCharge'  ] = parameters_dict[f'pVarMaxConsumption' ].replace(0.0, parameters_dict['pGenMaximumCharge'  ])
    parameters_dict[f'pMinStorage' ] = parameters_dict[f'pVarMinStorage'     ].replace(0.0, parameters_dict['pGenMinimumStorage' ])
    parameters_dict[f'pMaxStorage' ] = parameters_dict[f'pVarMaxStorage'     ].replace(0.0, parameters_dict['pGenMaximumStorage' ])
    parameters_dict[f'pMinInflows' ] = parameters_dict[f'pVarMinInflows'     ].replace(0.0, parameters_dict['pGenMinInflowsCons' ])
    parameters_dict[f'pMaxInflows' ] = parameters_dict[f'pVarMaxInflows'     ].replace(0.0, parameters_dict['pGenMaxInflowsCons' ])
    parameters_dict[f'pMinOutflows'] = parameters_dict[f'pVarMinOutflows'    ].replace(0.0, parameters_dict['pGenMinOutflowsProd'])
    parameters_dict[f'pMaxOutflows'] = parameters_dict[f'pVarMaxOutflows'    ].replace(0.0, parameters_dict['pGenMaxOutflowsProd'])
    parameters_dict[f'pMinFuelCost'] = parameters_dict[f'pVarMinFuelCost'    ].replace(0.0, parameters_dict['pGenLinearVarCost'  ])
    parameters_dict[f'pMaxFuelCost'] = parameters_dict[f'pVarMaxFuelCost'    ].replace(0.0, parameters_dict['pGenLinearVarCost'  ])
    parameters_dict[f'pMinCO2Cost' ] = parameters_dict[f'pVarMinEmissionCost'].replace(0.0, parameters_dict['pGenCO2EmissionCost'])
    parameters_dict[f'pMaxCO2Cost' ] = parameters_dict[f'pVarMaxEmissionCost'].replace(0.0, parameters_dict['pGenCO2EmissionCost'])

    for idx in ['MinPower', 'MaxPower', 'MinCharge', 'MaxCharge', 'MinStorage', 'MaxStorage', 'MinInflows', 'MaxInflows', 'MinOutflows', 'MaxOutflows', 'MinFuelCost', 'MaxFuelCost', 'MinCO2Cost', 'MaxCO2Cost']:
        parameters_dict[f'p{idx}'] = parameters_dict[f'p{idx}'].where(parameters_dict[f'p{idx}'] > 0.0, other=0.0)

    # parameter that allows the initial inventory to change with load level
    parameters_dict[f'pInitialInventory'] = pd.DataFrame([parameters_dict[f'pGenInitialStorage']] * len(parameters_dict[f'pMinStorage'].index), index=parameters_dict[f'pMinStorage'].index, columns=parameters_dict[f'pGenInitialStorage'].index)

    # minimum up- and downtime and maximum shift time converted to an integer number of time steps
    for idx in ['Up', 'Down']:
        parameters_dict[f'pGen{idx}Time'] = round(parameters_dict[f'pGen{idx}Time'] / parameters_dict['pParTimeStep']).astype('int')

    # %% definition of the time-steps leap to observe the stored energy at an ESS
    idxCycle            = dict()
    idxCycle[0        ] = 8736
    idxCycle[0.0      ] = 8736
    idxCycle['Hourly' ] = 1
    idxCycle['Daily'  ] = 1
    idxCycle['Weekly' ] = round(24  / parameters_dict['pParTimeStep'])
    idxCycle['Monthly'] = round(168 / parameters_dict['pParTimeStep'])
    idxCycle['Yearly' ] = round(168 / parameters_dict['pParTimeStep'])

    idxOutflows            = dict()
    idxOutflows[0        ] = 8736
    idxOutflows[0.0      ] = 8736
    idxOutflows['Hourly' ] =    1
    idxOutflows['Daily'  ] = round(24   / parameters_dict['pParTimeStep'])
    idxOutflows['Weekly' ] = round(168  / parameters_dict['pParTimeStep'])
    idxOutflows['Monthly'] = round(672  / parameters_dict['pParTimeStep'])
    idxOutflows['Yearly' ] = round(8736 / parameters_dict['pParTimeStep'])

    parameters_dict['pCycleTimeStep'   ] = parameters_dict['pGenStorageType' ].map(idxCycle                                                                                                                  ).astype('int')
    parameters_dict['pOutflowsTimeStep'] = parameters_dict['pGenOutflowsType'].map(idxOutflows).where(parameters_dict['pVarMinOutflows'].sum() + parameters_dict['pVarMaxOutflows'].sum() > 0.0, other = 8736).astype('int')
    parameters_dict['pCycleTimeStep'   ] = pd.concat([parameters_dict['pCycleTimeStep'], parameters_dict['pOutflowsTimeStep']], axis=1).min(axis=1)
    # mapping the string pParDemandType using the idxCycle dictionary
    parameters_dict['pParDemandType'   ] = idxOutflows[parameters_dict['pParDemandType']]
    # drop levels with duration 0
    parameters_dict['pDuration']            = parameters_dict['pDuration'].loc           [model.n  ]

    parameters_dict[f'pElectricityDemand'] = parameters_dict[f'pElectricityDemand'].loc[model.psn]
    parameters_dict[f'pHydrogenDemand'   ] = parameters_dict[f'pHydrogenDemand'   ].loc[model.psn]
    parameters_dict[f'pElectricityCost'  ] = parameters_dict[f'pElectricityCost'  ].loc[model.psn]
    parameters_dict[f'pElectricityPrice' ] = parameters_dict[f'pElectricityPrice' ].loc[model.psn]
    parameters_dict[f'pHydrogenCost'     ] = parameters_dict[f'pHydrogenCost'     ].loc[model.psn]
    parameters_dict[f'pHydrogenPrice'    ] = parameters_dict[f'pHydrogenPrice'    ].loc[model.psn]
    parameters_dict[f'pMinPower'         ] = parameters_dict[f'pMinPower'         ].loc[model.psn]
    parameters_dict[f'pMaxPower'         ] = parameters_dict[f'pMaxPower'         ].loc[model.psn]
    parameters_dict[f'pMinCharge'        ] = parameters_dict[f'pMinCharge'        ].loc[model.psn]
    parameters_dict[f'pMaxCharge'        ] = parameters_dict[f'pMaxCharge'        ].loc[model.psn]
    parameters_dict[f'pInitialInventory' ] = parameters_dict[f'pInitialInventory' ].loc[model.psn]
    parameters_dict[f'pMinStorage'       ] = parameters_dict[f'pMinStorage'       ].loc[model.psn]
    parameters_dict[f'pMaxStorage'       ] = parameters_dict[f'pMaxStorage'       ].loc[model.psn]
    parameters_dict[f'pMinInflows'       ] = parameters_dict[f'pMinInflows'       ].loc[model.psn]
    parameters_dict[f'pMaxInflows'       ] = parameters_dict[f'pMaxInflows'       ].loc[model.psn]
    parameters_dict[f'pMinOutflows'      ] = parameters_dict[f'pMinOutflows'      ].loc[model.psn]
    parameters_dict[f'pMaxOutflows'      ] = parameters_dict[f'pMaxOutflows'      ].loc[model.psn]
    parameters_dict[f'pVarMinInflows'    ] = parameters_dict[f'pVarMinInflows'    ].loc[model.psn]
    parameters_dict[f'pVarMaxInflows'    ] = parameters_dict[f'pVarMaxInflows'    ].loc[model.psn]
    parameters_dict[f'pVarMinOutflows'   ] = parameters_dict[f'pVarMinOutflows'   ].loc[model.psn]
    parameters_dict[f'pVarMaxOutflows'   ] = parameters_dict[f'pVarMaxOutflows'   ].loc[model.psn]

    for idx in model.reserves_prefixes:
        parameters_dict[f'pOperatingReservePrice_{idx}'     ] = parameters_dict[f'pOperatingReservePrice_{idx}'     ].loc[model.psn]
        parameters_dict[f'pOperatingReserveRequire_{idx}'   ] = parameters_dict[f'pOperatingReserveRequire_{idx}'   ].loc[model.psn]
        parameters_dict[f'pOperatingReserveActivation_{idx}'] = parameters_dict[f'pOperatingReserveActivation_{idx}'].loc[model.psn]

    # values < 1e-5 times the maximum system demand are converted to 0
    pEleEpsilon = (parameters_dict['pElectricityDemand'][[nd for nd in model.nd]].sum(axis=1).max()) * 1e-5
    pHydEpsilon = (parameters_dict['pHydrogenDemand'   ][[nd for nd in model.nd]].sum(axis=1).max()) * 1e-5

    # these parameters are in GW or tH2
    parameters_dict[f'pElectricityDemand'][parameters_dict[f'pElectricityDemand'] < pEleEpsilon] = 0.0
    parameters_dict[f'pElectricityCost'  ][parameters_dict[f'pElectricityCost'  ] < pEleEpsilon] = 0.0
    parameters_dict[f'pElectricityPrice' ][parameters_dict[f'pElectricityPrice' ] < pEleEpsilon] = 0.0
    parameters_dict[f'pHydrogenDemand'   ][parameters_dict[f'pHydrogenDemand'   ] < pHydEpsilon] = 0.0
    parameters_dict[f'pHydrogenCost'     ][parameters_dict[f'pHydrogenCost'     ] < pHydEpsilon] = 0.0
    parameters_dict[f'pHydrogenPrice'    ][parameters_dict[f'pHydrogenPrice'    ] < pHydEpsilon] = 0.0
    parameters_dict[f'pMinPower'         ][parameters_dict[f'pMinPower'         ] < max(pEleEpsilon,pHydEpsilon)] = 0.0
    parameters_dict[f'pMaxPower'         ][parameters_dict[f'pMaxPower'         ] < max(pEleEpsilon,pHydEpsilon)] = 0.0
    parameters_dict[f'pMinCharge'        ][parameters_dict[f'pMinCharge'        ] < max(pEleEpsilon,pHydEpsilon)] = 0.0
    parameters_dict[f'pMaxCharge'        ][parameters_dict[f'pMaxCharge'        ] < max(pEleEpsilon,pHydEpsilon)] = 0.0
    parameters_dict[f'pMinInflows'       ][parameters_dict[f'pMinInflows'       ] < max(pEleEpsilon,pHydEpsilon)/parameters_dict['pParTimeStep']] = 0.0
    parameters_dict[f'pMaxInflows'       ][parameters_dict[f'pMaxInflows'       ] < max(pEleEpsilon,pHydEpsilon)/parameters_dict['pParTimeStep']] = 0.0
    parameters_dict[f'pMinOutflows'      ][parameters_dict[f'pMinOutflows'      ] < max(pEleEpsilon,pHydEpsilon)/parameters_dict['pParTimeStep']] = 0.0
    parameters_dict[f'pMaxOutflows'      ][parameters_dict[f'pMaxOutflows'      ] < max(pEleEpsilon,pHydEpsilon)/parameters_dict['pParTimeStep']] = 0.0
    parameters_dict[f'pMinFuelCost'      ][parameters_dict[f'pMinFuelCost'      ] < max(pEleEpsilon,pHydEpsilon)] = 0.0
    parameters_dict[f'pMaxFuelCost'      ][parameters_dict[f'pMaxFuelCost'      ] < max(pEleEpsilon,pHydEpsilon)] = 0.0
    parameters_dict[f'pMinCO2Cost'       ][parameters_dict[f'pMinCO2Cost'       ] < max(pEleEpsilon,pHydEpsilon)] = 0.0
    parameters_dict[f'pMaxCO2Cost'       ][parameters_dict[f'pMaxCO2Cost'       ] < max(pEleEpsilon,pHydEpsilon)] = 0.0

    for idx in model.reserves_prefixes:
        parameters_dict[f'pOperatingReservePrice_{idx}'     ][parameters_dict[f'pOperatingReservePrice_{idx}'     ] < pEleEpsilon] = 0.0
        parameters_dict[f'pOperatingReserveRequire_{idx}'   ][parameters_dict[f'pOperatingReserveRequire_{idx}'   ] < pEleEpsilon] = 0.0
        parameters_dict[f'pOperatingReserveActivation_{idx}'][parameters_dict[f'pOperatingReserveActivation_{idx}'] < pEleEpsilon] = 0.0

    # these parameters are in GWh
    parameters_dict[f'pMinStorage'      ][parameters_dict[f'pMinStorage'      ] < pEleEpsilon] = 0.0
    parameters_dict[f'pMaxStorage'      ][parameters_dict[f'pMaxStorage'      ] < pEleEpsilon] = 0.0
    parameters_dict[f'pInitialInventory'][parameters_dict[f'pInitialInventory'] < pEleEpsilon] = 0.0

    for network in ['Ele', 'Hyd']:
        if network == 'Ele':
            pEpsilon = pEleEpsilon
        else:
            pEpsilon = pHydEpsilon
        parameters_dict[f'p{network}NetTTC'   ].update(pd.Series([0.0 for ni, nf, cc in parameters_dict[f'p{network}NetTTC'].index if parameters_dict[f'p{network}NetTTC'   ][ni, nf, cc] < pEpsilon], index=[(ni, nf, cc) for ni, nf, cc in parameters_dict[f'p{network}NetTTC'].index if parameters_dict[f'p{network}NetTTC'   ][ni, nf, cc] < pEpsilon], dtype='float64'))
        parameters_dict[f'p{network}NetTTCBck'].update(pd.Series([0.0 for ni, nf, cc in parameters_dict[f'p{network}NetTTC'].index if parameters_dict[f'p{network}NetTTCBck'][ni, nf, cc] < pEpsilon], index=[(ni, nf, cc) for ni, nf, cc in parameters_dict[f'p{network}NetTTC'].index if parameters_dict[f'p{network}NetTTCBck'][ni, nf, cc] < pEpsilon], dtype='float64'))
        parameters_dict[f'p{network}NetTTCMax'] = parameters_dict[f'p{network}NetTTC'].where(parameters_dict[f'p{network}NetTTC'] > parameters_dict[f'p{network}NetTTCBck'], parameters_dict[f'p{network}NetTTCBck'])

    parameters_dict[f'pMaxPower2ndBlock' ] = parameters_dict[f'pMaxPower' ] - parameters_dict[f'pMinPower']
    parameters_dict[f'pMaxCharge2ndBlock'] = parameters_dict[f'pMaxCharge'] - parameters_dict[f'pMinCharge']
    parameters_dict[f'pMaxCapacity'      ] = parameters_dict[f'pMaxPower' ].where(parameters_dict[f'pMaxPower'] > parameters_dict[f'pMaxCharge'], parameters_dict[f'pMaxCharge'])

    parameters_dict[f'pMaxPower2ndBlock' ][parameters_dict[f'pMaxPower2ndBlock' ] < pEleEpsilon] = 0.0
    parameters_dict[f'pMaxCharge2ndBlock'][parameters_dict[f'pMaxCharge2ndBlock'] < pEleEpsilon] = 0.0

    # replace < 0.0 by 0.0
    parameters_dict[f'pMaxPower2ndBlock' ] = parameters_dict[f'pMaxPower2ndBlock' ].where(parameters_dict[f'pMaxPower2ndBlock' ] > 0.0, 0.0)
    parameters_dict[f'pMaxCharge2ndBlock'] = parameters_dict[f'pMaxCharge2ndBlock'].where(parameters_dict[f'pMaxCharge2ndBlock'] > 0.0, 0.0)

    parameters_dict[f'pMaxInflows2ndBlock' ] = parameters_dict[f'pMaxInflows' ] - parameters_dict[f'pMinInflows' ]
    parameters_dict[f'pMaxInflows2ndBlock' ][parameters_dict[f'pMaxInflows2ndBlock' ] < pEleEpsilon] = 0.0

    parameters_dict[f'pMaxOutflows2ndBlock'] = parameters_dict[f'pMaxOutflows'] - parameters_dict[f'pMinOutflows']
    parameters_dict[f'pMaxOutflows2ndBlock'][parameters_dict[f'pMaxOutflows2ndBlock'] < pEleEpsilon] = 0.0
    # replace < 0.0 by 0.0
    parameters_dict[f'pMaxOutflows2ndBlock'] = parameters_dict[f'pMaxOutflows2ndBlock'].where(parameters_dict[f'pMaxOutflows2ndBlock'] > 0.0, 0.0)

    # drop generators not nr or ec
    parameters_dict['pGenStartUpCost'         ] = parameters_dict['pGenStartUpCost'         ].loc[model.gh ]
    parameters_dict['pGenShutDownCost'        ] = parameters_dict['pGenShutDownCost'        ].loc[model.gh ]
    parameters_dict['pGenBinaryCommitment'    ] = parameters_dict['pGenBinaryCommitment'    ].loc[model.gh ]
    parameters_dict['pGenStorageInvestment'   ] = parameters_dict['pGenStorageInvestment'   ].loc[model.esc]
    parameters_dict['pGenMaxInflowsCons'      ] = parameters_dict['pGenMaxInflowsCons'      ].loc[model.esc]
    parameters_dict['pGenMinInflowsCons'      ] = parameters_dict['pGenMinInflowsCons'      ].loc[model.esc]
    parameters_dict['pGenMaxOutflowsProd'     ] = parameters_dict['pGenMaxOutflowsProd'     ].loc[model.esc]
    parameters_dict['pGenMinOutflowsProd'     ] = parameters_dict['pGenMinOutflowsProd'     ].loc[model.esc]

    # drop lines not lc or ll
    parameters_dict['pEleNetFixedInvestmentCost'] = parameters_dict['pEleNetFixedInvestmentCost'].loc[model.elc]
    parameters_dict['pEleNetInvestmentLo'       ] = parameters_dict['pEleNetInvestmentLo'       ].loc[model.elc]
    parameters_dict['pEleNetInvestmentUp'       ] = parameters_dict['pEleNetInvestmentUp'       ].loc[model.elc]
    parameters_dict['pEleNetLossFactor'         ] = parameters_dict['pEleNetLossFactor'         ].loc[model.ell]

    # this option avoids a warning in the following assignments
    pd.options.mode.chained_assignment = None

    # drop pipelines not pc
    parameters_dict['pHydNetFixedInvestmentCost'] = parameters_dict['pHydNetFixedInvestmentCost'].loc[model.hpc]
    parameters_dict['pHydNetInvestmentLo'       ] = parameters_dict['pHydNetInvestmentLo'       ].loc[model.hpc]
    parameters_dict['pHydNetInvestmentUp'       ] = parameters_dict['pHydNetInvestmentUp'       ].loc[model.hpc]

    # replace very small costs by 0
    pEpsilon = 1e-4  # this value in €/GWh is related to the smallest reduced cost
    parameters_dict['pGenLinearTerm'  ][parameters_dict['pGenLinearTerm'  ] < pEpsilon] = 0.0
    parameters_dict['pGenConstantTerm'][parameters_dict['pGenConstantTerm'] < pEpsilon] = 0.0
    #
    # parameters_dict['pGenLinearTerm'].update  (pd.Series([0.0 for gg in model.gg if parameters_dict['pGenLinearTerm'  ][gg] < pEpsilon], index=[gg for gg in model.gh if parameters_dict['pGenLinearTerm'  ][gg] < pEpsilon]))
    # parameters_dict['pGenConstantTerm'].update(pd.Series([0.0 for gg in model.gg if parameters_dict['pGenConstantTerm'][gg] < pEpsilon], index=[gg for gg in model.gh if parameters_dict['pGenConstantTerm'][gg] < pEpsilon]))
    # parameters_dict['pGenStartUpCost'].update (pd.Series([0.0 for nr in model.nr if parameters_dict['pGenStartUpCost' ][nr] < pEpsilon], index=[nr for nr in model.gh if parameters_dict['pGenStartUpCost' ][nr] < pEpsilon]))
    # parameters_dict['pGenShutDownCost'].update(pd.Series([0.0 for nr in model.nr if parameters_dict['pGenShutDownCost'][nr] < pEpsilon], index=[nr for nr in model.gh if parameters_dict['pGenShutDownCost'][nr] < pEpsilon]))

    parameters_dict['pPeriodProb'] = parameters_dict['pScenProb'].copy()

    for p,sc in model.ps:
        # periods and scenarios are going to be solved together with their weight and probability
        parameters_dict['pPeriodProb'][p,sc] = parameters_dict['pPeriodWeight'][p] * parameters_dict['pScenProb'][p,sc]

    # load levels multiple of cycles for each ESS/generator
    model.nesct = [(n,es )    for n,es    in model.n * model.es  if model.n.ord(n) % parameters_dict['pCycleTimeStep'   ][es ] == 0]
    model.nhsct = [(n,hs )    for n,hs    in model.n * model.hs  if model.n.ord(n) % parameters_dict['pCycleTimeStep'   ][hs ] == 0]
    model.necct = [(n,ec )    for n,ec    in model.n * model.ec  if model.n.ord(n) % parameters_dict['pCycleTimeStep'   ][ec ] == 0]
    model.nesot = [(n,ess)    for n,ess   in model.n * model.ess if model.n.ord(n) % parameters_dict['pOutflowsTimeStep'][ess] == 0]

    # # ESS with outflows
    model.psesi = [(p,sc,ess) for p,sc,ess in model.psess if sum(parameters_dict['pVarMaxInflows' ][ess][p,sc,n2] for n2 in model.n2)]
    model.pseso = [(p,sc,ess) for p,sc,ess in model.psess if sum(parameters_dict['pVarMaxOutflows'][ess][p,sc,n2] for n2 in model.n2)]

    # if line length = 0 changed to geographical distance with an additional 10%
    for network in ['Ele', 'Hyd']:
        if network == 'Ele':
            snet = model.ela
        else:
            snet = model.hpa
        for ni, nf, cc in snet:
            if parameters_dict[f'p{network}NetLength'][ni,nf,cc] == 0.0:
                parameters_dict[f'p{network}NetLength'][ni,nf,cc]   =  1.1 * 6371 * 2 * math.asin(math.sqrt(math.pow(math.sin((parameters_dict['pNodeLat'][nf]-parameters_dict['pNodeLat'][ni])*math.pi/180/2),2) + math.cos(parameters_dict['pNodeLat'][ni]*math.pi/180)*math.cos(parameters_dict['pNodeLat'][nf]*math.pi/180)*math.pow(math.sin((parameters_dict['pNodeLon'][nf]-parameters_dict['pNodeLon'][ni])*math.pi/180/2),2)))

    # thermal and variable units ordered by increasing variable cost
    model.go = parameters_dict['pGenLinearTerm'].sort_values().index

    # determine the initial committed units and their output
    parameters_dict['pInitialOutput'] = pd.Series([0.0]*len(model.gh), model.ps * model.gh)
    parameters_dict['pInitialUC'    ] = pd.Series([0  ]*len(model.gh), model.ps * model.gh)
    for p,sc in model.ps:
        parameters_dict['pSystemOutput'] = 0.0
        for go in model.go:
            n1 = next(iter(model.n))
            if parameters_dict['pSystemOutput'] < sum(parameters_dict['pElectricityDemand'][nd][p,sc,n1] for nd in model.nd):
                if   go in model.re:
                    parameters_dict['pInitialOutput'][p,sc,go] = parameters_dict['pMaxPower'][go][p,sc,n1]
                elif go in model.g:
                    parameters_dict['pInitialOutput'][p,sc,go] = parameters_dict['pMinPower'][go][p,sc,n1]
                parameters_dict['pInitialUC'    ][p,sc,go] = 1
                parameters_dict['pSystemOutput' ]     += parameters_dict['pInitialOutput'][p,sc,go]
            if go in model.hz:
                parameters_dict['pInitialUC'    ][p,sc,go] = 1
            # calculating if the unit was committed before of the time periods or not
            if parameters_dict['pGenUpTime'][go] - parameters_dict['pGenUpTimeZero'][go] > 0:
                parameters_dict['pInitialUC'][p,sc,go] = 1
            if parameters_dict['pGenDownTime'][go] - parameters_dict['pGenDownTimeZero'][go] > 0:
                parameters_dict['pInitialUC'][p,sc,go] = 0

    # load levels multiple of cycles for each ESS/generator
    model.nessc        = [(n,ess) for n,ess in model.n * model.ess if model.n.ord(n) %     parameters_dict['pCycleTimeStep'   ][ess] == 0]
    model.nescc        = [(n,esc) for n,esc in model.n * model.esc if model.n.ord(n) %     parameters_dict['pCycleTimeStep'   ][esc] == 0]
    model.nesso        = [(n,ess) for n,ess in model.n * model.ess if model.n.ord(n) %     parameters_dict['pOutflowsTimeStep'][ess] == 0]
    model.nhhzo        = [(n,hz ) for n,hz  in model.n * model.hz  if model.n.ord(n) %     parameters_dict['pOutflowsTimeStep'][hz ] == 0]   # hydrogen zones with outflows

    # small values are converted to 0
    pGenerationPeak   = parameters_dict['pMaxPower'].sum(axis=1).max()
    pEpsilon_capacity = pGenerationPeak * 1e-5
    pCostPeak = parameters_dict['pGenLinearTerm'].max()
    pEpsilon_cost     = pCostPeak * 1e-3
    pPricePeak        = parameters_dict['pElectricityPrice'].max()         # electricity price
    pEpsilon_price    = pPricePeak * 1e-3

    # values < 1e-5 times the maximum generation are converted to 0 for all elements in parameters_dict
    for idx in ['MinPower', 'MaxPower', 'MinCharge', 'MaxCharge', 'MinStorage', 'MaxStorage', 'MinInflows', 'MaxInflows', 'MinOutflows', 'MaxOutflows', 'MinFuelCost', 'MaxFuelCost', 'MinCO2Cost', 'MaxCO2Cost']:
        parameters_dict[f'p{idx}'] = parameters_dict[f'p{idx}'].where(parameters_dict[f'p{idx}'] > pEpsilon_capacity, other=0.0)

    # for all costs
    for idx in ['LinearTerm', 'ConstantTerm', 'StartUpCost', 'ShutDownCost', 'LinearVarCost', 'CO2EmissionCost']:
        parameters_dict[f'pGen{idx}'] = parameters_dict[f'pGen{idx}'].where(parameters_dict[f'pGen{idx}'] > pEpsilon_cost, other=0.0)

    # for all prices
    for idx in ['ElectricityPrice', 'HydrogenPrice', 'ElectricityCost', 'HydrogenCost']:
        parameters_dict[f'p{idx}'] = parameters_dict[f'p{idx}'].where(parameters_dict[f'p{idx}'] > pEpsilon_price, other=0.0)


    model.Par = parameters_dict

    print('--- Defining the parameters:                                           {} seconds'.format(round(time.time() - start_time)))

    return model

def create_variables(model, optmodel):
    #
    print('-- Defining the variables')
    #%% start time
    StartTime = time.time()

    #%% total variables
    setattr(optmodel, 'vTotalSCost',                        Var(                     within=          Reals,                                                                                                                                                                                                   doc='total system                               cost [MEUR]'))

    setattr(optmodel, 'vTotalMCost',                        Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total variable market                      cost [MEUR]'))
    setattr(optmodel, 'vTotalGCost',                        Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total variable operation                   cost [MEUR]'))
    setattr(optmodel, 'vTotalCCost',                        Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total variable consumption operation       cost [MEUR]'))
    setattr(optmodel, 'vTotalECost',                        Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total system   emission                    cost [MEUR]'))
    setattr(optmodel, 'vTotalRCost',                        Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total system   reliability                 cost [MEUR]'))
    setattr(optmodel, 'vTotalEleTradeCost',                 Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total energy buy                           cost [MEUR]'))
    setattr(optmodel, 'vTotalEleTradeProfit',               Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total energy sell                        profit [MEUR]'))
    setattr(optmodel, 'vTotalHydTradeCost',                 Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total hydrogen buy                         cost [MEUR]'))
    setattr(optmodel, 'vTotalHydTradeProfit',               Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total hydrogen sell                      profit [MEUR]'))

    setattr(optmodel, 'vTotalReserveProfit',                Var(model.psn,   within=           Reals,                                                                                                                                                                                                 doc='total profit for contributing to reserves       [MEUR]'))

    print('--- Defining the total variables:                                      {} seconds'.format(round(time.time() - StartTime)))

    # variables related to the market
    setattr(optmodel, 'vElectricityBuy',                    Var(model.psnnd,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nd:(                                                        0.0, 0.05                                           ),                                                  doc='energy buy                                        [GW]'))
    setattr(optmodel, 'vElectricitySell',                   Var(model.psnnd,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nd:(                                                        0.0, 0.1                                            ),                                                  doc='energy sell                                       [GW]'))
    setattr(optmodel, 'vENS',                               Var(model.psnnd,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nd:(                                                        0.0, model.Par[f'pElectricityDemand'   ][nd][p,sc,n]),                                                  doc='energy not served                                 [GW]'))
    setattr(optmodel, f'vEleTotalOutput',                   Var(model.psng ,  within=NonNegativeReals, bounds=lambda model,p,sc,n,g :(                                                        0.0, model.Par[f'pMaxPower'            ][g ][p,sc,n]),                                                  doc=f'total electricity output of the unit             [GW]'))
    setattr(optmodel, f'vEleTotalOutputDelta',              Var(model.psng ,  within=Reals           , bounds=lambda model,p,sc,n,g :(            -model.Par['pVarPositionGeneration'][g][p,sc,n], model.Par[f'pMaxPower'            ][g ][p,sc,n]-model.Par['pVarPositionGeneration'][g][p,sc,n]),   doc=f'total electricity output of the unit             [GW]'))
    setattr(optmodel, f'vEleTotalOutput2ndBlock',           Var(model.psnnr,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nr:(                                                        0.0, model.Par[f'pMaxPower2ndBlock'    ][nr][p,sc,n]),                                                  doc=f'second block of the unit                         [GW]'))
    setattr(optmodel, f'vEleTotalCharge',                   Var(model.psneh,  within=NonNegativeReals, bounds=lambda model,p,sc,n,h :(                                                        0.0, model.Par[f'pMaxCharge'           ][h ][p,sc,n]),                                                  doc=f'ESS total charge power                           [GW]'))
    setattr(optmodel, f'vEleTotalChargeDelta',              Var(model.psneh,  within=Reals           , bounds=lambda model,p,sc,n,h :(           -model.Par['pVarPositionConsumption'][h][p,sc,n], model.Par[f'pMaxCharge'           ][h ][p,sc,n]-model.Par['pVarPositionConsumption'][h][p,sc,n]),  doc=f'ESS total charge power                           [GW]'))
    setattr(optmodel, f'vEleTotalCharge2ndBlock',           Var(model.psneh,  within=NonNegativeReals, bounds=lambda model,p,sc,n,h :(                                                        0.0, model.Par[f'pMaxCharge2ndBlock'   ][h ][p,sc,n]),                                                  doc=f'ESS       charge power                           [GW]'))
    setattr(optmodel, f'vEleTotalChargeRampPos',            Var(model.psneh,  within=NonNegativeReals, bounds=lambda model,p,sc,n,h :(                                                        0.0, model.Par[f'pMaxCharge'           ][h ][p,sc,n]),                                                  doc=f'ESS       charge power                           [GW]'))
    setattr(optmodel, f'vEleTotalChargeRampNeg',            Var(model.psneh,  within=NonNegativeReals, bounds=lambda model,p,sc,n,h :(                                                        0.0, model.Par[f'pMaxCharge'           ][h ][p,sc,n]),                                                  doc=f'ESS       charge power                           [GW]'))
    setattr(optmodel, f'vEleEnergyInflows',                 Var(model.psnes,  within=NonNegativeReals, bounds=lambda model,p,sc,n,es:(                     model.Par[f'pMinInflows' ][es][p,sc,n], model.Par[f'pMaxInflows'          ][es][p,sc,n]),                                                  doc=f'unscheduled inflows  of all ESS units           [GWh]'))
    setattr(optmodel, f'vEleEnergyOutflows',                Var(model.psnes,  within=NonNegativeReals, bounds=lambda model,p,sc,n,es:(                                                        0.0, model.Par[f'pMaxOutflows'         ][es][p,sc,n]),                                                  doc=f'scheduled   outflows of all ESS units           [GWh]'))
    setattr(optmodel, f'vEleInventory',                     Var(model.psnes,  within=NonNegativeReals, bounds=lambda model,p,sc,n,es:(                     model.Par[f'pMinStorage' ][es][p,sc,n], model.Par[f'pMaxStorage'          ][es][p,sc,n]),                                                  doc=f'ESS inventory                                   [GWh]'))
    setattr(optmodel, f'vEleSpillage',                      Var(model.psnes,  within=NonNegativeReals,                                                                                                                                                                                                doc=f'ESS spillage                                    [GWh]'))

    setattr(optmodel, 'vHydrogenBuy',                       Var(model.psnnd,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nd:(                                                        0.0,                                             1e4),                                                  doc='hydrogen buy        in node                      [tH2]'))
    setattr(optmodel, 'vHydrogenSell',                      Var(model.psnnd,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nd:(                                                        0.0,                                             1e4),                                                  doc='hydrogen sell       in node                      [tH2]'))
    setattr(optmodel, 'vHNS',                               Var(model.psnnd,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nd:(                                                        0.0, model.Par[f'pHydrogenDemand'      ][nd][p,sc,n]),                                                  doc='hydrogen not served in node                      [tH2]'))
    setattr(optmodel, f'vHydTotalDemand',                   Var(model.psnnd,  within=NonNegativeReals,                                                                                                                                                                                                doc=f'total hydrogen demand of the node               [tH2]'))
    setattr(optmodel, f'vHydTotalDemandDelta',              Var(model.psnnd,  within=Reals           , bounds=lambda model,p,sc,n,nd:(            -model.Par['pHydrogenDemand'      ][nd][p,sc,n], model.Par[f'pHydrogenDemand'      ][nd][p,sc,n]),                                                  doc=f'total hydrogen demand of the node               [tH2]'))
    setattr(optmodel, f'vHydTotalOutput',                   Var(model.psnh ,  within=NonNegativeReals, bounds=lambda model,p,sc,n,h :(                                                        0.0, model.Par[f'pMaxPower'            ][h ][p,sc,n]),                                                  doc=f'total hydrogen output of the unit               [tH2]'))
    setattr(optmodel, f'vHydTotalOutputDelta',              Var(model.psnh ,  within=Reals           , bounds=lambda model,p,sc,n,h :(            -model.Par['pVarPositionGeneration'][h][p,sc,n], model.Par[f'pMaxPower'            ][h ][p,sc,n]-model.Par['pVarPositionGeneration'][h][p,sc,n]),   doc=f'total hydrogen output of the unit               [tH2]'))
    setattr(optmodel, f'vHydTotalOutput2ndBlock',           Var(model.psnh ,  within=NonNegativeReals, bounds=lambda model,p,sc,n,h :(                                                        0.0, model.Par[f'pMaxPower2ndBlock'    ][h ][p,sc,n]),                                                  doc=f'second block of the unit                        [tH2]'))
    setattr(optmodel, f'vHydTotalCharge',                   Var(model.psnhe,  within=NonNegativeReals, bounds=lambda model,p,sc,n,he:(                                                        0.0, model.Par[f'pMaxCharge'           ][he][p,sc,n]),                                                  doc=f'total hydrogen output of the unit               [tH2]'))
    setattr(optmodel, f'vHydTotalChargeDelta',              Var(model.psnhe,  within=Reals           , bounds=lambda model,p,sc,n,he:(          -model.Par['pVarPositionConsumption'][he][p,sc,n], model.Par[f'pMaxCharge'           ][he][p,sc,n]-model.Par['pVarPositionConsumption'][he][p,sc,n]), doc=f'total hydrogen output of the unit               [tH2]'))
    # setattr(optmodel, f'vHydTotalChargeRampPos',            Var(model.psnhe,  within=NonNegativeReals, bounds=lambda model,p,sc,n,he:(                                                        0.0, model.Par[f'pMaxCharge'           ][he][p,sc,n]),                                                  doc=f'total hydrogen output of the unit               [tH2]'))
    # setattr(optmodel, f'vHydTotalChargeRampNeg',            Var(model.psnhe,  within=NonNegativeReals, bounds=lambda model,p,sc,n,he:(                                                        0.0, model.Par[f'pMaxCharge'           ][he][p,sc,n]),                                                  doc=f'total hydrogen output of the unit               [tH2]'))
    setattr(optmodel, f'vHydTotalCharge2ndBlock',           Var(model.psnhe,  within=NonNegativeReals, bounds=lambda model,p,sc,n,he:(                                                        0.0, model.Par[f'pMaxCharge2ndBlock'   ][he][p,sc,n]),                                                  doc=f'second block of the unit                        [tH2]'))
    setattr(optmodel, f'vHydEnergyInflows',                 Var(model.psnhs,  within=NonNegativeReals, bounds=lambda model,p,sc,n,hs:(                     model.Par[f'pMinInflows' ][hs][p,sc,n], model.Par[f'pMaxInflows'          ][hs][p,sc,n]),                                                  doc=f'unscheduled inflows  of all ESS units           [tH2]'))
    setattr(optmodel, f'vHydEnergyOutflows',                Var(model.psnhs,  within=NonNegativeReals, bounds=lambda model,p,sc,n,hs:(                                                        0.0, model.Par[f'pMaxPower'            ][hs][p,sc,n]),                                                  doc=f'scheduled   outflows of all ESS units           [tH2]'))
    setattr(optmodel, f'vHydInventory',                     Var(model.psnhs,  within=NonNegativeReals, bounds=lambda model,p,sc,n,hs:(                     model.Par[f'pMinStorage' ][hs][p,sc,n], model.Par[f'pMaxStorage'          ][hs][p,sc,n]),                                                  doc=f'ESS inventory                                   [tH2]'))
    setattr(optmodel, f'vHydSpillage',                      Var(model.psnhs,  within=NonNegativeReals,                                                                                                                                                                                                doc=f'ESS spillage                                    [tH2]'))
    setattr(optmodel, f'vHydCompressorConsumption',         Var(model.psnhs,  within=NonNegativeReals, bounds=lambda model,p,sc,n,hs:(                                                        0.0, model.Par[f'pGenMaxCompressorConsumption'][hs] ),                                                  doc=f'HESS compressor consumption                      [GW]'))
    setattr(optmodel, f'vHydStandByConsumption',            Var(model.psnh ,  within=NonNegativeReals, bounds=lambda model,p,sc,n,h :(                                                        0.0, model.Par[f'pGenStandByPower'     ][h] ),                                                          doc=f'HESS standby    consumption                      [GW]'))

    if model.Par['pOptIndBinSingleNode'] == 0:
        setattr(optmodel, f'vEleNetLosses',                 Var(model.psnell,  within=NonNegativeReals,                                                                                                                                                                                               doc=f'electricity losses                               [GW]'))
        setattr(optmodel, f'vHydNetLosses',                 Var(model.psnell,  within=NonNegativeReals,                                                                                                                                                                                               doc=f'hydrogen    losses                              [tH2]'))
        setattr(optmodel, f'vEleNetFlow',                   Var(model.psnela,  within=           Reals, bounds=lambda model,p,sc,n,ni,nf,cc:(              -model.Par['pEleNetTTCBck' ][ni,nf,cc], model.Par['pEleNetTTC'            ][ni,nf,cc]),                                                    doc=f'electricity flow                                 [GW]'))
        setattr(optmodel, f'vHydNetFlow',                   Var(model.psnhpa,  within=           Reals, bounds=lambda model,p,sc,n,ni,nf,cc:(              -model.Par['pHydNetTTCBck' ][ni,nf,cc], model.Par['pHydNetTTC'            ][ni,nf,cc]),                                                    doc=f'hydrogen    flow                                [tH2]'))
    else:
        setattr(optmodel, f'vEleNetLosses',                 Var(model.psnell,  within=NonNegativeReals,                                                                                                                                                                                               doc=f'electricity losses                               [GW]'))
        setattr(optmodel, f'vHydNetLosses',                 Var(model.psnell,  within=NonNegativeReals,                                                                                                                                                                                               doc=f'hydrogen    losses                              [tH2]'))
        setattr(optmodel, f'vEleNetFlow',                   Var(model.psnela,  within=           Reals,                                                                                                                                                                                               doc=f'electricity flow                                 [GW]'))
        setattr(optmodel, f'vHydNetFlow',                   Var(model.psnhpa,  within=           Reals,                                                                                                                                                                                               doc=f'hydrogen    flow                                [tH2]'))
    setattr(optmodel, f'vEleNetTheta',                      Var(model.psnnd ,  within=           Reals,                                                                                                                                                                                               doc=f'electricity voltage angle                        [GW]'))

    print('--- Defining the DA variables:                                         {} seconds'.format(round(time.time() - StartTime)))

    for idx in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
        setattr(optmodel, f'vEleReserveProd_{idx}',         Var(model.psnnr ,  within=NonNegativeReals, bounds=lambda model,p,sc,n,nr:(                                                       0.0, model.Par[f'pMaxPower2ndBlock'    ][nr][p,sc,n]),                                                  doc=f'operating reserve {idx}                          [GW]'))
        setattr(optmodel, f'vEleReserveCons_{idx}',         Var(model.psneh ,  within=NonNegativeReals, bounds=lambda model,p,sc,n,eh:(                                                       0.0, model.Par[f'pMaxCharge2ndBlock'   ][eh][p,sc,n]),                                                  doc=f'ESS operating reserve {idx}                      [GW]'))

    print('--- Defining the SR and TR variables:                                  {} seconds'.format(round(time.time() - StartTime)))

    # binary variables
    if model.Par['pOptIndBinGenOperat'] == 0:
        setattr(optmodel, 'vGenMaxCommitment',              Var(model.psnnr ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the commitment of the unit       '))
        setattr(optmodel, 'vGenCommitment',                 Var(model.psnnr ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the commitment of the unit       '))
        setattr(optmodel, 'vGenStartUp',                    Var(model.psnnr ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the start-up   of the unit       '))
        setattr(optmodel, 'vGenShutDown',                   Var(model.psnnr ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the shut-down  of the unit       '))
        setattr(optmodel, 'vHydCommitment',                 Var(model.psnh  ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the commitment of the unit       '))
        setattr(optmodel, 'vHydStartUp',                    Var(model.psnh  ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the start-up   of the unit       '))
        setattr(optmodel, 'vHydShutDown',                   Var(model.psnh  ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the shut-down  of the unit       '))
        setattr(optmodel, 'vEleStorOperat',                 Var(model.psnes ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable indicating charging or discharging   '))
        setattr(optmodel, 'vHydStorOperat',                 Var(model.psnhs ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable indicating charging or discharging   '))
        setattr(optmodel, 'vHydCompressorOperat',           Var(model.psnhs ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable indicating the operation of the compressor'))
        setattr(optmodel, 'vHydStandBy',                    Var(model.psnh  ,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable indicating the stand-by mode of the unit'))
    else:
        setattr(optmodel, 'vGenMaxCommitment',              Var(model.psnnr ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the commitment of the unit       '))
        setattr(optmodel, 'vGenCommitment',                 Var(model.psnnr ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the commitment of the unit       '))
        setattr(optmodel, 'vGenStartUp',                    Var(model.psnnr ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the start-up   of the unit       '))
        setattr(optmodel, 'vGenShutDown',                   Var(model.psnnr ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the shut-down  of the unit       '))
        setattr(optmodel, 'vHydCommitment',                 Var(model.psnh  ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the commitment of the unit       '))
        setattr(optmodel, 'vHydStartUp',                    Var(model.psnh  ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the start-up   of the unit       '))
        setattr(optmodel, 'vHydShutDown',                   Var(model.psnh  ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the shut-down  of the unit       '))
        setattr(optmodel, 'vEleStorOperat',                 Var(model.psnes ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable indicating charging or discharging   '))
        setattr(optmodel, 'vHydStorOperat',                 Var(model.psnhs ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable indicating charging or discharging   '))
        setattr(optmodel, 'vHydCompressorOperat',           Var(model.psnhs ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable indicating the operation of the compressor'))
        setattr(optmodel, 'vHydStandBy',                    Var(model.psnh  ,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable indicating the stand-by mode of the unit'))

    if model.Par['pOptIndBinNetOperat'] == 0:
        setattr(optmodel, 'vEleNetCommit',                  Var(model.psnela,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the flow of the line             '))
        setattr(optmodel, 'vHydNetCommit',                  Var(model.psnhpa,  within=UnitInterval, initialize=0,                                                                                                                                                                                     doc= 'binary variable for the flow of the line             '))
    else:
        setattr(optmodel, 'vEleNetCommit',                  Var(model.psnela,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the flow of the line             '))
        setattr(optmodel, 'vHydNetCommit',                  Var(model.psnhpa,  within=Binary,       initialize=0.0,                                                                                                                                                                                   doc= 'binary variable for the flow of the line             '))

    print('--- Defining the binary variables:                                     {} seconds'.format(round(time.time() - StartTime)))

    EnergyPrefix = {}
    for g in model.g:
        EnergyPrefix[g] = 'Ele'
    for h in model.h:
        EnergyPrefix[h] = 'Hyd'
    model.EnergyPrefix = EnergyPrefix

    #%% fixing variables
    nFixedVariables = 0.0

    # assign the minimum power for the RES units
    for idx in model.psnre:
        optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalOutput')[idx].setlb(model.Par[f'pMinPower'][idx[-1]][idx[:(len(idx)-1)]])

    # relax binary condition in unit generation, startup and shutdown decisions
    for idx in model.psnnr:
        if model.Par[f'pGenBinaryCommitment'][idx[-1]] == 0:
            optmodel.__getattribute__(f'vGenCommitment')[idx].domain = UnitInterval
            optmodel.__getattribute__(f'vGenStartUp'   )[idx].domain = UnitInterval
            optmodel.__getattribute__(f'vGenShutDown'  )[idx].domain = UnitInterval

    for idx in model.psnhz:
        if model.Par[f'pGenBinaryCommitment'][idx[-1]] == 0:
            optmodel.__getattribute__(f'vHydCommitment')[idx].domain = UnitInterval
            optmodel.__getattribute__(f'vHydStartUp'   )[idx].domain = UnitInterval
            optmodel.__getattribute__(f'vHydShutDown'  )[idx].domain = UnitInterval


    # existing electrical circuits are always committed if no switching decision is modeled
    for idx in model.psnele:
        if model.Par[f'pEleNetSwitching'][idx[-3:]] == 0:
            optmodel.__getattribute__(f'vEleNetCommit')[idx].fix(1)
            nFixedVariables += 1

    # existing hydrogen pipelines are always committed if no switching decision is modeled
    for idx in model.psnhpe:
        if model.Par[f'pHydNetSwitching'][idx[-3:]] == 0:
            optmodel.__getattribute__(f'vHydNetCommit')[idx].fix(1)
            nFixedVariables += 1

    # if min and max power coincide there are neither second block, nor operating reserve
    for idx in model.psnnr:
        if model.Par[f'pMaxPower2ndBlock'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalOutput2ndBlock')[idx].fix(0.0)
            nFixedVariables += 1

    for idx in model.psnnr:
        if model.Par['pGenNoOperatingReserve'][idx[-1]] != 0.0:
            for idx2 in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
                # print(f'vEleReserveProd_{idx2}')
                optmodel.__getattribute__(f'vEleReserveProd_{idx2}')[idx].fix(0.0)
                optmodel.__getattribute__(f'vEleReserveCons_{idx2}')[idx].fix(0.0)
                nFixedVariables += 2

    for idx in model.psneh:
        if model.Par['pGenNoOperatingReserve'][idx[-1]] != 0.0:
            for idx2 in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
                optmodel.__getattribute__(f'vEleReserveCons_{idx2}')[idx].fix(0.0)
                nFixedVariables += 1

    # if min and max outflows coincide there are neither second block, nor operating reserve
    for idx in  model.psnhz:
        if model.Par[f'pMaxPower2ndBlock'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'vHydTotalOutput2ndBlock')[idx].fix(0.0)
            nFixedVariables += 1

    # ESS with no charge capacity or not storage capacity can't charge
    for idx in model.psness:
        if model.Par[f'pMaxCharge'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalCharge')[idx].fix(0.0)
            nFixedVariables += 1
        # ESS with no charge capacity and no inflows can't produce
        if model.Par[f'pMaxCharge'][idx[-1]][idx[:(len(idx)-1)]] == 0.0 and sum(model.Par[f'pMaxInflows'][idx[-1]][idx[:(len(idx)-2)]+(n2,)] for n2 in model.n2) == 0.0:
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalOutput')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalOutput2ndBlock')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Spillage')[idx].fix(0.0)
            nFixedVariables += 3
        if model.Par[f'pMaxCharge2ndBlock'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalCharge2ndBlock')[idx].fix(0.0)
            nFixedVariables += 1
        if model.Par[f'pMaxStorage'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Inventory')[idx].fix(0.0)
            nFixedVariables += 1
        # fixing the ESS inventory at the last load level of the stage for every period and scenario if between storage limits in the DA market
        if len(model.n):
            if model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]] >= model.Par[f'pMinStorage'][idx[-1]][idx[:(len(idx)-2)]+(model.n.last(),)] and model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]] <= model.Par[f'pMaxStorage'][idx[-1]][idx[:(len(idx)-2)]+(model.n.last(),)]:
                optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Inventory')[idx[:(len(idx)-2)]+(model.n.last(),)+(idx[-1],)].fix(model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]])
                nFixedVariables += 1
        # # fixing the ESS inventory at the end of the following pCycleTimeStep (daily, weekly, monthly), i.e., for daily ESS is fixed at the end of the week, for weekly/monthly ESS is fixed at the end of the year
        #     if model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]] >= model.Par[f'pMinStorage'][idx[-1]][idx[:(len(idx)-1)]]                   and model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]] <= model.Par[f'pMaxStorage'][idx[-1]][idx[:(len(idx)-1)]]:
        #         if model.Par['pGenStorageType'][idx[-1]] == 'Hourly' and model.n.ord(idx[-2]) % int(24/model.Par['pParTimeStep']) == 0:
        #             optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Inventory')[idx].fix(model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]])
        #             nFixedVariables += 1
        #         if model.Par['pGenStorageType'][idx[-1]] == 'Daily' and model.n.ord(idx[-2]) % int(168/model.Par['pParTimeStep']) == 0:
        #             optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Inventory')[idx].fix(model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]])
        #             nFixedVariables += 1
        #         if model.Par['pGenStorageType'][idx[-1]] == 'Weekly' and model.n.ord(idx[-2]) % int(8736/model.Par['pParTimeStep']) == 0:
        #             optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Inventory')[idx].fix(model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]])
        #             nFixedVariables += 1
        #         if model.Par['pGenStorageType'][idx[-1]] == 'Monthly' and model.n.ord(idx[-2]) % int(8736/model.Par['pParTimeStep']) == 0:
        #             optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Inventory')[idx].fix(model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]])
        #             nFixedVariables += 1

    # for idx in ['Up_SR', 'Down_SR', 'Up_TR', 'Down_TR']:
    #     for idx2 in model.psnes:
    #         if model.Par['pGenNoOperatingReserve'][idx2[-1]] != 0.0:
    #             optmodel.__getattribute__(f'vEleReserveCons_{idx}')[idx2].fix(0.0)
    #             nFixedVariables += 1
    #         # if model.Par[f'pRMOperatingReserve{idx[:2]}'][p, n] == 0.0:
    #         #     optmodel.__getattribute__(f'vESSReserve{idx}')[p, n, es].fix(0.0)
    #         #     nFixedVariables += 1

    # # if no operating reserve is required no variables are needed
    # for idx in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
    #     for p,n,nr in model.pnnr:
    #         if model.Par[f'pRMOperatingReserve{idx[:2]}'][p,sc,n] == 0.0:
    #             optmodel.__getattribute__(f'vEleReserve{idx}')[p,sc,n,nr].fix(0.0)
    #             nFixedVariables += 1

    # if there are no energy outflows no variable is needed
    iset = model.psn
    for es in model.es:
        if sum(model.Par[f'pMaxOutflows'][es][idx] for idx in iset) == 0.0:
            for idx in iset:
                optmodel.__getattribute__(f'v{model.EnergyPrefix[es]}EnergyOutflows')[idx+(es,)].fix(0.0)
                nFixedVariables += 1

    # fixing the voltage angle of the reference node for each scenario, period, and load level
    if model.Par['pOptIndBinSingleNode'] == 0:
        for p,sc,n in model.psn:
            optmodel.__getattribute__('vEleNetTheta')[p,sc,n,model.ndrf.first()].fix(0.0)
            nFixedVariables += 1

    # fixing the ENS in nodes with no electricity and hydrogen demand in market
    for idx in model.psnnd:
        if model.Par[f'pElectricityDemand'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'vENS')[idx].fix(0.0)
            nFixedVariables += 1
        if model.Par[f'pHydrogenDemand'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'vHNS')[idx].fix(0.0)
            nFixedVariables += 1

    # remove power plants and lines not installed in this period
    for idx in model.psng:
        if idx[-1] not in model.gc and (model.Par[f'pGenInitialPeriod'][idx[-1]] > model.Par['pParEconomicBaseYear'] or model.Par[f'pGenFinalPeriod'][idx[-1]] < model.Par['pParEconomicBaseYear']):
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalOutput')[idx].fix(0.0)
            nFixedVariables += 1

    for idx in model.psnnr:
        if idx[-1] not in model.gc and (model.Par[f'pGenInitialPeriod'][idx[-1]] > model.Par['pParEconomicBaseYear'] or model.Par[f'pGenFinalPeriod'][idx[-1]] < model.Par['pParEconomicBaseYear']):
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalOutput2ndBlock')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}GenCommitment')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}GenStartUp')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}GenShutDown')[idx].fix(0.0)
            nFixedVariables += 4

    for idx1 in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
        for idx2 in model.psnnr:
            if idx2[-1] not in model.gc and (model.Par['pGenInitialPeriod'][idx2[-1]] > model.Par['pParEconomicBaseYear'] or model.Par['pGenFinalPeriod'][idx2[-1]] < model.Par['pParEconomicBaseYear']):
                optmodel.__getattribute__(f'vEleReserveProd_{idx1}_')[idx2].fix(0.0)
                nFixedVariables += 1
            # if nr in model.es:
            #     optmodel.__getattribute__(f'vEleReserveProd_{idx}')[p,sc,n,nr].fix(0.0)
            #     nFixedVariables += 1

    for idx in model.psnes:
        if idx[-1] not in model.gc and (model.Par[f'pGenInitialPeriod'][idx[-1]] > model.Par['pParEconomicBaseYear'] or model.Par[f'pGenFinalPeriod'][idx[-1]] < model.Par['pParEconomicBaseYear']):
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalCharge')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}TotalCharge2ndBlock')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Inventory')[idx].fix(0.0)
            optmodel.__getattribute__(f'v{model.EnergyPrefix[idx[-1]]}Spillage')[idx].fix(0.0)
            nFixedVariables += 4

    for idx1 in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
        for idx2 in model.psneh:
            if idx not in model.gc and (model.Par['pGenInitialPeriod'][idx2[-1]] > model.Par['pParEconomicBaseYear'] or model.Par['pGenFinalPeriod'][idx2[-1]] < model.Par['pParEconomicBaseYear']):
                optmodel.__getattribute__(f'vEleReserveCons_{idx1}')[idx2].fix(0.0)
                nFixedVariables += 1

    for idx in model.psnela:
        if idx[-3:] not in model.elc and (model.Par[f'pEleNetInitialPeriod'][idx[-3:]] > model.Par['pParEconomicBaseYear'] or model.Par[f'pEleNetFinalPeriod'][idx[-3:]] < model.Par['pParEconomicBaseYear']):
            optmodel.__getattribute__(f'vEleNetFlow')[idx].fix(0.0)
            optmodel.__getattribute__(f'vEleNetLosses')[idx].fix(0.0)
            nFixedVariables += 2

    for idx in model.psnhpa:
        if idx[-3:] not in model.elc and (model.Par[f'pHydNetInitialPeriod'][idx[-3:]] > model.Par['pParEconomicBaseYear'] or model.Par[f'pHydNetFinalPeriod'][idx[-3:]] < model.Par['pParEconomicBaseYear']):
            optmodel.__getattribute__(f'vHydNetFlow')[idx].fix(0.0)
            nFixedVariables += 1

    for idx in model.psnnd:
        if model.Par[f'pElectricityCost'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'vElectricityBuy')[idx].fix(0.0)
            nFixedVariables += 1
        if model.Par[f'pHydrogenCost'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'vHydrogenBuy')[idx].fix(0.0)
            nFixedVariables += 1
        if model.Par[f'pElectricityPrice'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'vElectricitySell')[idx].fix(0.0)
            nFixedVariables += 1
        if model.Par[f'pHydrogenPrice'][idx[-1]][idx[:(len(idx)-1)]] == 0.0:
            optmodel.__getattribute__(f'vHydrogenSell')[idx].fix(0.0)
            nFixedVariables += 1

    for idx1 in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
        for idx2 in model.psnnr:
            if model.Par['pGenNoOperatingReserve'][idx2[-1]] != 0.0 and model.Par[f'pOperatingReserveRequire_{idx1}'][idx2[:-1]] == 0.0:
                optmodel.__getattribute__(f'vEleReserveProd_{idx1}')[idx2].fix(0.0)

    for idx1 in ['Up_SR', 'Down_SR','Up_TR', 'Down_TR']:
        for idx2 in model.psneh:
            if model.Par['pGenNoOperatingReserve'][idx2[-1]] != 0.0 and model.Par[f'pOperatingReserveRequire_{idx1}'][idx2[:-1]] == 0.0:
                optmodel.__getattribute__(f'vEleReserveCons_{idx1}')[idx2].fix(0.0)
                nFixedVariables += 2

    # fixing the initial committed electricity units based on the UpTimeZero and DownTimeZero
    for p,sc,n,t in model.psnt:
        if model.Par['pGenUpTimeZero'  ][t] > 0 and model.n.ord(n) <= max(0,min(model.n.ord(n),(model.Par['pGenUpTime'][t]-model.Par['pGenUpTimeZero'][t]))):
            optmodel.__getattribute__(f'vGenCommitment')[p,sc,n,t].fix(1)
            nFixedVariables += 1
        if model.Par['pGenDownTimeZero'][t] > 0 and model.n.ord(n) <= max(0,min(model.n.ord(n),(model.Par['pGenDownTime'][t]-model.Par['pGenDownTimeZero'][t]))):
            optmodel.__getattribute__(f'vGenCommitment')[p,sc,n,t].fix(0)
            nFixedVariables += 1
    # fixing the initial committed hydrogen units based on the UpTimeZero and DownTimeZero
    for p,sc,n,hz in model.psnhz:
        if model.Par['pGenUpTimeZero'  ][hz] > 0 and model.n.ord(n) <= max(0,min(model.n.ord(n),(model.Par['pGenUpTime'][hz]-model.Par['pGenUpTimeZero'][hz]))):
            optmodel.__getattribute__(f'vHydCommitment')[p,sc,n,hz].fix(1)
            nFixedVariables += 1
        if model.Par['pGenDownTimeZero'][hz] > 0 and model.n.ord(n) <= max(0,min(model.n.ord(n),(model.Par['pGenDownTime'][hz]-model.Par['pGenDownTimeZero'][hz]))):
            optmodel.__getattribute__(f'vHydCommitment')[p,sc,n,hz].fix(0)
            nFixedVariables += 1

    # fixing electricity buys in hours when electricity cost is equal o greater than 1000
    for idx in model.psnnd:
        if model.Par[f'pElectricityCost'][idx[-1]][idx[:(len(idx)-1)]] >= 1000.0:
            optmodel.__getattribute__(f'vElectricityBuy')[idx].fix(0.0)
            nFixedVariables += 1

    # fixing the vHydTotalDemandDelta variable in nodes with no hydrogen demand in market
    for nd in model.nd:
        if sum(model.Par[f'pHydrogenDemand'][nd][idx] for idx in model.psn) == 0.0:
            for idx in model.psn:
                optmodel.__getattribute__(f'vHydTotalDemandDelta')[idx+(nd,)].fix(0.0)
                nFixedVariables += 1

    # incoming and outgoing lines (lin) (lout)
    lin   = defaultdict(list)
    lout  = defaultdict(list)
    for ni,nf,cc in model.ela:
        lin  [nf].append((ni,cc))
        lout [ni].append((nf,cc))

    hin   = defaultdict(list)
    hout  = defaultdict(list)
    for ni,nf,cc in model.hpa:
        hin  [nf].append((ni,cc))
        hout [ni].append((nf,cc))

    # setting up the lower and upper bounds for the vHydTotalDemandDelta variable
    for nd in model.nd:
        if sum(model.Par[f'pHydrogenDemand'][nd][idx] for idx in model.psn) != 0.0:
            for idx in model.psn:
                if model.Par[f'pHydrogenDemand'][nd][idx] == 0.0:
                    optmodel.__getattribute__(f'vHydTotalDemandDelta')[idx+(nd,)].setlb(0.0)
                    optmodel.__getattribute__(f'vHydTotalDemandDelta')[idx+(nd,)].setub(max(0.0, sum(model.Par[f'pGenMaximumPower'][hz] for hz in model.hz for cc in model.cc if (model.Par[f'pGenNode'][hz],cc) in hin[nd]), sum(model.Par[f'pGenMaximumPower'][hs] for hs in model.hs for cc in model.cc if (model.Par[f'pGenNode'][hs],cc) in hin[nd])))
                else:
                    optmodel.__getattribute__(f'vHydTotalDemandDelta')[idx+(nd,)].fix(0.0)

    # detecting infeasibility: total min ESS output greater than total inflows, total max ESS charge lower than total outflows
    for es in model.es:
        if sum(model.Par[f'pMinPower'][es][idx] for idx in iset) - sum(model.Par[f'pMaxInflows'][es][idx] for idx in model.psn) > 0.0:
            print('### Total minimum output greater than total inflows for ESS unit ', es)
            assert(0==1)
        if sum(model.Par[f'pMaxCharge'][es][idx] for idx in iset) - sum(model.Par[f'pMaxOutflows'][es][idx] for idx in model.psn) < 0.0:
            print('### Total maximum charge lower than total outflows for ESS unit ', es)
            assert(0==1)

    # detecting inventory infeasibility
    for idx in model.psnes:
        if model.Par[f'pMaxCharge'][idx[-1]][idx[:(len(idx)-1)]] + model.Par[f'pMaxPower'][idx[-1]][idx[:(len(idx)-1)]] > 0.0:
            if model.n.ord(idx[-2]) == model.Par['pCycleTimeStep'][idx[-1]]:
                if model.Par[f'pInitialInventory'][idx[-1]][idx[:(len(idx)-1)]] + sum(model.Par['pDuration'][n2] * (model.Par[f'pMaxInflows'][idx[-1]][idx[:(len(idx)-2)]+(n2,)] - model.Par[f'pMinPower'][idx[-1]][idx[:(len(idx)-2)]+(n2,)] + model.Par['pGenEfficiency'][idx[-1]] * model.Par[f'pMaxCharge'][idx[-1]][idx[:(len(idx)-2)]+(n2,)]) for n2 in list(model.n2)[model.n.ord(idx[-2]) - model.Par['pCycleTimeStep'][idx[-1]]:model.n.ord(idx[-2])]) < model.Par[f'pMinStorage'][idx[-1]][idx[:(len(idx)-1)]]:
                    print('### Inventory equation violation ', idx)
                    assert(0==1)
            elif model.n.ord(idx[-2]) > model.Par['pCycleTimeStep'][idx[-1]]:
                if model.Par[f'pMaxStorage'][idx[-1]][idx[:(len(idx)-1)]] + sum(model.Par['pDuration'][n2] * (model.Par[f'pMaxInflows'][idx[-1]][idx[:(len(idx)-2)]+(n2,)] - model.Par[f'pMinPower'][idx[-1]][idx[:(len(idx)-2)]+(n2,)] + model.Par['pGenEfficiency'][idx[-1]] * model.Par[f'pMaxCharge'][idx[-1]][idx[:(len(idx)-2)]+(n2,)]) for n2 in list(model.n2)[model.n.ord(idx[-2]) - model.Par['pCycleTimeStep'][idx[-1]]:model.n.ord(idx[-2])]) < model.Par[f'pMinStorage'][idx[-1]][idx[:(len(idx)-1)]]:
                    print('### Inventory equation violation ', idx)
                    assert(0==1)

    # fixing vGenMaxCommitment variables which are not the one at the beginning of the day
    for idx in model.psnnr:
        if model.Par['pGenMaxCommitment'][idx[-1]] != 0.0 and model.n.ord(idx[-2]) % 24 != 0:
            optmodel.__getattribute__(f'vGenMaxCommitment')[idx].fix(0.0)
            nFixedVariables += 1
    # Fixing the stand-by mode of the hydrogen units
    for idx in model.psnhz:
        if model.Par['pGenStandByStatus'][idx[-1]] == 0.0:
            optmodel.__getattribute__(f'vHydStandByConsumption')[idx].fix(0.0)
            optmodel.__getattribute__(f'vHydStandBy')[idx].fix(0.0)
            nFixedVariables += 2
    # Fixing the shut down in the first 8 hours of every day
    for idx in model.psnnr:
        if model.Par['pGenBinaryCommitment'][idx[-1]] != 0 and model.n.ord(idx[-2]) % 24 < 10 and idx[-1] in model.hz:
            optmodel.__getattribute__(f'vGenShutDown')[idx].fix(0.0)
            optmodel.__getattribute__(f'vHydCommitment')[idx].fix(1.0)
            nFixedVariables += 2
        # if model.Par['pGenBinaryCommitment'][idx[-1]] != 0 and model.n.ord(idx[-2]) % 24 < 10 and model.n.ord(idx[-2]) % 24 > 7 and idx[-1] in model.hz:
        #     optmodel.__getattribute__(f'vHydStandBy')[idx].fix(1.0)
        #     nFixedVariables += 1

    model.nFixedVariables = Param(initialize=round(nFixedVariables), within=NonNegativeIntegers, doc='Number of fixed variables')

    print('--- Fixing variables:                                                  {} seconds'.format(round(time.time() - StartTime)))

    return model

def create_objective_function(model, optmodel):
    # this function declares constraints
    StartTime = time.time() # to compute elapsed time

    print('-- Declaring objective function')

    # tolerance to consider avoid division by 0
    pEpsilon = 1e-6

    # defining the objective function
    def eTotalSCost(optmodel):
        return optmodel.vTotalSCost
    optmodel.__setattr__('eTotalSCost', Objective(rule=eTotalSCost, sense=minimize, doc='Total system cost [MEUR]'))

    def eTotalTCost(optmodel):
        return optmodel.vTotalSCost == sum(optmodel.Par['pDiscountFactor'][idx[0]] * (optmodel.__getattribute__(f'vTotalMCost')[idx] + optmodel.__getattribute__(f'vTotalGCost')[idx] + optmodel.__getattribute__(f'vTotalECost')[idx] + optmodel.__getattribute__(f'vTotalCCost')[idx] - optmodel.__getattribute__(f'vTotalRCost')[idx]) for idx in model.psn)
    optmodel.__setattr__('eTotalTCost', Constraint(rule=eTotalTCost, doc='Total system cost [MEUR]'))

    print('--- Declaring the totals components of the ObjFunc:                    {} seconds'.format(round(time.time() - StartTime)))

    return model

def create_objective_function_market(model, optmodel):
    #
    StartTime = time.time() # to compute elapsed time
    # Market variable cost [M€]
    def eTotalMCost(optmodel, p,sc,n):
        return (optmodel.vTotalMCost[p,sc,n] ==   optmodel.vTotalEleTradeCost[p,sc,n] - optmodel.vTotalEleTradeProfit[p,sc,n] + optmodel.vTotalHydTradeCost[p,sc,n] - optmodel.vTotalHydTradeProfit[p,sc,n]
                                                + sum(model.Par['pDuration'][n] * (model.Par['pParENSCost'] * optmodel.vENS[p,sc,n,nd] + model.Par['pParHNSCost'] * optmodel.vHNS[p,sc,n,nd]) for nd in model.nd))
    optmodel.__setattr__('eTotalMCost', Constraint(optmodel.psn, rule=eTotalMCost, doc='Total market cost in the DA market [MEUR]'))

    def eTotalEleTradeCost(optmodel, p,sc,n):
        return optmodel.vTotalEleTradeCost[p,sc,n] == sum(model.Par['pDuration'][n] * (model.Par['pElectricityCost'][nd][p,sc,n] * optmodel.vElectricityBuy[p,sc,n,nd]) for nd in model.nd)
    optmodel.__setattr__('eTotalEleTradeCost', Constraint(optmodel.psn, rule=eTotalEleTradeCost, doc='Total electricity trade cost in the DA market [MEUR]'))

    def eTotalEleTradeProfit(optmodel, p,sc,n):
        return optmodel.vTotalEleTradeProfit[p,sc,n] == sum(model.Par['pDuration'][n] * (model.Par['pElectricityPrice'][nd][p,sc,n] * optmodel.vElectricitySell[p,sc,n,nd]) for nd in model.nd)
    optmodel.__setattr__('eTotalEleTradeProfit', Constraint(optmodel.psn, rule=eTotalEleTradeProfit, doc='Total electricity trade profit in the DA market [MEUR]'))

    def eTotalHydTradeCost(optmodel, p,sc,n):
        return optmodel.vTotalHydTradeCost[p,sc,n] == sum(model.Par['pDuration'][n] * (model.Par['pHydrogenCost'][nd][p,sc,n] * optmodel.vHydrogenBuy[p,sc,n,nd]) for nd in model.nd)
    optmodel.__setattr__('eTotalHydTradeCost', Constraint(optmodel.psn, rule=eTotalHydTradeCost, doc='Total hydrogen trade cost in the DA market [MEUR]'))

    def eTotalHydTradeProfit(optmodel, p,sc,n):
        return optmodel.vTotalHydTradeProfit[p,sc,n] == sum(model.Par['pDuration'][n] * (model.Par['pHydrogenPrice'][nd][p,sc,n] * optmodel.vHydrogenSell[p,sc,n,nd]) for nd in model.nd)
    optmodel.__setattr__('eTotalHydTradeProfit', Constraint(optmodel.psn, rule=eTotalHydTradeProfit, doc='Total hydrogen trade profit in the DA market [MEUR]'))

    # Generation operation cost in DA [M€]
    def eTotalGCost(optmodel, p,sc,n):
        return optmodel.vTotalGCost[p,sc,n] == (sum(model.Par['pDuration'][n] * model.Par['pGenLinearVarCost'  ][g ] *       optmodel.vEleTotalOutput       [p,sc,n,g ] for g  in model.g ) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenConstantVarCost'][nr] *       optmodel.vGenMaxCommitment     [p,sc,n,nr] for nr in model.nr) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenStartUpCost'    ][nr] *       optmodel.vGenStartUp           [p,sc,n,nr] for nr in model.nr) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenShutDownCost'   ][nr] *       optmodel.vGenShutDown          [p,sc,n,nr] for nr in model.nr) -
                                                # sum(model.Par['pDuration'][n] * 1e-5                                 *       optmodel.vHydInventory         [p,sc,n,hs] for hs in model.hs) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenLinearVarCost'  ][hz] *       optmodel.vEleTotalCharge       [p,sc,n,hz] for hz in model.hz) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenConstantVarCost'][hz] *      (optmodel.vHydCommitment        [p,sc,n,hz] - optmodel.vHydStandBy[p,sc,n,hz]) for hz in model.hz) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenStartUpCost'    ][hz] * 1e3 * optmodel.vEleTotalChargeRampPos[p,sc,n,hz] for hz in model.hz) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenShutDownCost'   ][hz] *       optmodel.vHydShutDown          [p,sc,n,hz] for hz in model.hz) +
                                                sum(model.Par['pDuration'][n] * model.Par['pGenOMVariableCost' ][g ] *       optmodel.vEleTotalOutput       [p,sc,n,g ] for g  in model.g ))
    optmodel.__setattr__('eTotalGCost', Constraint(optmodel.psn, rule=eTotalGCost, doc='Total generation cost in the DA market [MEUR]'))

    # Generation emission cost in DA [M€]
    def eTotalECost(optmodel, p,sc,n):
        return optmodel.vTotalECost[p,sc,n] == sum(model.Par['pDuration'][n] * model.Par['pGenCO2EmissionCost'][nr] * optmodel.vEleTotalOutput[p,sc,n,nr] for nr in model.nr)
    optmodel.__setattr__('eTotalECost', Constraint(optmodel.psn, rule=eTotalECost, doc='Total emission cost in the DA market [MEUR]'))
    # Consumption operation cost in DA [M€]
    def eTotalCCost(optmodel, p,sc,n):
        return optmodel.vTotalCCost[p,sc,n] == sum(model.Par['pDuration'][n] * model.Par['pGenLinearTerm'][g] * optmodel.vEleTotalCharge[p,sc,n,g] for g in model.es)
    optmodel.__setattr__('eTotalCCost', Constraint(optmodel.psn, rule=eTotalCCost, doc='Total consumption cost in the DA market [MEUR]'))
    # Reserve operation revenue in DA [M€]
    def eTotalRCost(optmodel, p,sc,n):
        return optmodel.vTotalRCost[p,sc,n] == (sum(                            sum(model.Par[f'pOperatingReservePrice_{idx}'][p,sc,n]                                                           * optmodel.__getattribute__(f'vEleReserveProd_{idx}')[p,sc,n,nr] for idx in ['Up_SR','Down_SR'                  ]) for nr in model.nr if model.Par['pGenNoOperatingReserve'][nr] == 0) +
                                                sum(model.Par['pDuration'][n] * sum(model.Par[f'pOperatingReservePrice_{idx}'][p,sc,n] * model.Par[f'pOperatingReserveActivation_{idx}'][p,sc,n] * optmodel.__getattribute__(f'vEleReserveProd_{idx}')[p,sc,n,nr] for idx in ['Up_SR','Down_SR','Up_TR','Down_TR']) for nr in model.nr if model.Par['pGenNoOperatingReserve'][nr] == 0) +
                                                sum(                            sum(model.Par[f'pOperatingReservePrice_{idx}'][p,sc,n]                                                           * optmodel.__getattribute__(f'vEleReserveCons_{idx}')[p,sc,n,eh] for idx in ['Up_SR','Down_SR'                  ]) for eh in model.eh if model.Par['pGenNoOperatingReserve'][eh] == 0) +
                                                sum(model.Par['pDuration'][n] * sum(model.Par[f'pOperatingReservePrice_{idx}'][p,sc,n] * model.Par[f'pOperatingReserveActivation_{idx}'][p,sc,n] * optmodel.__getattribute__(f'vEleReserveCons_{idx}')[p,sc,n,eh] for idx in ['Up_TR','Down_TR','Up_TR','Down_TR']) for eh in model.eh if model.Par['pGenNoOperatingReserve'][eh] == 0))
    optmodel.__setattr__('eTotalRCost', Constraint(optmodel.psn, rule=eTotalRCost, doc='Total reserve revenue in the market [MEUR]'))

    print('--- Declaring the ObjFunc components:                                  {} seconds'.format(round(time.time() - StartTime)))

    return model

def create_constraints(model, optmodel):
    # this function declares constraints
    StartTime = time.time()  # to compute elapsed time

    print('-- Declaring constraints for the market')

    # incoming and outgoing lines (lin) (lout)
    lin   = defaultdict(list)
    lout  = defaultdict(list)
    for ni,nf,cc in model.ela:
        lin  [nf].append((ni,cc))
        lout [ni].append((nf,cc))
    
    hin   = defaultdict(list)
    hout  = defaultdict(list)
    for ni,nf,cc in model.hpa:
        hin  [nf].append((ni,cc))
        hout [ni].append((nf,cc))

    # nodes to generators (g2n)
    g2n = defaultdict(list)
    for nd,g in model.n2g:
        g2n[nd].append(g)
    gt2n = defaultdict(list)
    for nd,t in model.nd*model.t:
        if (nd,t) in model.n2g:
            gt2n[nd].append(t)
    hz2n = defaultdict(list)
    for nd,hz in model.nd*model.hz:
        if (nd,hz) in model.n2h:
            hz2n[nd].append(hz)
    hs2n = defaultdict(list)
    for nd,hs in model.nd*model.hs:
        if (nd,hs) in model.n2h:
            hs2n[nd].append(hs)

    #%% Constraints
    # Corrections of the units in the electricity and hydrogen markets
    def eMarketCorrectionEleProd(optmodel, p,sc,n,g):
        return optmodel.vEleTotalOutput[p,sc,n,g] == model.Par['pVarPositionGeneration'][g][p,sc,n] + optmodel.vEleTotalOutputDelta[p,sc,n,g]
    optmodel.__setattr__('eMarketCorrectionEleProd', Constraint(optmodel.psng, rule=eMarketCorrectionEleProd, doc='Correction of the electricity generation'))

    def eMarketCorrectionEleCharge(optmodel, p,sc,n,eh):
        return optmodel.vEleTotalCharge[p,sc,n,eh] == model.Par['pVarPositionConsumption'][eh][p,sc,n] + optmodel.vEleTotalChargeDelta[p,sc,n,eh]
    optmodel.__setattr__('eMarketCorrectionEleCharge', Constraint(optmodel.psneh, rule=eMarketCorrectionEleCharge, doc='Correction of the electricity consumption in the BES'))

    def eMarketCorrectionHydProd(optmodel, p,sc,n,h):
        return optmodel.vHydTotalOutput[p,sc,n,h] == model.Par['pVarPositionGeneration'][h][p,sc,n] + optmodel.vHydTotalOutputDelta[p,sc,n,h]
    optmodel.__setattr__('eMarketCorrectionHydProd', Constraint(optmodel.psnh, rule=eMarketCorrectionHydProd, doc='Correction of the hydrogen generation'))

    def eMarketCorrectionHydCharge(optmodel, p,sc,n,he):
        return optmodel.vHydTotalCharge[p,sc,n,he] == model.Par['pVarPositionConsumption'][he][p,sc,n] + optmodel.vHydTotalChargeDelta[p,sc,n,he]
    optmodel.__setattr__('eMarketCorrectionHydCharge', Constraint(optmodel.psnhe, rule=eMarketCorrectionHydCharge, doc='Correction of the hydrogen consumption in the HES'))

    def eMarketCorrectionHydDemand(optmodel, p,sc,n,nd):
        return optmodel.vHydTotalDemand[p,sc,n,nd] == model.Par['pHydrogenDemand'][nd][p,sc,n] + optmodel.vHydTotalDemandDelta[p,sc,n,nd]
    optmodel.__setattr__('eMarketCorrectionHydDemand', Constraint(optmodel.psnnd, rule=eMarketCorrectionHydDemand, doc='Correction of the hydrogen demand'))

    print('--- Declaring the market correction:                                   {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time()  # to compute elapsed time

    # 1st kirchhoff law: electrical energy conservation or balance in the DA market
    def eElectricityBalance(optmodel, p,sc,n,nd):
        if sum(1 for g in g2n[nd]) + sum(1 for g in hz2n[nd]) + sum(1 for g in hs2n[nd]) + sum(1 for nf, cc in lout[nd]) + sum(1 for ni, cc in lin[nd]):
            return (sum(optmodel.vEleTotalOutput[p,sc,n,g] for g in model.g  if (nd,g) in model.n2g) - sum(optmodel.vEleTotalCharge[p,sc,n,es] for es in model.es if (nd,es) in model.n2g) - sum(optmodel.vEleTotalCharge[p,sc,n,hz] + optmodel.vHydStandByConsumption[p,sc,n,hz] for hz in model.hz if (nd,hz) in model.n2h) - sum(optmodel.vHydCompressorConsumption[p,sc,n,hs] for hs in model.hs if (nd,hs) in model.n2h)
                  - sum(optmodel.vEleNetFlow[p,sc,n,nd,nf,cc] for (nf,cc) in lout[nd]) + sum(optmodel.vEleNetFlow[p,sc,n,ni,nd,cc] for (ni,cc) in lin[nd]) + optmodel.vElectricityBuy[p,sc,n,nd] - optmodel.vElectricitySell[p,sc,n,nd] == model.Par['pElectricityDemand'][nd][p,sc,n] - optmodel.vENS[p,sc,n,nd])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eElectricityBalance', Constraint(optmodel.psnnd, rule=eElectricityBalance, doc='Electricity balance in the DA market'))

    # hydrogen energy conservation or balance
    def eHydrogenBalance(optmodel, p,sc,n,nd):
        if sum(1 for h in hz2n[nd]) + sum(1 for h in hs2n[nd]) + sum(1 for h in gt2n[nd]) + sum(1 for nf, cc in hout[nd]) + sum(1 for ni, cc in hin[nd]):
            return (sum(optmodel.vHydTotalOutput[p,sc,n,h] for h in model.h if (nd,h) in model.n2h) - sum(optmodel.vHydTotalCharge[p,sc,n,hs] for hs in model.hs if (nd,hs) in model.n2h) - sum(optmodel.vHydTotalCharge[p,sc,n,t] for t in model.t if (nd,t) in model.n2g)
                  - sum(optmodel.vHydNetFlow[p,sc,n,nd,nf,cc] for (nf,cc) in hout[nd]) + sum(optmodel.vHydNetFlow[p,sc,n,ni,nd,cc] for (ni,cc) in hin[nd]) + optmodel.vHydrogenBuy[   p,sc,n,nd] - optmodel.vHydrogenSell[   p,sc,n,nd] == optmodel.vHydTotalDemand[p,sc,n,nd] - optmodel.vHNS[p,sc,n,nd])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydrogenBalance', Constraint(optmodel.psnnd, rule=eHydrogenBalance, doc='Hydrogen balance in the DA market'))

    print('--- Declaring the energy balance:                                      {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Upward and downward operating reserves provided by non-renewable generators, and ESS when charging for each area [GW]
    def eReserveRequire_Up_SR(optmodel, p,sc,n):
        if model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] > 0.0:
            return sum(optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] for nr in model.nr if model.Par['pGenNoOperatingReserve'][nr] == 0) + sum(optmodel.vEleReserveCons_Up_SR[p,sc,n,eh] for eh in model.eh) <= model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveRequire_Up_SR', Constraint(optmodel.psn, rule=eReserveRequire_Up_SR, doc='Upward operating reserve in the DA market [GW]'))

    def eReserveRequire_Dw_SR(optmodel, p,sc,n):
        if model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n]:
            return sum(optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] for nr in model.nr if model.Par['pGenNoOperatingReserve'][nr] == 0) + sum(optmodel.vEleReserveCons_Down_SR[p,sc,n,eh] for eh in model.eh) <= model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveRequire_Dw_SR', Constraint(optmodel.psn, rule=eReserveRequire_Dw_SR, doc='Downward operating reserve in the DA market [GW]'))

    def eReserveRequire_Up_TR(optmodel, p,sc,n):
        if model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n] > 0.0:
            return sum(optmodel.vEleReserveProd_Up_TR[p,sc,n,nr] for nr in model.nr if model.Par['pGenNoOperatingReserve'][nr] == 0) + sum(optmodel.vEleReserveCons_Up_TR[p,sc,n,eh] for eh in model.eh) <= model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveRequire_Up_TR', Constraint(optmodel.psn, rule=eReserveRequire_Up_TR, doc='Upward operating reserve in the DA market [GW]'))

    def eReserveRequire_Dw_TR(optmodel, p,sc,n):
        if model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]:
            return sum(optmodel.vEleReserveProd_Down_TR[p,sc,n,nr] for nr in model.nr if model.Par['pGenNoOperatingReserve'][nr] == 0) + sum(optmodel.vEleReserveCons_Down_TR[p,sc,n,eh] for eh in model.eh) <= model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveRequire_Dw_TR', Constraint(optmodel.psn, rule=eReserveRequire_Dw_TR, doc='Downward operating reserve in the DA market [GW]'))

    print('--- Declaring the operating reserves:                                  {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # # Ratio between downward and upward operating reserves provided by non-renewable generators, and ESS when charging for each area [GW]
    # def eReserveProdMinRatioDwUp_SR(optmodel, p,sc,n, nr):
    #     if model.Par['pParMinRatioDwUp'] > 0.0 and model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][nr] == 0 and model.Par['pMaxPower2ndBlock'][nr][p,sc,n]:
    #         return optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] >= optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] * model.Par['pParMinRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveProdMinRatioDwUp_SR', Constraint(optmodel.psnnr, rule=eReserveProdMinRatioDwUp_SR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    # def eReserveProdMaxRatioDwUp_SR(optmodel, p,sc,n, nr):
    #     if model.Par['pParMaxRatioDwUp'] < 1.0 and model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][nr] == 0 and model.Par['pMaxPower2ndBlock'][nr][p,sc,n]:
    #         return optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] <= optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] * model.Par['pParMaxRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveProdMaxRatioDwUp_SR', Constraint(optmodel.psnnr, rule=eReserveProdMaxRatioDwUp_SR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    # def eReserveProdMinRatioDwUp_TR(optmodel, p,sc,n, nr):
    #     if model.Par['pParMinRatioDwUp'] > 0.0 and model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][nr] == 0 and model.Par['pMaxPower2ndBlock'][nr][p,sc,n]:
    #         return optmodel.vEleReserveProd_Down_TR[p,sc,n,nr] >= optmodel.vEleReserveProd_Up_TR[p,sc,n,nr] * model.Par['pParMinRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveProdMinRatioDwUp_TR', Constraint(optmodel.psnnr, rule=eReserveProdMinRatioDwUp_TR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    # def eReserveProdMaxRatioDwUp_TR(optmodel, p,sc,n, nr):
    #     if model.Par['pParMaxRatioDwUp'] < 1.0 and model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][nr] == 0 and model.Par['pMaxPower2ndBlock'][nr][p,sc,n]:
    #         return optmodel.vEleReserveProd_Down_TR[p,sc,n,nr] <= optmodel.vEleReserveProd_Up_TR[p,sc,n,nr] * model.Par['pParMaxRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveProdMaxRatioDwUp_TR', Constraint(optmodel.psnnr, rule=eReserveProdMaxRatioDwUp_TR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    # def eReserveConsMinRatioDwUp_SR(optmodel, p,sc,n, eh):
    #     if model.Par['pParMinRatioDwUp'] > 0.0 and model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][eh] == 0 and model.Par['pMaxPower2ndBlock'][eh][p,sc,n]:
    #         return optmodel.vEleReserveCons_Down_SR[p,sc,n,eh] >= optmodel.vEleReserveCons_Up_SR[p,sc,n,eh] * model.Par['pParMinRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveConsMinRatioDwUp_SR', Constraint(optmodel.psneh, rule=eReserveConsMinRatioDwUp_SR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    #
    # def eReserveConsMaxRatioDwUp_SR(optmodel, p,sc,n, eh):
    #     if model.Par['pParMaxRatioDwUp'] < 1.0 and model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][eh] == 0 and model.Par['pMaxPower2ndBlock'][eh][p,sc,n]:
    #         return optmodel.vEleReserveCons_Down_SR[p,sc,n,eh] <= optmodel.vEleReserveCons_Up_SR[p,sc,n,eh] * model.Par['pParMaxRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveConsMaxRatioDwUp_SR', Constraint(optmodel.psneh, rule=eReserveConsMaxRatioDwUp_SR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    # def eReserveConsMinRatioDwUp_TR(optmodel, p,sc,n, eh):
    #     if model.Par['pParMinRatioDwUp'] > 0.0 and model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][eh] == 0 and model.Par['pMaxPower2ndBlock'][eh][p,sc,n]:
    #         return optmodel.vEleReserveCons_Down_TR[p,sc,n,eh] >= optmodel.vEleReserveCons_Up_TR[p,sc,n,eh] * model.Par['pParMinRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveConsMinRatioDwUp_TR', Constraint(optmodel.psneh, rule=eReserveConsMinRatioDwUp_TR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    # def eReserveConsMaxRatioDwUp_TR(optmodel, p,sc,n, eh):
    #     if model.Par['pParMaxRatioDwUp'] < 1.0 and model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n] and model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n] and model.Par['pGenNoOperatingReserve'][eh] == 0 and model.Par['pMaxPower2ndBlock'][eh][p,sc,n]:
    #         return optmodel.vEleReserveCons_Down_TR[p,sc,n,eh] <= optmodel.vEleReserveCons_Up_TR[p,sc,n,eh] * model.Par['pParMaxRatioDwUp']
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eReserveConsMaxRatioDwUp_TR', Constraint(optmodel.psneh, rule=eReserveConsMaxRatioDwUp_TR, doc='Ratio between downward and upward operating reserves in the DA market'))
    #
    # print('--- Declaring the ratio between down/up operating reserves:            {} seconds'.format(round(time.time() - StartTime)))
    # StartTime = time.time() # to compute elapsed time

    # operating reserves from ESS can only be provided if enough energy is available for producing them
    def eReserveUpIfEnergyProd(optmodel, p,sc,n, es):
        if model.Par['pGenNoOperatingReserve'][es] == 0  and (n,es) in model.nessc:
            if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][es][p,sc,n]:
                return model.Par['pOperatingReserveActivation_Up_SR'][p,sc,n] * optmodel.vEleReserveProd_Up_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Up_TR'][p,sc,n]  * optmodel.vEleReserveProd_Up_TR[p,sc,n,es] <= (optmodel.vEleInventory[p,sc,n,es] - model.Par['pMinStorage'][es][p,sc,n]) / model.Par['pDuration'][n]
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveUpIfEnergyProd', Constraint(optmodel.psnes, rule=eReserveUpIfEnergyProd, doc='up   operating reserve if energy available [GW]'))

    def eReserveDwIfEnergyProd(optmodel, p,sc,n, es):
        if model.Par['pGenNoOperatingReserve'][es] == 0 and (n,es) in model.nessc:
            if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][es][p,sc,n]:
                return model.Par['pOperatingReserveActivation_Down_SR'][p,sc,n] * optmodel.vEleReserveProd_Down_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Down_TR'][p,sc,n] * optmodel.vEleReserveProd_Down_TR[p,sc,n,es] <= (model.Par['pMaxStorage'][es][p,sc,n] - optmodel.vEleInventory[p,sc,n,es]) / model.Par['pDuration'][n]
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveDwIfEnergyProd', Constraint(optmodel.psnes, rule=eReserveDwIfEnergyProd, doc='down operating reserve if energy available [GW]'))

    # operating reserves from ESS can only be provided if enough energy is available for storing them
    def eReserveUpIfEnergyCons(optmodel, p,sc,n,es):
        if model.Par['pGenNoOperatingReserve'][es] == 0:
            if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pMaxCharge2ndBlock'][es][p,sc,n]:
                return model.Par['pOperatingReserveActivation_Up_SR'][p,sc,n] * optmodel.vEleReserveCons_Up_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Up_TR'][p,sc,n] * optmodel.vEleReserveCons_Up_TR[p,sc,n,es] <= (model.Par['pMaxStorage'][es][p,sc,n] - optmodel.vEleInventory[p,sc,n,es]) / model.Par['pDuration'][n]
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveUpIfEnergyCons', Constraint(optmodel.psnes, rule=eReserveUpIfEnergyCons, doc='up   operating reserve if energy available [GW]'))

    def eReserveDwIfEnergyCons(optmodel, p,sc,n, es):
        if model.Par['pGenNoOperatingReserve'][es] == 0:
            if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pMaxCharge2ndBlock'][es][p,sc,n]:
                return model.Par['pOperatingReserveActivation_Down_SR'][p,sc,n] * optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Down_TR'][p,sc,n] * optmodel.vEleReserveCons_Down_TR[p,sc,n,es] <= (optmodel.vEleInventory[p,sc,n,es] - model.Par['pMinStorage'][es][p,sc,n]) / model.Par['pDuration'][n]
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveDwIfEnergyCons', Constraint(optmodel.psnes, rule=eReserveDwIfEnergyCons, doc='down operating reserve if energy available [GW]'))


    print('--- Declaring the operating reserves from ESS:                         {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # # maximum and minimum relative inventory of ESS (only for load levels multiple of 1, 24, 168, 8736 h depending on the ESS storage type) constrained by the ESS commitment decision times the maximum capacity [p.u.]
    # def eDAMaxInventory2Commitment(optmodel, p,sc,n, es):
    #     if model.Par['pDAMaxStorage'][es][p,sc,n] and model.Par['pDAMaxPower2ndBlock'][es][p,sc,n] and (n,es) in model.nesc:
    #         return optmodel.vESSInventory[p,sc,n,es] / model.Par['pDAMaxStorage'][es][p,sc,n] <= optmodel.vDAGenCommitment[p,sc,n,es]
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eDAMaxInventory2Commitment', Constraint(optmodel.psnes, rule=eDAMaxInventory2Commitment, doc='maximum inventory to commitment [p.u.]'))
    #
    # def eDAMinInventory2Commitment(optmodel, p,sc,n, es):
    #     if model.Par['pDAMaxStorage'][es][p,sc,n] and model.Par['pDAMaxPower2ndBlock'][es][p,sc,n] and (n,es) in model.nesc:
    #         return optmodel.vESSInventory[p,sc,n,es] / model.Par['pDAMaxStorage'][es][p,sc,n] >= optmodel.vDAGenCommitment[p,sc,n,es]
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eDAMinInventory2Commitment', Constraint(optmodel.psnes, rule=eDAMinInventory2Commitment, doc='minimum inventory to commitment [p.u.]'))
    #
    # print('--- Declaring the maximum and minimum relative inventory of ESS:       {} seconds'.format(round(time.time() - StartTime)))
    # StartTime = time.time() # to compute elapsed time

    # Energy inflows of ESS (only for load levels multiple of 1, 24, 168, 8736 h depending on the ESS storage type) constrained by the ESS commitment decision times the inflows data [p.u.]
    def eMaxInflows2Commitment(optmodel, p,sc,n, es):
        if model.Par['pMaxStorage'][es][p,sc,n] and model.Par['pMaxPower2ndBlock'][es][p,sc,n] and model.Par['pVarMaxInflows'][es][p,sc,n] and (n,es) in model.nessc:
            return optmodel.vEleEnergyInflows[p,sc,n,es] / model.Par['pVaxMaxInflows'][es][p,sc,n] <= optmodel.vGenCommitment[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxInflows2Commitment', Constraint(optmodel.psnes, rule=eMaxInflows2Commitment, doc='energy inflows to commitment [p.u.]'))

    def eMinInflows2Commitment(optmodel, p,sc,n, es):
        if model.Par['pMinStorage'][es][p,sc,n] and model.Par['pMaxPower2ndBlock'][es][p,sc,n] and model.Par['pVarMinInflows'][es][p,sc,n] and (n,es) in model.nessc:
            return optmodel.vEleEnergyInflows[p,sc,n,es] / model.Par['pVaxMinInflows'][es][p,sc,n] >= optmodel.vGenCommitment[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinInflows2Commitment', Constraint(optmodel.psnes, rule=eMinInflows2Commitment, doc='energy inflows to commitment [p.u.]'))

    print('--- Declaring the energy inflows of ESS:                               {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # ESS energy inventory (only for load levels multiple of 1, 24, 168 h depending on the ESS storage type) [GWh]
    def eEleInventory(optmodel, p,sc,n, es):
        if model.Par['pMaxCharge'][es][p,sc,n] + model.Par['pMaxPower'][es][p,sc,n] and (n,es) in model.nessc:
            if   model.n.ord(n) == model.Par['pCycleTimeStep'][es]:
                return model.Par['pInitialInventory'][es][p,sc,n]                                      + sum(model.Par['pDuration'][n2] * (optmodel.vEleEnergyInflows[p,sc,n2,es] - optmodel.vEleEnergyOutflows[p,sc,n2,es] - optmodel.vEleTotalOutput[p,sc,n2,es] + model.Par['pGenEfficiency'][es] * optmodel.vEleTotalCharge[p,sc,n2,es]) for n2 in list(model.n2)[model.n.ord(n) - model.Par['pCycleTimeStep'][es]:model.n.ord(n)]) == optmodel.vEleInventory[p,sc,n,es] + optmodel.vEleSpillage[p,sc,n,es]
            elif model.n.ord(n) >  model.Par['pCycleTimeStep'][es]:
                return optmodel.vEleInventory[p,sc,model.n.prev(n,model.Par['pCycleTimeStep'][es]),es] + sum(model.Par['pDuration'][n2] * (optmodel.vEleEnergyInflows[p,sc,n2,es] - optmodel.vEleEnergyOutflows[p,sc,n2,es] - optmodel.vEleTotalOutput[p,sc,n2,es] + model.Par['pGenEfficiency'][es] * optmodel.vEleTotalCharge[p,sc,n2,es]) for n2 in list(model.n2)[model.n.ord(n) - model.Par['pCycleTimeStep'][es]:model.n.ord(n)]) == optmodel.vEleInventory[p,sc,n,es] + optmodel.vEleSpillage[p,sc,n,es]
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleInventory', Constraint(optmodel.psnes, rule=eEleInventory, doc='ESS inventory balance [GWh]'))

    def eHydInventory(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge'][hs][p,sc,n] + model.Par['pMaxPower'][hs][p,sc,n] and (n,hs) in model.nessc:
            if   model.n.ord(n) == model.Par['pCycleTimeStep'][hs]:
                return model.Par['pInitialInventory'][hs][p,sc,n]                                      + sum(model.Par['pDuration'][n2] * (optmodel.vHydEnergyInflows[p,sc,n2,hs] - optmodel.vHydEnergyOutflows[p,sc,n2,hs] - optmodel.vHydTotalOutput[p,sc,n2,hs] + model.Par['pGenEfficiency'][hs] * optmodel.vHydTotalCharge[p,sc,n2,hs]) for n2 in list(model.n2)[model.n.ord(n) - model.Par['pCycleTimeStep'][hs]:model.n.ord(n)]) == optmodel.vHydInventory[p,sc,n,hs] + optmodel.vHydSpillage[p,sc,n,hs]
            elif model.n.ord(n) >  model.Par['pCycleTimeStep'][hs]:
                return optmodel.vHydInventory[p,sc,model.n.prev(n,model.Par['pCycleTimeStep'][hs]),hs] + sum(model.Par['pDuration'][n2] * (optmodel.vHydEnergyInflows[p,sc,n2,hs] - optmodel.vHydEnergyOutflows[p,sc,n2,hs] - optmodel.vHydTotalOutput[p,sc,n2,hs] + model.Par['pGenEfficiency'][hs] * optmodel.vHydTotalCharge[p,sc,n2,hs]) for n2 in list(model.n2)[model.n.ord(n) - model.Par['pCycleTimeStep'][hs]:model.n.ord(n)]) == optmodel.vHydInventory[p,sc,n,hs] + optmodel.vHydSpillage[p,sc,n,hs]
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydInventory', Constraint(optmodel.psnhs, rule=eHydInventory, doc='ESS inventory balance [GWh]'))

    print('--- Declaring the ESS energy inventory:                                {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Energy conversion from energy from electricity to hydrogen and vice versa [p.u.]
    def eAllEnergy2Hyd(optmodel, p,sc,n, hz):
        if model.Par['pMaxPower'][hz][p,sc,n] and hz in model.h:
            return optmodel.vHydTotalOutput[p,sc,n,hz] == optmodel.vEleTotalCharge[p,sc,n,hz] / model.Par['pGenProductionFunction'][hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eAllEnergy2Hyd', Constraint(optmodel.psnhz, rule=eAllEnergy2Hyd, doc='energy conversion from different energy type to hydrogen [p.u.]'))

    def eAllEnergy2Ele(optmodel, p,sc,n, g):
        if model.Par['pMaxPower'][g][p,sc,n] and g in model.t:
            return optmodel.vEleTotalOutput[p,sc,n,g] == optmodel.vHydTotalCharge[p,sc,n,g] * model.Par['pGenProductionFunction'][g]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eAllEnergy2Ele', Constraint(optmodel.psng, rule=eAllEnergy2Ele, doc='energy conversion from different energy type to electricity [p.u.]'))

    # ESS outflows (only for load levels multiple of 1, 24, 168, 672, and 8736 h depending on the ESS outflow cycle) must be satisfied [GWh]
    def eMaxEleOutflows2Commitment(optmodel, p,sc,n, es):
        if model.Par['pMaxCharge'][es][p,sc,n] and model.Par['pMaxPower2ndBlock'][es][p,sc,n] and model.Par['pVarMaxOutflows'][es][p,sc,n] and (n,es) in model.nessc:
            return optmodel.vEleEnergyOutflows[p,sc,n,es] / model.Par['pVarMaxOutflows'][es][p,sc,n] <= optmodel.vGenCommitment[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxEleOutflows2Commitment', Constraint(optmodel.psnes, rule=eMaxEleOutflows2Commitment, doc='energy outflows to commitment [p.u.]'))

    def eMinEleOutflows2Commitment(optmodel, p,sc,n, es):
        if model.Par['pMinCharge'][es][p,sc,n] and model.Par['pMaxPower2ndBlock'][es][p,sc,n] and model.Par['pVarMinOutflows'][es][p,sc,n] and (n,es) in model.nessc:
            return optmodel.vEleEnergyOutflows[p,sc,n,es] / model.Par['pVarMinOutflows'][es][p,sc,n] >= optmodel.vGenCommitment[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinEleOutflows2Commitment', Constraint(optmodel.psnes, rule=eMinEleOutflows2Commitment, doc='energy outflows to commitment [p.u.]'))

    def eMaxHydOutflows2Commitment(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge'][hs][p,sc,n] and model.Par['pMaxPower2ndBlock'][hs][p,sc,n] and model.Par['pVarMaxOutflows'][hs][p,sc,n] and (n,hs) in model.nessc:
            return optmodel.vHydEnergyOutflows[p,sc,n,hs] / model.Par['pVarMaxOutflows'][hs][p,sc,n] <= optmodel.vHydCommitment[p,sc,n,hs]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxHydOutflows2Commitment', Constraint(optmodel.psnhs, rule=eMaxHydOutflows2Commitment, doc='energy outflows to commitment [p.u.]'))

    def eMinHydOutflows2Commitment(optmodel, p,sc,n, hs):
        if model.Par['pMinCharge'][hs][p,sc,n] and model.Par['pMaxPower2ndBlock'][hs][p,sc,n] and model.Par['pVarMinOutflows'][hs][p,sc,n] and (n,hs) in model.nessc:
            return optmodel.vHydEnergyOutflows[p,sc,n,hs] / model.Par['pVarMinOutflows'][hs][p,sc,n] >= optmodel.vHydCommitment[p,sc,n,hs]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinHydOutflows2Commitment', Constraint(optmodel.psnhs, rule=eMinHydOutflows2Commitment, doc='energy outflows to commitment [p.u.]'))

    def eEleEnergyOutflows(optmodel, p,sc,n, es):
        if model.Par['pMaxCharge'][es][p,sc,n] + model.Par['pMaxPower'][es][p,sc,n] and (n,es) in model.nesso:
            return sum(optmodel.vEleEnergyOutflows[p,sc,n2,es] - model.Par['pVarMaxOutflows'][es][p,sc,n2] for n2 in list(model.n2)[model.n.ord(n) - model.Par['pOutflowsTimeStep'][es]:model.n.ord(n)]) == 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleEnergyOutflows', Constraint(optmodel.psnes, rule=eEleEnergyOutflows, doc='electricity energy outflows of an ESS unit [GWh]'))

    def eHydMinEnergyOutflows(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge'][hs][p,sc,n] + model.Par['pMaxPower'][hs][p,sc,n] and (n,hs) in model.nesso:
            return sum(optmodel.vHydEnergyOutflows[p,sc,n2,hs] - model.Par['pVarMinOutflows'][hs][p,sc,n2] for n2 in list(model.n2)[model.n.ord(n) - model.Par['pOutflowsTimeStep'][hs]:model.n.ord(n)]) >= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydMinEnergyOutflows', Constraint(optmodel.psnhs, rule=eHydMinEnergyOutflows, doc='hydrogen energy outflows of an ESS unit [tH2]'))

    def eHydMaxEnergyOutflows(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge'][hs][p,sc,n] + model.Par['pMaxPower'][hs][p,sc,n] and (n,hs) in model.nesso:
            return sum(optmodel.vHydTotalOutput[p,sc,n2,hs] - model.Par['pVarMaxOutflows'][hs][p,sc,n2] for n2 in list(model.n2)[model.n.ord(n) - model.Par['pOutflowsTimeStep'][hs]:model.n.ord(n)]) <= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydMaxEnergyOutflows', Constraint(optmodel.psnhs, rule=eHydMaxEnergyOutflows, doc='hydrogen energy outflows of an ESS unit [tH2]'))

    # Demand cycle target
    def eHydDemandCycleTarget(optmodel, p,sc,n, nd):
        if model.Par['pParTargetDemand'] > 0.0 and sum(1 for idx in model.psn if model.Par['pHydrogenDemand'][nd][idx]) > 0.0 and model.n.ord(n) % model.Par['pParDemandType'] == 0:
            return sum(optmodel.vHydTotalDemand[p,sc,n2,nd]                                             for n2 in list(model.n2)[model.n.ord(n) - int(model.Par['pParDemandType']):model.n.ord(n)]) - model.Par['pParTargetDemand'] == 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydDemandCycleTarget', Constraint(optmodel.psnnd, rule=eHydDemandCycleTarget, doc='hydrogen demand cycle target [tH2]'))

    # def eHydMinEnergyOutflowsHZ(optmodel, p,sc,n,hz):
    #     if model.Par['pMaxCharge'][hz][p,sc,n] + model.Par['pMaxPower'][hz][p,sc,n] and (n,hz) in model.nhhzo and sum(1 for (nd,h) in optmodel.n2h if nd == model.Par['pGenNode'][hz] and h not in model.hz) == 0 and sum(1 for (nf, pa) in hout[model.Par['pGenNode'][hz]] for h in model.hs if (nf, h) in model.n2h) == 0:
    #         return sum(optmodel.vHydTotalOutput[p,sc,n2,hz] + optmodel.vHNS[p,sc,n2,model.Par['pGenNode'][hz]] - model.Par['pVarMinOutflows'][hz][p,sc,n2] for n2 in list(model.n2)[model.n.ord(n) - model.Par['pOutflowsTimeStep'][hz]:model.n.ord(n)]) >= 0.0
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eHydMinEnergyOutflowsHZ', Constraint(optmodel.psnhz, rule=eHydMinEnergyOutflowsHZ, doc='hydrogen energy outflows of an H2 unit [tH2]'))
    # 
    # def eHydMaxEnergyOutflowsHZ(optmodel, p,sc,n,hz):
    #     if model.Par['pMaxCharge'][hz][p,sc,n] + model.Par['pMaxPower'][hz][p,sc,n] and (n,hz) in model.nhhzo and sum(1 for (nd,h) in optmodel.n2h if nd == model.Par['pGenNode'][hz] and h not in model.hz) == 0 and sum(1 for (nf, pa) in hout[model.Par['pGenNode'][hz]] for h in model.hs if (nf, h) in model.n2h) == 0:
    #         return sum(optmodel.vHydTotalOutput[p,sc,n2,hz] + optmodel.vHNS[p,sc,n2,model.Par['pGenNode'][hz]] - model.Par['pVarMaxOutflows'][hz][p,sc,n2] for n2 in list(model.n2)[model.n.ord(n) - model.Par['pOutflowsTimeStep'][hz]:model.n.ord(n)]) <= 0.0
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eHydMaxEnergyOutflowsHZ', Constraint(optmodel.psnhz, rule=eHydMaxEnergyOutflowsHZ, doc='hydrogen energy outflows of an H2 unit [tH2]'))


    print('--- Declaring the ESS outflows:                                        {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Maximum and minimum output of the second block of a committed unit (all except the VRES and ESS units) [p.u.]
    def eMaxEleOutput2ndBlock(optmodel, p,sc,n, nr):
        if   (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][nr][p,sc,n] and nr not in model.es and n != model.n.last():
            return (optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] + optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] + optmodel.vEleReserveProd_Up_TR[p,sc,n,nr])/ model.Par['pMaxPower2ndBlock'][nr][p,sc,n] <= optmodel.vGenCommitment[p,sc,n,nr] - optmodel.vGenStartUp[p,sc,n,nr] - optmodel.vGenShutDown[p,sc,model.n.next(n),nr]
        elif (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][nr][p,sc,n] and nr not in model.es and n == model.n.last():
            return (optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] + optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] + optmodel.vEleReserveProd_Up_TR[p,sc,n,nr])/ model.Par['pMaxPower2ndBlock'][nr][p,sc,n] <= optmodel.vGenCommitment[p,sc,n,nr] - optmodel.vGenStartUp[p,sc,n,nr]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxEleOutput2ndBlock', Constraint(optmodel.psnnr, rule=eMaxEleOutput2ndBlock, doc='max output of the second block of a committed unit [p.u.]'))

    def eMinEleOutput2ndBlock(optmodel, p,sc,n, nr):
        if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][nr][p,sc,n] and nr not in model.es:
            return (optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] - optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] - optmodel.vEleReserveProd_Down_TR[p,sc,n,nr])/ model.Par['pMaxPower2ndBlock'][nr][p,sc,n] >= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinEleOutput2ndBlock', Constraint(optmodel.psnnr, rule=eMinEleOutput2ndBlock, doc='min output of the second block of a committed unit [p.u.]'))

    def eMaxHydOutput2ndBlock(optmodel, p,sc,n, hz):
        if   model.Par['pMaxPower2ndBlock'][hz][p,sc,n] and hz not in model.es and n != model.n.last():
            return optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz] / model.Par['pMaxPower2ndBlock'][hz][p,sc,n] <= optmodel.vHydCommitment[p,sc,n,hz] - optmodel.vHydStartUp[p,sc,n,hz] - optmodel.vHydShutDown[p,sc,model.n.next(n),hz]
        elif model.Par['pMaxPower2ndBlock'][hz][p,sc,n] and hz not in model.es and n == model.n.last():
            return optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz] / model.Par['pMaxPower2ndBlock'][hz][p,sc,n] <= optmodel.vHydCommitment[p,sc,n,hz] - optmodel.vHydStartUp[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxHydOutput2ndBlock', Constraint(optmodel.psnhz, rule=eMaxHydOutput2ndBlock, doc='max output of the second block of a committed unit [p.u.]'))

    def eMinHydOutput2ndBlock(optmodel, p,sc,n, hz):
        if model.Par['pMaxPower2ndBlock'][hz][p,sc,n] and hz not in model.es:
            return optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz] / model.Par['pMaxPower2ndBlock'][hz][p,sc,n] >= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinHydOutput2ndBlock', Constraint(optmodel.psnhz, rule=eMinHydOutput2ndBlock, doc='min output of the second block of a committed unit [p.u.]'))

    print('--- Declaring the maximum and minimum output of the second block:      {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Maximum and minimum output of the second block of an electricity ESS [p.u.]
    def eMaxEleESSOutput2ndBlock(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][es][p,sc,n] and n != model.n.last():
            return (optmodel.vEleTotalOutput2ndBlock[p,sc,n,es] + optmodel.vEleReserveProd_Up_SR[p,sc,n,es] + optmodel.vEleReserveProd_Up_TR[p,sc,n,es])/ model.Par['pMaxPower2ndBlock'][es][p,sc,n] <= optmodel.vGenCommitment[p,sc,n,es] - optmodel.vGenStartUp[p,sc,n,es] - optmodel.vGenShutDown[p,sc,model.n.next(n),es]
        elif (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][es][p,sc,n] and n == model.n.last():
            return (optmodel.vEleTotalOutput2ndBlock[p,sc,n,es] + optmodel.vEleReserveProd_Up_SR[p,sc,n,es] + optmodel.vEleReserveProd_Up_TR[p,sc,n,es])/ model.Par['pMaxPower2ndBlock'][es][p,sc,n] <= optmodel.vGenCommitment[p,sc,n,es] - optmodel.vGenStartUp[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxEleESSOutput2ndBlock', Constraint(optmodel.psnes, rule=eMaxEleESSOutput2ndBlock, doc='max output of the second block of an ESS [p.u.]'))

    def eMinEleESSOutput2ndBlock(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pMaxPower2ndBlock'][es][p,sc,n]:
            return (optmodel.vEleTotalOutput2ndBlock[p,sc,n,es] - optmodel.vEleReserveProd_Down_SR[p,sc,n,es] - optmodel.vEleReserveProd_Down_TR[p,sc,n,es])/ model.Par['pMaxPower2ndBlock'][es][p,sc,n] >= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinEleESSOutput2ndBlock', Constraint(optmodel.psnes, rule=eMinEleESSOutput2ndBlock, doc='min output of the second block of an ESS [p.u.]'))

    def eMaxHydESSOutput2ndBlock(optmodel, p,sc,n, hs):
        if model.Par['pMaxPower2ndBlock'][hs][p,sc,n] and n != model.n.last():
            return optmodel.vHydTotalOutput2ndBlock[p,sc,n,hs] / model.Par['pMaxPower2ndBlock'][hs][p,sc,n] <= optmodel.vHydCommitment[p,sc,n,hs] - optmodel.vHydStartUp[p,sc,n,hs] - optmodel.vHydShutDown[p,sc,model.n.next(n),hs]
        elif model.Par['pMaxPower2ndBlock'][hs][p,sc,n] and n == model.n.last():
            return optmodel.vHydTotalOutput2ndBlock[p,sc,n,hs] / model.Par['pMaxPower2ndBlock'][hs][p,sc,n] <= optmodel.vHydCommitment[p,sc,n,hs] - optmodel.vHydStartUp[p,sc,n,hs]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxHydESSOutput2ndBlock', Constraint(optmodel.psnhs, rule=eMaxHydESSOutput2ndBlock, doc='max output of the second block of an ESS [p.u.]'))

    def eMinHydESSOutput2ndBlock(optmodel, p,sc,n, hs):
        if model.Par['pMaxPower2ndBlock'][hs][p,sc,n]:
            return optmodel.vHydTotalOutput2ndBlock[p,sc,n,hs] / model.Par['pMaxPower2ndBlock'][hs][p,sc,n] >= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinHydESSOutput2ndBlock', Constraint(optmodel.psnhs, rule=eMinHydESSOutput2ndBlock, doc='min output of the second block of an ESS [p.u.]'))

    # Maximum and minimum charge of an ESS [p.u.]
    def eMaxEleESSCharge2ndBlock(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pMaxCharge2ndBlock'][es][p,sc,n] and model.Par['pGenNoOperatingReserve'][es] == 0:
            return (optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] + optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + optmodel.vEleReserveCons_Down_TR[p,sc,n,es])/ model.Par['pMaxCharge2ndBlock'][es][p,sc,n] <= optmodel.vGenCommitment[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxEleESSCharge2ndBlock', Constraint(optmodel.psnes, rule=eMaxEleESSCharge2ndBlock, doc='max charge of an ESS [p.u.]'))

    def eMinEleESSCharge2ndBlock(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pMaxCharge2ndBlock'][es][p,sc,n] and model.Par['pGenNoOperatingReserve'][es] == 0:
            return (optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] - optmodel.vEleReserveCons_Up_SR[p,sc,n,es] - optmodel.vEleReserveCons_Up_TR[p,sc,n,es])/ model.Par['pMaxCharge2ndBlock'][es][p,sc,n] >= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinEleESSCharge2ndBlock', Constraint(optmodel.psnes, rule=eMinEleESSCharge2ndBlock, doc='min charge of an ESS [p.u.]'))

    def eMaxEle2HydCharge2ndBlock(optmodel, p,sc,n, hz):
        if model.Par['pMaxCharge2ndBlock'][hz][p,sc,n]:
            return (optmodel.vEleTotalCharge2ndBlock[p,sc,n,hz] + optmodel.vEleReserveCons_Down_SR[p,sc,n,hz] + optmodel.vEleReserveCons_Down_TR[p,sc,n,hz]) / model.Par['pMaxCharge2ndBlock'][hz][p,sc,n] <= optmodel.vHydCommitment[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxEle2HydCharge2ndBlock', Constraint(optmodel.psnhz, rule=eMaxEle2HydCharge2ndBlock, doc='max charge of an ESS [p.u.]'))

    def eMinEle2HydCharge2ndBlock(optmodel, p,sc,n, hz):
        if model.Par['pMaxCharge2ndBlock'][hz][p,sc,n]:
            return (optmodel.vEleTotalCharge2ndBlock[p,sc,n,hz] - optmodel.vEleReserveCons_Up_SR[p,sc,n,hz] - optmodel.vEleReserveCons_Up_TR[p,sc,n,hz]) / model.Par['pMaxCharge2ndBlock'][hz][p,sc,n] >= optmodel.vHydCommitment[p,sc,n,hz] - 1
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinEle2HydCharge2ndBlock', Constraint(optmodel.psnhz, rule=eMinEle2HydCharge2ndBlock, doc='min charge of an ESS [p.u.]'))

    def eMaxHydESSCharge2ndBlock(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge2ndBlock'][hs][p,sc,n]:
            return optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs] / model.Par['pMaxCharge2ndBlock'][hs][p,sc,n] <= optmodel.vHydCommitment[p,sc,n,hs]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxHydESSCharge2ndBlock', Constraint(optmodel.psnhs, rule=eMaxHydESSCharge2ndBlock, doc='max charge of an ESS [p.u.]'))

    def eMinHydESSCharge2ndBlock(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge2ndBlock'][hs][p,sc,n]:
            return optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs] / model.Par['pMaxCharge2ndBlock'][hs][p,sc,n] >= 0.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinHydESSCharge2ndBlock', Constraint(optmodel.psnhs, rule=eMinHydESSCharge2ndBlock, doc='min charge of an ESS [p.u.]'))

    print('--- Declaring the maximum and minimum charge of an ESS:                {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # # Incompatibility between charge and discharge of an electrical ESS [p.u.]
    # def eEleIncompatibilityChargeDischarge(optmodel, p,sc,n, es):
    #     if model.Par['pMaxCharge2ndBlock'][es][p,sc,n] and model.Par['pMaxPower2ndBlock'][es][p,sc,n] and model.Par['pGenNoOperatingReserve'][es] == 0:
    #         return ((optmodel.vEleTotalOutput2ndBlock[p,sc,n,es] + model.Par['pOperatingReserveActivation_Up_SR'  ][p,sc,n] * optmodel.vEleReserveCons_Up_SR[  p,n,es] + model.Par['pOperatingReserveActivation_Up_TR'  ][p,sc,n] * optmodel.vEleReserveCons_Up_TR[  p,n,es]) / model.Par['pMaxPower2ndBlock' ][es][p,sc,n]
    #               + (optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] + model.Par['pOperatingReserveActivation_Down_SR'][p,sc,n] * optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Down_TR'][p,sc,n] * optmodel.vEleReserveCons_Down_TR[p,sc,n,es]) / model.Par['pMaxCharge2ndBlock'][es][p,sc,n] <= 1.0)
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eEleIncompatibilityChargeDischarge', Constraint(optmodel.psnes, rule=eEleIncompatibilityChargeDischarge, doc='incompatibility between charge and discharge [p.u.]'))
    #
    # # Incompatibility between charge and discharge of an H2 ESS [p.u.]
    # def eHydIncompatibilityChargeDischarge(optmodel, p,sc,n, hs):
    #     if model.Par['pMaxCharge2ndBlock'][hs][p,sc,n] and model.Par['pMaxPower2ndBlock'][hs][p,sc,n] and model.Par['pGenNoOperatingReserve'][hs] == 0:
    #         return ( optmodel.vHydTotalOutput2ndBlock[p,sc,n,hs] / model.Par['pMaxPower2ndBlock' ][hs][p,sc,n]
    #               +  optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs] / model.Par['pMaxCharge2ndBlock'][hs][p,sc,n] <= 1.0)
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eHydIncompatibilityChargeDischarge', Constraint(optmodel.psnhs, rule=eHydIncompatibilityChargeDischarge, doc='incompatibility between charge and discharge [p.u.]'))

    # Incompatibility between charge and discharge of an electrical ESS [p.u.]
    def eEleChargingDecision(optmodel, p,sc,n, es):
        if model.Par['pMaxCharge'][es][p,sc,n] :
            return (optmodel.vEleTotalCharge[p,sc,n,es] / model.Par['pMaxCharge'][es][p,sc,n]  <= optmodel.vEleStorOperat[p,sc,n,es])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleChargingDecision', Constraint(optmodel.psnes, rule=eEleChargingDecision, doc='charging decision [p.u.]'))

    def eEleDischargingDecision(optmodel, p,sc,n, es):
        if model.Par['pMaxPower'][es][p,sc,n] :
            return (optmodel.vEleTotalOutput[p,sc,n,es] / model.Par['pMaxPower'][es][p,sc,n]  <= 1.0 - optmodel.vEleStorOperat[p,sc,n,es])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleDischargingDecision', Constraint(optmodel.psnes, rule=eEleDischargingDecision, doc='discharging decision [p.u.]'))

    def eReserveConsChargingDecision_Up(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pGenNoOperatingReserve'][es] == 0:
            return ((optmodel.vEleReserveCons_Up_SR[p,sc,n,es] + optmodel.vEleReserveCons_Up_TR[p,sc,n,es]) / (model.Par['pMaxCharge'][es][p,sc,n] - model.Par['pMinCharge'][es][p,sc,n]) <= optmodel.vEleStorOperat[p,sc,n,es])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveConsChargingDecision_Up', Constraint(optmodel.psnes, rule=eReserveConsChargingDecision_Up, doc='discharging decision [p.u.]'))

    def eReserveConsDischargingDecision_Dw(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pGenNoOperatingReserve'][es] == 0:
            return ((optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + optmodel.vEleReserveCons_Down_TR[p,sc,n,es]) / (model.Par['pMaxCharge'][es][p,sc,n] - model.Par['pMinCharge'][es][p,sc,n]) <= optmodel.vEleStorOperat[p,sc,n,es])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveConsDischargingDecision_Dw', Constraint(optmodel.psnes, rule=eReserveConsDischargingDecision_Dw, doc='discharging decision [p.u.]'))

    def eReserveProdChargingDecision_Up(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pGenNoOperatingReserve'][es] == 0:
            return ((optmodel.vEleReserveProd_Up_SR[p,sc,n,es] + optmodel.vEleReserveProd_Up_TR[p,sc,n,es]) / (model.Par['pMaxPower'][es][p,sc,n] - model.Par['pMinPower'][es][p,sc,n]) <= 1.0 - optmodel.vEleStorOperat[p,sc,n,es])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveProdChargingDecision_Up', Constraint(optmodel.psnes, rule=eReserveProdChargingDecision_Up, doc='discharging decision [p.u.]'))

    def eReserveProdDischargingDecision_Down(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pGenNoOperatingReserve'][es] == 0:
            return ((optmodel.vEleReserveProd_Down_SR[p,sc,n,es] + optmodel.vEleReserveProd_Down_TR[p,sc,n,es]) / (model.Par['pMaxPower'][es][p,sc,n] - model.Par['pMinPower'][es][p,sc,n]) <= 1.0 - optmodel.vEleStorOperat[p,sc,n,es])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveProdDischargingDecision_Down', Constraint(optmodel.psnes, rule=eReserveProdDischargingDecision_Down, doc='discharging decision [p.u.]'))

    # reserve in consecutive time steps
    def eReserveConsUpConsecutiveTime(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pGenReserveConsecutiveTime'][es] > 1 and model.n.ord(n) >= model.Par['pGenReserveConsecutiveTime'][es]:
            # return sum(optmodel.vEleReserveCons_Up_SR[p,sc,n2,es] + optmodel.vEleReserveCons_Up_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= sum(model.Par['pMaxStorage'][es][p,sc,n2] - optmodel.vEleInventory[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)])
            return sum(optmodel.vEleReserveCons_Up_SR[p,sc,n2,es] + optmodel.vEleReserveCons_Up_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= model.Par['pMaxStorage'][es][p,sc,n] - optmodel.vEleInventory[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveConsUpConsecutiveTime', Constraint(optmodel.psnes, rule=eReserveConsUpConsecutiveTime, doc='reserve in consecutive hours [p.u.]'))

    def eReserveConsDownConsecutiveTime(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pGenReserveConsecutiveTime'][es] > 1 and model.n.ord(n) >= model.Par['pGenReserveConsecutiveTime'][es]:
            # return sum(optmodel.vEleReserveCons_Down_SR[p,sc,n2,es] + optmodel.vEleReserveCons_Down_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= sum(optmodel.vEleInventory[p,sc,n2,es] - model.Par['pMinStorage'][es][p,sc,n2] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)])
            return sum(optmodel.vEleReserveCons_Down_SR[p,sc,n2,es] + optmodel.vEleReserveCons_Down_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= optmodel.vEleInventory[p,sc,n,es] - model.Par['pMinStorage'][es][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveConsDownConsecutiveTime', Constraint(optmodel.psnes, rule=eReserveConsDownConsecutiveTime, doc='reserve in consecutive hours [p.u.]'))

    def eReserveProdUpConsecutiveTime(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Up_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Up_TR'][p,sc,n]) and model.Par['pGenReserveConsecutiveTime'][es] > 1 and model.n.ord(n) >= model.Par['pGenReserveConsecutiveTime'][es]:
            # return sum(optmodel.vEleReserveProd_Up_SR[p,sc,n2,es] + optmodel.vEleReserveProd_Up_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= sum(optmodel.vEleInventory[p,sc,n2,es] - model.Par['pMinStorage'][es][p,sc,n2] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)])
            return sum(optmodel.vEleReserveProd_Up_SR[p,sc,n2,es] + optmodel.vEleReserveProd_Up_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= optmodel.vEleInventory[p,sc,n,es] - model.Par['pMinStorage'][es][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveProdUpConsecutiveTime', Constraint(optmodel.psnes, rule=eReserveProdUpConsecutiveTime, doc='reserve in consecutive hours [p.u.]'))

    def eReserveProdDownConsecutiveTime(optmodel, p,sc,n, es):
        if (model.Par['pOperatingReserveRequire_Down_SR'][p,sc,n] or model.Par['pOperatingReserveRequire_Down_TR'][p,sc,n]) and model.Par['pGenReserveConsecutiveTime'][es] > 1 and model.n.ord(n) >= model.Par['pGenReserveConsecutiveTime'][es]:
            # return sum(optmodel.vEleReserveProd_Down_SR[p,sc,n2,es] + optmodel.vEleReserveProd_Down_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= sum(model.Par['pMaxStorage'][es][p,sc,n2] - optmodel.vEleInventory[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)])
            return sum(optmodel.vEleReserveProd_Down_SR[p,sc,n2,es] + optmodel.vEleReserveProd_Down_TR[p,sc,n2,es] for n2 in list(model.n2)[model.n.ord(n)-int(model.Par['pGenReserveConsecutiveTime'][es]):model.n.ord(n)]) <= model.Par['pMaxStorage'][es][p,sc,n] - optmodel.vEleInventory[p,sc,n,es]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eReserveProdDownConsecutiveTime', Constraint(optmodel.psnes, rule=eReserveProdDownConsecutiveTime, doc='reserve in consecutive hours [p.u.]'))

    # Incompatibility between charge and discharge of an H2 ESS [p.u.]
    def eHydChargingDecision(optmodel, p,sc,n, hs):
        if model.Par['pMaxPower'][hs][p,sc,n] :
            return (optmodel.vHydTotalOutput[p,sc,n,hs] / model.Par['pMaxPower'][hs][p,sc,n]  <= optmodel.vHydStorOperat[p,sc,n,hs])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydChargingDecision', Constraint(optmodel.psnhs, rule=eHydChargingDecision, doc='charging decision [p.u.]'))

    def eHydDischargingDecision(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge'][hs][p,sc,n] :
            return (optmodel.vHydTotalCharge[p,sc,n,hs] / model.Par['pMaxCharge'][hs][p,sc,n]  <= 1.0 - optmodel.vHydStorOperat[p,sc,n,hs])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydDischargingDecision', Constraint(optmodel.psnhs, rule=eHydDischargingDecision, doc='discharging decision [p.u.]'))

    print('--- Declaring the incompatibility between charge and discharge:        {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Total output of a committed unit (all except the VRES units) [GW]
    def eEleTotalOutput(optmodel, p,sc,n, nr):
        if model.Par['pMaxPower'][nr][p,sc,n]:
            if model.Par['pMinPower'][nr][p,sc,n] == 0.0:
                return optmodel.vEleTotalOutput[p,sc,n,nr]                                      ==                                       optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] + model.Par['pOperatingReserveActivation_Up_SR'][p,sc,n] * optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] + model.Par['pOperatingReserveActivation_Up_TR'][p,sc,n] * optmodel.vEleReserveProd_Up_TR[p,sc,n,nr] - model.Par['pOperatingReserveActivation_Down_SR'][p,sc,n] * optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] - model.Par['pOperatingReserveActivation_Down_TR'][p,sc,n] * optmodel.vEleReserveProd_Down_TR[p,sc,n,nr]
            else:
                return optmodel.vEleTotalOutput[p,sc,n,nr] / model.Par['pMinPower'][nr][p,sc,n] == optmodel.vGenCommitment[p,sc,n,nr] + (optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] + model.Par['pOperatingReserveActivation_Up_SR'][p,sc,n] * optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] + model.Par['pOperatingReserveActivation_Up_TR'][p,sc,n] * optmodel.vEleReserveProd_Up_TR[p,sc,n,nr] - model.Par['pOperatingReserveActivation_Down_SR'][p,sc,n] * optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] - model.Par['pOperatingReserveActivation_Down_TR'][p,sc,n] * optmodel.vEleReserveProd_Down_TR[p,sc,n,nr]) / model.Par['pMinPower'][nr][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleTotalOutput', Constraint(optmodel.psnnr, rule=eEleTotalOutput, doc='total output of a unit [GW]'))

    print('--- Declaring the total output of a committed unit:                    {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Total output of an H2 producer unit [tH2]
    def eHydTotalOutput(optmodel, p,sc,n, hz):
        if model.Par['pMaxPower'][hz][p,sc,n]:
            if model.Par['pMinPower'][hz][p,sc,n] == 0.0:
                return optmodel.vHydTotalOutput[p,sc,n,hz]                                      ==                                       optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz]
            else:
                return optmodel.vHydTotalOutput[p,sc,n,hz] / model.Par['pMinPower'][hz][p,sc,n] == optmodel.vHydCommitment[p,sc,n,hz] + (optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz]) / model.Par['pMinPower'][hz][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydTotalOutput', Constraint(optmodel.psnhz, rule=eHydTotalOutput, doc='total output of an H2 producer unit [tH2]'))

    # Total charge of an ESS [GW]
    def eEleTotalCharge(optmodel, p,sc,n, es):
        if es in model.es:
            if model.Par['pMaxCharge'][es][p,sc,n] and model.Par['pMaxCharge2ndBlock'][es][p,sc,n]:
                if model.Par['pMinCharge'][es][p,sc,n] == 0.0:
                    return optmodel.vEleTotalCharge[p,sc,n,es]                                       ==        optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] + model.Par['pOperatingReserveActivation_Up_SR'][p,sc,n] * optmodel.vEleReserveCons_Up_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Up_TR'][p,sc,n] * optmodel.vEleReserveCons_Up_TR[p,sc,n,es] - model.Par['pOperatingReserveActivation_Down_SR'][p,sc,n] * optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Down_TR'][p,sc,n] * optmodel.vEleReserveCons_Down_TR[p,sc,n,es]
                else:
                    return optmodel.vEleTotalCharge[p,sc,n,es] / model.Par['pMinCharge'][es][p,sc,n] == 1.0 + (optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] + model.Par['pOperatingReserveActivation_Up_SR'][p,sc,n] * optmodel.vEleReserveCons_Up_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Up_TR'][p,sc,n] * optmodel.vEleReserveCons_Up_TR[p,sc,n,es] - model.Par['pOperatingReserveActivation_Down_SR'][p,sc,n] * optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + model.Par['pOperatingReserveActivation_Down_TR'][p,sc,n] * optmodel.vEleReserveCons_Down_TR[p,sc,n,es]) / model.Par['pMinCharge'][es][p,sc,n]
            else:
                return Constraint.Skip
        elif es in model.hz:
            if model.Par['pMaxCharge'][es][p,sc,n] and model.Par['pMaxCharge2ndBlock'][es][p,sc,n]:
                if model.Par['pMinCharge'][es][p,sc,n] == 0.0:
                    return optmodel.vEleTotalCharge[p,sc,n,es]                                       ==                                       optmodel.vEleTotalCharge2ndBlock[p,sc,n,es]
                else:
                    return optmodel.vEleTotalCharge[p,sc,n,es] / model.Par['pMinCharge'][es][p,sc,n] == optmodel.vHydCommitment[p,sc,n,es] + (optmodel.vEleTotalCharge2ndBlock[p,sc,n,es]) / model.Par['pMinCharge'][es][p,sc,n]
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleTotalCharge', Constraint(optmodel.psneh, rule=eEleTotalCharge, doc='total charge of an ESS unit [GW]'))

    print('--- Declaring the total charge of an ESS:                              {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Total charge of an H2 ESS unit [tH2]
    def eHydTotalCharge(optmodel, p,sc,n, hs):
        if model.Par['pMaxCharge'][hs][p,sc,n] and model.Par['pMaxCharge2ndBlock'][hs][p,sc,n]:
            if model.Par['pMinCharge'][hs][p,sc,n] == 0.0:
                return optmodel.vHydTotalCharge[p,sc,n,hs]                                       ==        optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs]
            else:
                return optmodel.vHydTotalCharge[p,sc,n,hs] / model.Par['pMinCharge'][hs][p,sc,n] == optmodel.vHydCommitment[p,sc,n,es] + (optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs]) / model.Par['pMinCharge'][hs][p,sc,n]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydTotalCharge', Constraint(optmodel.psnhs, rule=eHydTotalCharge, doc='total charge of an H2 ESS unit [tH2]'))

    # Incompatibility between charge and outflows use of an ESS [p.u.]
    def eIncompatibilityEleChargeOutflows(optmodel, p,sc,n, es):
        if (p,sc,es) in model.pseso:
            if model.Par['pMaxCharge2ndBlock'][es][p,sc,n]:
                return (optmodel.vEleEnergyOutflows[p,sc,n,es] + optmodel.vEleTotalCharge2ndBlock[p,sc,n,es]) / model.Par['pMaxCharge2ndBlock'][es][p,sc,n] <= 1.0
            else:
                return Constraint.Skip
        else:
            return Constraint.Skip
    optmodel.__setattr__('eIncompatibilityEleChargeOutflows', Constraint(optmodel.psnes, rule=eIncompatibilityEleChargeOutflows, doc='incompatibility between charge and outflows use [p.u.]'))

    # def eIncompatibilityHydChargeOutflows(optmodel, p,sc,n, hs):
    #     if (p,sc,hs) in model.pseso:
    #         if model.Par['pMaxCharge2ndBlock'][hs][p,sc,n]:
    #             return (optmodel.vHydEnergyOutflows[p,sc,n,hs] + optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs]) / model.Par['pMaxCharge2ndBlock'][hs][p,sc,n] <= 1.0
    #         else:
    #             return Constraint.Skip
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eIncompatibilityHydChargeOutflows', Constraint(optmodel.psnhs, rule=eIncompatibilityHydChargeOutflows, doc='incompatibility between charge and outflows use [p.u.]'))

    print('--- Declaring the incompatibility between charge and outflows use:     {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Logical relation between commitment, startup and shutdown status of a committed unit (all except the VRES units) [p.u.]
    def eEleCommitmentStartupShutdown(optmodel, p,sc,n, nr):
        if (model.Par['pMinPower'][nr][p,sc,n] or model.Par['pGenConstantTerm'][nr] or model.Par['pOptIndBinGenMinTime'] == 1) and nr not in model.es:
            if n == model.n.first():
                return optmodel.vGenCommitment[p,sc,n,nr] - model.Par['pInitialUC'][p,sc,nr]                 == optmodel.vGenStartUp[p,sc,n,nr] - optmodel.vGenShutDown[p,sc,n,nr]
            else:
                return optmodel.vGenCommitment[p,sc,n,nr] - optmodel.vGenCommitment[p,sc,model.n.prev(n),nr] == optmodel.vGenStartUp[p,sc,n,nr] - optmodel.vGenShutDown[p,sc,n,nr]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleCommitmentStartupShutdown', Constraint(optmodel.psnnr, rule=eEleCommitmentStartupShutdown, doc='Electricity relation among commitment startup and shutdown'))

    def eEleMaxCommitment(optmodel, p,sc,n, nr):
        if model.Par['pGenMaxCommitment'][nr]:
            return optmodel.vGenCommitment[p,sc,n,nr] <= sum(optmodel.vGenMaxCommitment[p,sc,n2,nr] for n2 in list(model.n2)[(model.n.ord(n)-1):(model.n.ord(n)+23)] if model.n2.ord(n2) % 24 == 0)
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleMaxCommitment', Constraint(optmodel.psnnr, rule=eEleMaxCommitment, doc='Electricity relation among commitment startup and shutdown'))

    def eHydCommitmentStartupShutdown(optmodel, p,sc,n,hz):
        if (model.Par['pMinPower'][hz][p,sc,n] or model.Par['pGenConstantTerm'][hz] or model.Par['pOptIndBinGenMinTime'] == 1) and hz not in model.hs:
            if n == model.n.first():
                return optmodel.vHydCommitment[p,sc,n,hz] - model.Par['pInitialUC'][p,sc,hz]                 == optmodel.vHydStartUp[p,sc,n,hz] - optmodel.vHydShutDown[p,sc,n,hz]
            else:
                return optmodel.vHydCommitment[p,sc,n,hz] - optmodel.vHydCommitment[p,sc,model.n.prev(n),hz] == optmodel.vHydStartUp[p,sc,n,hz] - optmodel.vHydShutDown[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydCommitmentStartupShutdown', Constraint(optmodel.psnhz, rule=eHydCommitmentStartupShutdown, doc='Hydrogen relation among commitment startup and shutdown'))

    print('--- Declaring the logical relation in the unit commitment:             {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Maximum ramp up and ramp down for the second block of a non-renewable (thermal, hydro) unit [p.u.]
    def eMaxRampUpEleOutput(optmodel, p,sc,n, nr):
        if model.Par['pGenRampUp'][nr] and model.Par['pOptIndBinGenRamps'] == 1 and model.Par['pGenRampUp'][nr] < model.Par['pMaxPower2ndBlock'][nr][p,sc,n]:
            if n == model.n.first():
                return (- max(model.Par['pSystemOutput'][p,sc,nr] - model.Par['pMinPower'][nr][p,sc,n],0.0)                                                                                                 + optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] + optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] + optmodel.vEleReserveProd_Up_TR[p,sc,n,nr]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][nr] <=   optmodel.vGenCommitment[p,sc,n,nr] - optmodel.vGenStartUp[p,sc,n,nr]
            else:
                return (- optmodel.vEleTotalOutput2ndBlock[p,sc,model.n.prev(n),nr] - optmodel.vEleReserveProd_Down_SR[p,sc,model.n.prev(n),nr] - optmodel.vEleReserveProd_Down_TR[p,sc,model.n.prev(n),nr] + optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] + optmodel.vEleReserveProd_Up_SR[p,sc,n,nr] + optmodel.vEleReserveProd_Up_TR[p,sc,n,nr]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][nr] <=   optmodel.vGenCommitment[p,sc,n,nr] - optmodel.vGenStartUp[p,sc,n,nr]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampUpEleOutput', Constraint(optmodel.psnnr, rule=eMaxRampUpEleOutput, doc='maximum ramp up   [p.u.]'))

    def eMaxRampDwEleOutput(optmodel, p,sc,n, nr):
        if model.Par['pGenRampDown'][nr] and model.Par['pOptIndBinGenRamps'] == 1 and model.Par['pGenRampDw'][nr] < model.Par['pMaxPower2ndBlock'][nr][p,sc,n]:
            if n == model.n.first():
                return (- max(model.Par['pSystemOutput'][p,sc,nr] - model.Par['pMinPower'][nr][p,sc,n],0.0)                                                                                               + optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] - optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] - optmodel.vEleReserveProd_Down_TR[p,sc,n,nr]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][nr] >= - model.Par['pInitialUC'][p,sc,nr]                 + optmodel.vGenShutDown[p,sc,n,nr]
            else:
                return (- optmodel.vEleTotalOutput2ndBlock[p,sc,model.n.prev(n),nr] + optmodel.vEleReserveProd_Up_SR[p,sc,model.n.prev(n),nr] + optmodel.vEleReserveProd_Up_TR[p,sc,model.n.prev(n),nr]   + optmodel.vEleTotalOutput2ndBlock[p,sc,n,nr] - optmodel.vEleReserveProd_Down_SR[p,sc,n,nr] - optmodel.vEleReserveProd_Down_TR[p,sc,n,nr]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][nr] >= - optmodel.vGenCommitment[p,sc,model.n.prev(n),nr] + optmodel.vGenShutDown[p,sc,n,nr]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampDwEleOutput', Constraint(optmodel.psnnr, rule=eMaxRampDwEleOutput, doc='maximum ramp down [p.u.]'))

    print('--- Declaring the maximum ramp up and ramp down:                       {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Maximum ramp down and ramp up for the charge of an ESS [p.u.]
    def eMaxRampUpEleCharge(optmodel, p,sc,n, es):
        if model.Par['pGenRampUp'][es] and model.Par['pOptIndBinGenRamps'] == 1 and model.Par['pMaxCharge2ndBlock'][es][p,sc,n]:
            if n == model.n.first():
                return (                                                                                                                                                                              optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] - optmodel.vEleReserveCons_Up_SR[p,sc,n,es] - optmodel.vEleReserveCons_Up_TR[p,sc,n,es]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][es] >= - 1.0
            else:
                return (- optmodel.vEleTotalCharge2ndBlock[p,sc,model.n.prev(n),es] + optmodel.vEleReserveCons_Down_SR[p,sc,model.n.prev(n),es] + optmodel.vEleReserveCons_Down_TR[p,sc,model.n.prev(n),es] + optmodel.vESSTotalCharge2ndBlock[p,sc,n,es] - optmodel.vEleReserveCons_Up_SR[p,sc,n,es] - optmodel.vEleReserveCons_Up_TR[p,sc,n,es]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][es] >= - 1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampUpEleCharge', Constraint(optmodel.psnes, rule=eMaxRampUpEleCharge, doc='maximum ramp up   charge [p.u.]'))

    def eMaxRampDwEleCharge(optmodel, p,sc,n, es):
        if model.Par['pGenRampDown'][es] and model.Par['pOptIndBinGenRamps'] == 1 and model.Par['pMaxCharge2ndBlock'][es][p,sc,n]:
            if n == model.n.first():
                return (                                                                                                                                                                          + optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] + optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + optmodel.vEleReserveCons_Down_TR[p,sc,n,es]) / model.Par['pDuration'][n] / model.Par['pGenRampDw'][es] <=   1.0
            else:
                return (- optmodel.vEleTotalCharge2ndBlock[p,sc,model.n.prev(n),es] - optmodel.vEleReserveCons_Up_SR[p,sc,model.n.prev(n),es] - optmodel.vEleReserveCons_Up_TR[p,sc,model.n.prev(n),es]   + optmodel.vEleTotalCharge2ndBlock[p,sc,n,es] + optmodel.vEleReserveCons_Down_SR[p,sc,n,es] + optmodel.vEleReserveCons_Down_TR[p,sc,n,es]) / model.Par['pDuration'][n] / model.Par['pGenRampDw'][es] <=   1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampDwEleCharge', Constraint(optmodel.psnes, rule=eMaxRampDwEleCharge, doc='maximum ramp down charge [p.u.]'))

    print('--- Declaring the maximum ramp down and ramp up for the charge:        {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # maximum ramp up and ramp down for the charge of an H2 producer [p.u.]
    def eMaxRampUpHydOutput(optmodel, p,sc,n, hz):
        if model.Par['pGenRampUp'][hz] > 0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                              optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][hz] <=   optmodel.vHydCommitment[p,sc,n,hz] - optmodel.vHydStartUp[p,sc,n,hz]
            else:
                return (- optmodel.vHydTotalOutput2ndBlock[p,sc,model.n.prev(n),hz] + optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][hz] <=   optmodel.vHydCommitment[p,sc,n,hz] - optmodel.vHydStartUp[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampUpHydOutput', Constraint(optmodel.psnhz, rule=eMaxRampUpHydOutput, doc='maximum ramp up   output [p.u.]'))

    def eMaxRampDwHydOutput(optmodel, p,sc,n, hz):
        if model.Par['pGenRampDown'][hz] > 0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                              optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][hz] >= - model.Par['pInitialUC'][p,sc,hz]                 + optmodel.vHydShutDown[p,sc,n,hz]
            else:
                return (- optmodel.vHydTotalOutput2ndBlock[p,sc,model.n.prev(n),hz] + optmodel.vHydTotalOutput2ndBlock[p,sc,n,hz]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][hz] >= - optmodel.vHydCommitment[p,sc,model.n.prev(n),hz] + optmodel.vHydShutDown[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampDwHydOutput', Constraint(optmodel.psnhz, rule=eMaxRampDwHydOutput, doc='maximum ramp down output [p.u.]'))

    print('--- Declaring the maximum ramp up and ramp down for the H2 output:     {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # maximum ramp up and ramp down for the charge of an H2 ESS [p.u.]
    def eMaxRampUpHydCharge(optmodel, p,sc,n, hs):
        if model.Par['pGenRampUp'][hs] > 0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                              optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][hs] >= - 1.0
            else:
                return (- optmodel.vHydTotalCharge2ndBlock[p,sc,model.n.prev(n),hs] + optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][hs] >= - 1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampUpHydCharge', Constraint(optmodel.psnhs, rule=eMaxRampUpHydCharge, doc='maximum ramp up   charge [p.u.]'))

    def eMaxRampDwHydCharge(optmodel, p,sc,n, hs):
        if model.Par['pGenRampDown'][hs] > 0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                              optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][hs] <=   1.0
            else:
                return (- optmodel.vHydTotalCharge2ndBlock[p,sc,model.n.prev(n),hs] + optmodel.vHydTotalCharge2ndBlock[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][hs] <=   1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampDwHydCharge', Constraint(optmodel.psnhs, rule=eMaxRampDwHydCharge, doc='maximum ramp down charge [p.u.]'))

    print('--- Declaring the maximum ramp up and ramp down for the H2 charge:     {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # maximum ramp up and ramp down for the outflows of an H2 ESS [p.u.]
    def eMaxRampUpHydOutflows(optmodel, p,sc,n, hs):
        if model.Par['pGenRampUp'][hs] > 0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                         optmodel.vHydEnergyOutflows[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][hs] <=   1.0
            else:
                return (- optmodel.vHydEnergyOutflows[p,sc,model.n.prev(n),hs] + optmodel.vHydEnergyOutflows[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampUp'][hs] <=   1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampUpHydOutflows', Constraint(optmodel.psnhs, rule=eMaxRampUpHydOutflows, doc='maximum ramp up   outflows [p.u.]'))

    def eMaxRampDwHydOutflows(optmodel, p,sc,n, hs):
        if model.Par['pGenRampDown'][hs] > 0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                         optmodel.vHydEnergyOutflows[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][hs] >= - 1.0
            else:
                return (- optmodel.vHydEnergyOutflows[p,sc,model.n.prev(n),hs] + optmodel.vHydEnergyOutflows[p,sc,n,hs]) / model.Par['pDuration'][n] / model.Par['pGenRampDown'][hs] >= - 1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMaxRampDwHydOutflows', Constraint(optmodel.psnhs, rule=eMaxRampDwHydOutflows, doc='maximum ramp down outflows [p.u.]'))

    # ramp in the provision of hydrogen to the customer
    def eRampUpHydDemand(optmodel, p,sc,n,nd):
        if model.Par['pParRampDemand'] > 0.0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                         optmodel.vHydTotalDemand   [p,sc,n,nd]) / model.Par['pDuration'][n] / model.Par['pParRampDemand'] <=  1.0
            else:
                return (- optmodel.vHydTotalDemand   [p,sc,model.n.prev(n),nd] + optmodel.vHydTotalDemand   [p,sc,n,nd]) / model.Par['pDuration'][n] / model.Par['pParRampDemand'] <=  1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eRampUpHydDemand', Constraint(optmodel.psnnd, rule=eRampUpHydDemand, doc='maximum ramp up   outflows [p.u.]'))

    def eRampDwHydDemand(optmodel, p,sc,n,nd):
        if model.Par['pParRampDemand'] > 0.0 and model.Par['pOptIndBinGenRamps'] == 1:
            if n == model.n.first():
                return (                                                         optmodel.vHydTotalDemand   [p,sc,n,nd]) / model.Par['pDuration'][n] / model.Par['pParRampDemand'] >= - 1.0
            else:
                return (- optmodel.vHydTotalDemand   [p,sc,model.n.prev(n),nd] + optmodel.vHydTotalDemand   [p,sc,n,nd]) / model.Par['pDuration'][n] / model.Par['pParRampDemand'] >= - 1.0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eRampDwHydDemand', Constraint(optmodel.psnnd, rule=eRampDwHydDemand, doc='maximum ramp down outflows [p.u.]'))

    # Differences between electricity consumption of two consecutive hours [GW]
    def eEleConsumptionDiff(optmodel, p,sc,n,hz):
        if n == model.n.first():
            return                                                      optmodel.vEleTotalCharge[p,sc,n,hz] == optmodel.vEleTotalChargeRampPos[p,sc,n,hz] - optmodel.vEleTotalChargeRampNeg[p,sc,n,hz]
        else:
            return -optmodel.vEleTotalCharge[p,sc,model.n.prev(n),hz] + optmodel.vEleTotalCharge[p,sc,n,hz] == optmodel.vEleTotalChargeRampPos[p,sc,n,hz] - optmodel.vEleTotalChargeRampNeg[p,sc,n,hz]
    optmodel.__setattr__('eEleConsumptionDiff', Constraint(optmodel.psnhz, rule=eEleConsumptionDiff, doc='difference between electricity consumption [GW]'))

    print('--- Declaring the maximum ramp up and ramp down for the H2 outflows:   {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time


    # Minimum up time and down time of thermal unit [h]
    def eMinUpTimeEle(optmodel, p,sc,n,t):
        if model.Par['pOptIndBinGenMinTime'] == 1 and (model.Par['pMinPower'][t][p,sc,n] or model.Par['pGenConstantTerm'][t]) and n not in model.es and model.n.ord(n) > (model.Par['pGenUpTime'][t] - model.Par['pGenUpTimeZero'][t]):
            return sum(optmodel.vGenStartUp[ p,sc,n2,t] for n2 in list(model.n2)[int(max(model.n.ord(n)-model.Par['pGenUpTime'  ][t], max(0,min(model.n.ord(n),(model.Par['pGenUpTime'  ][t] - model.Par['pGenUpTimeZero'  ][t])*(  model.Par['pInitialUC'][p,sc,t]))))):model.n.ord(n)]) <=     optmodel.vGenCommitment[p,sc,n,t]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinUpTimeEle', Constraint(optmodel.psnt, rule=eMinUpTimeEle, doc='minimum up   time [h]'))

    def eMinDownTimeEle(optmodel, p,sc,n,t):
        if model.Par['pOptIndBinGenMinTime'] == 1 and (model.Par['pMinPower'][t][p,sc,n] or model.Par['pGenConstantTerm'][t]) and n not in model.es and model.n.ord(n) > (model.Par['pGenDownTime'][t] - model.Par['pGenDownTimeZero'][t]):
            return sum(optmodel.vGenShutDown[p,sc,n2,t] for n2 in list(model.n2)[int(max(model.n.ord(n)-model.Par['pGenDownTime'][t], max(0,min(model.n.ord(n),(model.Par['pGenDownTime'][t] - model.Par['pGenDownTimeZero'][t])*(1-model.Par['pInitialUC'][p,sc,t]))))):model.n.ord(n)]) <= 1 - optmodel.vGenCommitment[p,sc,n,t]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinDownTimeEle', Constraint(optmodel.psnt, rule=eMinDownTimeEle, doc='minimum down time [h]'))

    # Minimum up time and down time of an electrolyzer [h]
    def eMinUpTimeHyd(optmodel, p,sc,n,hz):
        if model.Par['pOptIndBinGenMinTime'] == 1 and model.Par['pGenUpTime'][hz] > 1 and model.n.ord(n) > (model.Par['pGenUpTime'][hz] - model.Par['pGenUpTimeZero'][hz]):
            return sum(optmodel.vHydStartUp[p,sc,n2,hz] for n2 in list(model.n2)[int(max(model.n.ord(n)-model.Par['pGenUpTime'][hz], max(0,min(model.n.ord(n),(model.Par['pGenUpTime'  ][hz] - model.Par['pGenUpTimeZero'  ][hz])*(  model.Par['pInitialUC'][p,sc,hz]))))):model.n.ord(n)]) <= optmodel.vHydCommitment[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinUpTimeHyd', Constraint(optmodel.psnhz, rule=eMinUpTimeHyd, doc='minimum up   time [h]'))

    def eMinDownTimeHyd(optmodel, p,sc,n,hz):
        if model.Par['pOptIndBinGenMinTime'] == 1 and model.Par['pGenDownTime'][hz] > 1 and model.n.ord(n) > (model.Par['pGenDownTime'][hz] - model.Par['pGenDownTimeZero'][hz]):
            return sum(optmodel.vHydShutDown[p,sc,n2,hz] for n2 in list(model.n2)[int(max(model.n.ord(n)-model.Par['pGenDownTime'][hz], max(0,min(model.n.ord(n),(model.Par['pGenDownTime'][hz] - model.Par['pGenDownTimeZero'][hz])*(1-model.Par['pInitialUC'][p,sc,hz]))))):model.n.ord(n)]) <= 1 - optmodel.vHydCommitment[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eMinDownTimeHyd', Constraint(optmodel.psnhz, rule=eMinDownTimeHyd, doc='minimum down time [h]'))

    print('--- Declaring the minimum up and down time:                            {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # Relationship between hydrogen charge in the HESS and its electricity consumption [GW]
    # def eHydChargeEleConsumption(optmodel, p,sc,n,hs):
    #     if model.Par['pGenMaxCompressorConsumption'][hs]:
    #         return optmodel.vHydCompressorConsumption[p,sc,n,hs] == optmodel.vHydTotalCharge[p,sc,n,hs]/model.Par['pMaxCharge'][hs][p,sc,n] * model.Par['pGenMaxCompressorConsumption'][hs]
    #     else:
    #         return Constraint.Skip
    # optmodel.__setattr__('eHydChargeEleConsumption', Constraint(optmodel.psnhs, rule=eHydChargeEleConsumption, doc='relationship between hydrogen charge and electricity consumption [GW]'))

    # Compressor modeling
    def eCompressorOperStatus(optmodel, p,sc,n,hs):
        if model.Par['pGenMaxCompressorConsumption'][hs]:
            return optmodel.vHydCompressorConsumption[p,sc,n,hs] >= optmodel.vHydTotalOutput[p,sc,n,'AEL_01']/model.Par['pMaxPower']['AEL_01'][p,sc,n] * model.Par['pGenMaxCompressorConsumption'][hs] - 1e3* (1 - optmodel.vHydCompressorOperat[p,sc,n,hs])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eCompressorOperStatus', Constraint(optmodel.psnhs, rule=eCompressorOperStatus, doc='relationship between hydrogen charge and electricity consumption [GW]'))

    def eCompressorOperInventory(optmodel, p,sc,n,hs):
        if model.Par['pGenMaxCompressorConsumption'][hs]:
            return optmodel.vHydInventory[p,sc,n,hs] <= model.Par['pMinStorage'][hs][p,sc,n] + (model.Par['pMaxStorage'][hs][p,sc,n]-model.Par['pMinStorage'][hs][p,sc,n]) * (optmodel.vHydCompressorOperat[p,sc,n,hs])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eCompressorOperInventory', Constraint(optmodel.psnhs, rule=eCompressorOperInventory, doc='relationship between hydrogen charge and electricity consumption [GW]'))

    print('--- Declaring the relationship between hydrogen SoC and compression:   {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    # StanBy status of the electrolyzer
    def eEleStandBy_consumption_UpperBound(optmodel, p,sc,n,hz):
        if model.Par['pGenStandByStatus'][hz]:
            return optmodel.vHydStandByConsumption[p,sc,n,hz] <= model.Par['pGenStandByPower'][hz] * optmodel.vHydStandBy[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleStandBy_consumption_UpperBound', Constraint(optmodel.psnhz, rule=eEleStandBy_consumption_UpperBound, doc='standby consumption of the electrolyzer'))

    def eEleStandBy_consumption_LowerBound(optmodel, p,sc,n,hz):
        if model.Par['pGenStandByStatus'][hz]:
            return optmodel.vHydStandByConsumption[p,sc,n,hz] >= model.Par['pGenStandByPower'][hz] * optmodel.vHydStandBy[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleStandBy_consumption_LowerBound', Constraint(optmodel.psnhz, rule=eEleStandBy_consumption_LowerBound, doc='standby consumption of the electrolyzer'))

    def eEleStandBy_production_UpperBound(optmodel, p,sc,n,hz):
        if model.Par['pGenStandByStatus'][hz]:
            return optmodel.vEleTotalCharge[p,sc,n,hz] <= model.Par['pMaxCharge'][hz][p,sc,n] * (1 - optmodel.vHydStandBy[p,sc,n,hz])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleStandBy_production_UpperBound', Constraint(optmodel.psnhz, rule=eEleStandBy_production_UpperBound, doc='standby charge of the electrolyzer'))

    def eEleStandBy_production_LowerBound(optmodel, p,sc,n,hz):
        if model.Par['pGenStandByStatus'][hz]:
            return optmodel.vEleTotalCharge[p,sc,n,hz] >= model.Par['pMinCharge'][hz][p,sc,n] * (1 - optmodel.vHydStandBy[p,sc,n,hz])
        else:
            return Constraint.Skip
    optmodel.__setattr__('eEleStandBy_production_LowerBound', Constraint(optmodel.psnhz, rule=eEleStandBy_production_LowerBound, doc='standby charge of the electrolyzer'))

    def eHydAvoidTransition_Off_StandBy(optmodel, p,sc,n,hz):
        if model.Par['pGenStandByStatus'][hz]:
            # return 1 - optmodel.vHydCommitment[p,sc,n,hz] + optmodel.vHydStandBy[p,sc,n,hz] <= 1
            return  optmodel.vHydStandBy[p,sc,n,hz] <= optmodel.vHydCommitment[p,sc,n,hz]
        else:
            return Constraint.Skip
    optmodel.__setattr__('eHydAvoidTransition_Off_StandBy', Constraint(optmodel.psnhz, rule=eHydAvoidTransition_Off_StandBy, doc='transition avoid from off to standby'))

    print('--- Declaring the standby status of the electrolyzer:                  {} seconds'.format(round(time.time() - StartTime)))
    StartTime = time.time() # to compute elapsed time

    def eKirchhoff2ndLaw(optmodel,p,sc,n,ni,nf,cc):
        if model.Par[('pOptIndBinSingleNode')] == 0 and model.Par['pEleNetInitialPeriod'][ni,nf,cc] <= model.Par['pParEconomicBaseYear'] and model.Par['pEleNetFinalPeriod'][ni,nf,cc] >= model.Par['pParEconomicBaseYear'] and (ni,nf,cc) in model.elea:
            return optmodel.vEleNetFlow[p,sc,n,ni,nf,cc] / model.Par['pEleNetTTC'][ni,nf,cc] - (optmodel.vEleNetTheta[p,sc,n,ni] - optmodel.vEleNetTheta[p,sc,n,nf]) / model.Par['pEleNetReactance'][ni,nf,cc] / model.Par['pEleNetTTC'][ni,nf,cc] * 0.1 == 0
        else:
            return Constraint.Skip
    optmodel.__setattr__('eKirchhoff2ndLaw', Constraint(optmodel.psnela, rule=eKirchhoff2ndLaw, doc='Kirchhoff 1st Law'))

    print('--- Declaring the Kirchhoff 2nd Law:                                   {} seconds'.format(round(time.time() - StartTime)))

    return model

def solving_model(DirName, CaseName, SolverName, optmodel, pWriteLP):
    # start time
    StartTime = time.time()

    # defining the path
    _path = os.path.join(DirName, CaseName)

    if pWriteLP == 1:
        # %% solving the problem
        optmodel.write(_path + '/oH_' + CaseName + '.lp', io_options={'symbolic_solver_labels': True})  # create lp-format file
        WritingLPTime = time.time() - StartTime
        StartTime = time.time()
        print('Writing LP file                       ... ', round(WritingLPTime), 's')

    Solver = SolverFactory(SolverName)  # select solver
    if SolverName == 'gurobi':
        Solver.options['LogFile'] = _path + '/oH_' + CaseName + '.log'
        # Solver.options['IISFile'      ] = _path+'/oH_'+CaseName+'.ilp'                   # should be uncommented to show results of IIS
        # Solver.options['Method'       ] = 2                                             # barrier method
        Solver.options['Method'] = 2  # barrier method
        Solver.options['MIPFocus'] = 1
        Solver.options['Presolve'] = 2
        Solver.options['RINS'] = 100
        Solver.options['Crossover'] = -1
        Solver.options['FeasibilityTol'] = 1e-9
        # Solver.options['BarConvTol'    ] = 1e-9
        # Solver.options['BarQCPConvTol' ] = 0.025
        # Solver.options['NumericFocus'  ] = 3
        Solver.options['MIPGap'] = 0.01
        Solver.options['Threads'] = int((psutil.cpu_count(logical=True) + psutil.cpu_count(logical=False)) / 2)
        Solver.options['TimeLimit'] = 1800
        Solver.options['IterationLimit'] = 1800000
    idx = 0
    for var in optmodel.component_data_objects(Var, active=False, descend_into=True):
        if not var.is_continuous():
            idx += 1
    if idx == 0:
        optmodel.dual = Suffix(direction=Suffix.IMPORT)
        optmodel.rc = Suffix(direction=Suffix.IMPORT)
    SolverResults = Solver.solve(optmodel, tee=True)  # tee=True displays the output of the solver
    print('Termination condition: ', SolverResults.solver.termination_condition)
    SolverResults.write()  # summary of the solver results

    # %% fix values of binary variables to get dual variables and solve it again
    print('# ============================================================================= #')
    print('# ============================================================================= #')
    idx = 0
    for var in optmodel.component_data_objects(Var, active=True, descend_into=True):
        if not var.is_continuous():
            print("fixing: " + str(var))
            var.fixed = True  # fix the current value
            idx += 1
    print("Number of fixed variables: ", idx)
    print('# ============================================================================= #')
    print('# ============================================================================= #')
    if idx != 0:
        optmodel.del_component(optmodel.dual)
        optmodel.del_component(optmodel.rc)
        optmodel.dual = Suffix(direction=Suffix.IMPORT)
        optmodel.rc = Suffix(direction=Suffix.IMPORT)
        SolverResults = Solver.solve(optmodel, tee=False)  # tee=True displays the output of the solver
        SolverResults.write()  # summary of the solver results

    SolvingTime = time.time() - StartTime
    print('Solving                               ... ', round(SolvingTime), 's')

    print('Objective function value                  ', round(optmodel.eTotalSCost.expr(), 2), 'M€')

    return optmodel

def OutputVariablesToCSV(DirName, CaseName, SolverName, model, optmodel):

    _path = os.path.join(DirName, CaseName)
    StartTime = time.time()

    # for v in optmodel.component_objects(Var, active=True):
    #     DF = pd.Series([v[index]() for index in v], index=pd.Index(list(v.index_set())), dtype='float64').to_frame(name=v.name)
    #     DF = DF.reset_index()
    #     DF.to_csv(_path+'/oH_Result_'+v.name+'_'+CaseName+'.csv', index=False, sep=',')

    for var in optmodel.component_objects(Var, active=True):
        with open(_path+'/oH_Result_'+var.name+'_'+CaseName+'.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Index', 'Value', 'Lower Bound', 'Upper Bound'])
            var_object = getattr(optmodel, str(var))
            for index in var_object:
                writer.writerow([str(var), index, var_object[index].value, str(var_object[index].lb), str(var_object[index].ub)])

    # Extract and write parameters from the case
    for par in optmodel.component_objects(Param):
        with open(_path+'/oH_Result_'+par.name+'_'+CaseName+'.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Index', 'Value'])
            par_object = getattr(optmodel, str(par))
            if par_object.is_indexed():
                for index in par_object:
                    if (isinstance(index, tuple) and par_object.mutable == False) or par_object.mutable == False:
                        writer.writerow([str(par), index, par_object[index]])
                    else:
                        writer.writerow([str(par), index, par_object[index].value])
            else:
                writer.writerow        ([str(par), 'NA',  par_object.value])

    # Extract and write dual variables
    for con in optmodel.component_objects(Constraint, active=True):
        with open(_path+'/oH_Result_'+con.name+'_'+CaseName+'.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Index', 'Value', 'Lower Bound', 'Upper Bound'])
            con_object = getattr(optmodel, str(con))
            if con.is_indexed():
                for index in con_object:
                    writer.writerow([str(con), index, model.dual[con_object[index]], str(con_object[index].lb), str(con_object[index].ub)])

    SavingDataTime = time.time() - StartTime
    print('Output variable to CSV file                     ... ', round(SavingDataTime), 's')

    return model

def saving_results(DirName, CaseName, SolverName, model, optmodel):

    # Definition of Area plots
    def AreaPlots(period,scenario, df, Category, X, Y, OperationType):
        Results = df.loc[period,scenario,:,:]
        Results = Results.reset_index().rename(columns={'level_0': X, 'level_1': Category, 0: Y})
        # Change the format of the LoadLevel
        Results[X] = Results[X].str[:14]
        Results[X] = (Results[X]+'+01:00')
        Results[X] = (str(period)+'-'+Results[X])
        Results[X] = pd.to_datetime(Results[X])
        Results[X] = Results[X].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Composed Names
        C_C = Category+':N'

        C_X = X+':T'
        C_Y = Y+':Q'
        # Define and build the chart
        # alt.data_transformers.enable('json')
        alt.data_transformers.disable_max_rows()
        interval = alt.selection_interval(encodings=['x'])
        selection = alt.selection_point(fields=[Category], bind='legend')

        base  = alt.Chart(Results).mark_area().encode(x=alt.X(C_X, axis=alt.Axis(title='')), y=alt.Y(C_Y, axis=alt.Axis(title=Y)), color=alt.Color(C_C, scale=alt.Scale(scheme='category20c')), opacity=alt.condition(selection, alt.value(1), alt.value(0.2))).add_params(selection)
        chart = base.encode(alt.X(C_X, axis=alt.Axis(title='')).scale(domain=interval)).properties(width=1200, height=450)
        view  = base.add_params(interval).properties(width=1200, height=50)
        plot  = alt.vconcat(chart, view)

        return plot

    _path = os.path.join(DirName, CaseName)
    StartTime = time.time()
    print('Objective function value                  ', model.eTotalSCost.expr())

    # components of the objective function
    OutputResults1 = pd.Series(data=[ optmodel.vTotalMCost     [p,sc,n]()*model.Par['pDuration'][n] for p,sc,n in model.psn], index=pd.Index(model.psn)).to_frame(name='TotalMCost'     )
    OutputResults2 = pd.Series(data=[ optmodel.vTotalGCost     [p,sc,n]()*model.Par['pDuration'][n] for p,sc,n in model.psn], index=pd.Index(model.psn)).to_frame(name='TotalGCost'     )
    OutputResults3 = pd.Series(data=[ optmodel.vTotalECost     [p,sc,n]()*model.Par['pDuration'][n] for p,sc,n in model.psn], index=pd.Index(model.psn)).to_frame(name='TotalECost'     )
    OutputResults4 = pd.Series(data=[ optmodel.vTotalCCost     [p,sc,n]()*model.Par['pDuration'][n] for p,sc,n in model.psn], index=pd.Index(model.psn)).to_frame(name='TotalCCost'     )
    OutputResults5 = pd.Series(data=[-optmodel.vTotalRCost     [p,sc,n]()*model.Par['pDuration'][n] for p,sc,n in model.psn], index=pd.Index(model.psn)).to_frame(name='TotalRCost'     )
    OutputResults  = pd.concat([OutputResults1, OutputResults2, OutputResults3, OutputResults4, OutputResults5], axis=1)

    OutputResults.stack().rename_axis(['Period', 'Scenario', 'LoadLevel', 'Component'], axis=0).reset_index().rename(columns={0: 'MEUR'}, inplace=False).to_csv(_path+'/oH_Result_TotalCost_'+CaseName+'.csv', index=False, sep=',')

    # %% outputting the electrical energy balance
    #%%  Power balance per period, scenario, and load level
    # incoming and outgoing lines (lin) (lout)
    lin   = defaultdict(list)
    lout  = defaultdict(list)
    for ni,nf,cc in model.ela:
        lin  [nf].append((ni,cc))
        lout [ni].append((nf,cc))

    hin   = defaultdict(list)
    hout  = defaultdict(list)
    for ni,nf,cc in model.hpa:
        hin  [nf].append((ni,cc))
        hout [ni].append((nf,cc))

    sPNND   = [(p,sc,n,nd)    for p,sc,n,nd    in model.psn*model.nd]
    sPNNDGT = [(p,sc,n,nd,gt) for p,sc,n,nd,gt in sPNND*model.gt   ]

    OutputResults1     = pd.Series(data=[ sum(optmodel.vEleTotalOutput          [p,sc,n,g       ]() * model.Par['pDuration'][n] for g  in model.g  if (nd,g ) in model.n2g and (gt,g ) in model.t2g) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='Generation'        ).reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='Generation' )
    OutputResults2     = pd.Series(data=[-sum(optmodel.vEleTotalCharge          [p,sc,n,es      ]() * model.Par['pDuration'][n] for es in model.eh if (nd,es) in model.n2g and (gt,es) in model.t2g) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='ConsumptionEleESS' ).reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='ConsumptionEleESS')
    OutputResults3     = pd.Series(data=[-sum(optmodel.vEleTotalCharge          [p,sc,n,es      ]() * model.Par['pDuration'][n] for es in model.eh if (nd,es) in model.n2h and (gt,es) in model.t2h) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='ConsumptionEle2Hyd').reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='ConsumptionEle2Hyd')
    OutputResults4     = pd.Series(data=[-sum(optmodel.vHydCompressorConsumption[p,sc,n,hs      ]() * model.Par['pDuration'][n] for hs in model.he if (nd,hs) in model.n2h and (gt,hs) in model.t2h) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='CompressorConsumpt').reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='CompressorConsumpt')
    OutputResults5     = pd.Series(data=[-sum(optmodel.vHydStandByConsumption   [p,sc,n,es      ]() * model.Par['pDuration'][n] for es in model.eh if (nd,es) in model.n2h and (gt,es) in model.t2h) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='StandByConsumption').reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='StandByConsumption')
    OutputResults6     = pd.Series(data=[     optmodel.vENS                     [p,sc,n,nd      ]() * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='ENS'               )
    OutputResults7     = pd.Series(data=[-       model.Par['pElectricityDemand'][nd][p,sc,n     ]   * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='ElectricityDemand' )
    OutputResults8     = pd.Series(data=[     optmodel.vElectricityBuy          [p,sc,n,nd      ]() * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='ElectricityBuy'    )
    OutputResults9     = pd.Series(data=[-    optmodel.vElectricitySell         [p,sc,n,nd      ]() * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='ElectricitySell'   )
    OutputResults10    = pd.Series(data=[-sum(optmodel.vEleNetFlow              [p,sc,n,nd,nf,cc]() * model.Par['pDuration'][n] for (nf,cc) in lout [nd])                                            for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='PowerFlowOut'      )
    OutputResults11    = pd.Series(data=[ sum(optmodel.vEleNetFlow              [p,sc,n,ni,nd,cc]() * model.Par['pDuration'][n] for (ni,cc) in lin  [nd])                                            for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='PowerFlowIn'       )
    OutputResults  = pd.concat([OutputResults1, OutputResults2, OutputResults3, OutputResults4, OutputResults5, OutputResults6, OutputResults7, OutputResults8, OutputResults9, OutputResults10, OutputResults11], axis=1)

    OutputResults.stack().rename_axis(['Period', 'Scenario', 'LoadLevel', 'Node', 'Technology'], axis=0).reset_index().rename(columns={0: 'GWh'}, inplace=False).to_csv(_path+'/oH_Result_ElectricityBalance_'+CaseName+'.csv', index=False, sep=',')

    print('Outputting the electrical energy balance ... ', round(time.time() - StartTime), 's')

    # %% outputting the hydrogen energy balance
    #%%  Hydrogen balance per period, scenario, and load level
    OutputResults1     = pd.Series(data=[ sum(optmodel.vHydTotalOutput           [p,sc,n,h       ]() * model.Par['pDuration'][n] for h  in model.h  if (nd,h ) in model.n2h and (gt,h ) in model.t2h) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='Generation'        ).reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='Generation'        , aggfunc='sum')
    OutputResults2     = pd.Series(data=[-sum(optmodel.vHydTotalCharge           [p,sc,n,hs      ]() * model.Par['pDuration'][n] for hs in model.he if (nd,hs) in model.n2h and (gt,hs) in model.t2h) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='ConsumptionHydESS' ).reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='ConsumptionHydESS')
    OutputResults3     = pd.Series(data=[-sum(optmodel.vHydTotalCharge           [p,sc,n,hs      ]() * model.Par['pDuration'][n] for hs in model.he if (nd,hs) in model.n2g and (gt,hs) in model.t2g) for p,sc,n,nd,gt in sPNNDGT], index=pd.Index(sPNNDGT)).to_frame(name='ConsumptionHyd2Ele').reset_index().pivot_table(index=['level_0','level_1','level_2','level_3'], columns='level_4', values='ConsumptionHyd2Ele')
    OutputResults4     = pd.Series(data=[     optmodel.vHNS                      [p,sc,n,nd      ]() * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='HNS'               )
    OutputResults5     = pd.Series(data=[-    optmodel.vHydTotalDemand           [p,sc,n,nd      ]() * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='HydrogenDemand'    )
    OutputResults6     = pd.Series(data=[     optmodel.vHydrogenBuy              [p,sc,n,nd      ]() * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='HydrogenBuy'       )
    OutputResults7     = pd.Series(data=[-    optmodel.vHydrogenSell             [p,sc,n,nd      ]() * model.Par['pDuration'][n]                                                                      for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='HydrogenSell'      )
    OutputResults8     = pd.Series(data=[-sum(optmodel.vHydNetFlow               [p,sc,n,nd,nf,cc]() * model.Par['pDuration'][n] for (nf,cc) in hout [nd])                                            for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='HydrogenFlowOut'   )
    OutputResults9     = pd.Series(data=[ sum(optmodel.vHydNetFlow               [p,sc,n,ni,nd,cc]() * model.Par['pDuration'][n] for (ni,cc) in hin  [nd])                                            for p,sc,n,nd    in sPNND  ], index=pd.Index(sPNND  )).to_frame(name='HydrogenFlowIn'    )
    OutputResults  = pd.concat([OutputResults1, OutputResults2, OutputResults3, OutputResults4, OutputResults5, OutputResults6, OutputResults7, OutputResults8, OutputResults9], axis=1)

    OutputResults.stack().rename_axis(['Period', 'Scenario', 'LoadLevel', 'Node', 'Technology'], axis=0).reset_index().rename(columns={0: 'tH2'}, inplace=False).to_csv(_path+'/oH_Result_HydrogenBalance_'+CaseName+'.csv', index=False, sep=',')

    sPSNGT       = [(p,sc,n,gt) for p,sc,n,gt in model.psngt if sum(1 for g in model.g if (gt,g) in model.t2g) > 0]
    OutputToFile = pd.Series(data=[sum(optmodel.vEleTotalOutput[p,sc,n,g]() for g in model.g if (gt,g) in model.t2g) for p,sc,n,gt in sPSNGT], index=pd.Index(sPSNGT))
    OutputToFile *= 1e3
    OutputToFile.to_frame(name='MW').reset_index().pivot_table(index=['level_0','level_1','level_2'], columns='level_3', values='MW', aggfunc='sum').rename_axis(['Period', 'Scenario', 'LoadLevel'], axis=0).rename_axis([None], axis=1).to_csv(_path+'/oT_Result_TechnologyGeneration_'+CaseName+'.csv', sep=',')

    # TechnologyOutput = OutputToFile.loc[:,:,:,:]
    # for p,sc in model.ps:
    #     chart = AreaPlots(p,sc, TechnologyOutput, 'Technology', 'LoadLevel', 'MW', 'sum')
    #     chart.save(_path+'/oH_Plot_TechnologyOutput_'+str(p)+'_'+CaseName+'.html', embed_options={'renderer': 'svg'})

    # saving the results of the electricity network flows
    OutputResults = pd.Series(data=[optmodel.vEleNetFlow[p,sc,n,ni,nf,cc]() for p,sc,n,ni,nf,cc in model.psnela], index=pd.Index(model.psnela)).to_frame(name='MW').rename_axis(['Period', 'Scenario', 'LoadLevel', 'InitialNode', 'FinalNode', 'Circuit'], axis=0).reset_index()
    OutputResults.to_csv(_path+'/oH_Result_ElectricityNetworkFlows_'+CaseName+'.csv', index=False, sep=',')

    # saving the results of the hydrogen network flows
    OutputResults = pd.Series(data=[optmodel.vHydNetFlow[p,sc,n,ni,nf,cc]() for p,sc,n,ni,nf,cc in model.psnhpa], index=pd.Index(model.psnhpa)).to_frame(name='MW').rename_axis(['Period', 'Scenario', 'LoadLevel', 'InitialNode', 'FinalNode', 'Circuit'], axis=0).reset_index()
    OutputResults.to_csv(_path+'/oH_Result_HydrogenNetworkFlows_'+CaseName+'.csv', index=False, sep=',')

    # saving the reserves offers
    if len(model.psnes) > 0:
        data = []
        OutputResults1 = pd.Series(data=[optmodel.vEleReserveCons_Up_SR[p,sc,n,es]()   for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveCons_Up_SR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults1)
        OutputResults2 = pd.Series(data=[optmodel.vEleReserveCons_Up_TR[p,sc,n,es]()   for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveCons_Up_TR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults2)
        OutputResults3 = pd.Series(data=[optmodel.vEleReserveCons_Down_SR[p,sc,n,es]() for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveCons_Down_SR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults3)
        OutputResults4 = pd.Series(data=[optmodel.vEleReserveCons_Down_TR[p,sc,n,es]() for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveCons_Down_TR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults4)
        OutputResults5 = pd.Series(data=[optmodel.vEleReserveProd_Up_SR[p,sc,n,es]()   for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveProd_Up_SR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults5)
        OutputResults6 = pd.Series(data=[optmodel.vEleReserveProd_Up_TR[p,sc,n,es]()   for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveProd_Up_TR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults6)
        OutputResults7 = pd.Series(data=[optmodel.vEleReserveProd_Down_SR[p,sc,n,es]() for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveProd_Down_SR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults7)
        OutputResults8 = pd.Series(data=[optmodel.vEleReserveProd_Down_TR[p,sc,n,es]() for p,sc,n,es in model.psnes], index=pd.Index(model.psnes)).to_frame(name='vEleReserveProd_Down_TR').rename_axis(['Period', 'Scenario', 'LoadLevel', 'Unit'], axis=0)
        data.append(OutputResults8)
        OutputResults = pd.concat(data, axis=1)
        OutputResults.reset_index().to_csv(_path+'/oH_Result_ReservesOffers_'+CaseName+'.csv', index=False, sep=',')

    return model

def network_map(DirName, CaseName, model, optmodel):
    # %% plotting the network in a map
    _path = os.path.join(DirName, CaseName)
    DIR   = os.path.dirname(__file__)
    StartTime = time.time()

    # Sub functions
    def make_series(_var, _sets, _factor):
        return pd.Series(data=[_var[p,sc,n,ni,nf,cc]()*_factor for p,sc,n,ni,nf,cc in _sets], index=pd.Index(list(_sets)))

    def selecting_data(p,sc,n):
        # Nodes data
        pio.renderers.default = 'chrome'

        loc_df = pd.Series(data=[model.Par['pNodeLat'][i] for i in model.nd], index=model.nd).to_frame(name='Lat')
        loc_df['Lon'   ] =  0.0
        loc_df['Zone'  ] =  '0.0'
        loc_df['Demand'] =  0.0
        loc_df['Size'  ] = 15.0

        for nd,zn in model.ndzn:
            loc_df['Lon'   ][nd] = model.Par['pNodeLon'][nd]
            # warnings
            loc_df['Zone'  ][nd] = zn
            loc_df['Demand'][nd] = model.Par['pElectricityDemand'][nd][p,sc,n]*1e3

        # loc_df = loc_df.reset_index().rename(columns={'Type': 'Scenario'}, inplace=False)
        loc_df = loc_df.reset_index()

        # Edges data
        OutputToFile = make_series(optmodel.vEleNetFlow, model.psnela, 1e3)
        OutputToFile.index.names = ['Period', 'Scenario', 'LoadLevel', 'InitialNode', 'FinalNode', 'Circuit']
        OutputToFile = OutputToFile.to_frame(name='MW')

        # tolerance to consider avoid division by 0
        pEpsilon = 1e-6

        line_df = pd.DataFrame(data={'NTCFrw': pd.Series(data=[model.Par['pEleNetTTC'   ][i] * 1e3 + pEpsilon for i in model.ela], index=model.ela),
                                     'NTCBck': pd.Series(data=[model.Par['pEleNetTTCBck'][i] * 1e3 + pEpsilon for i in model.ela], index=model.ela)}, index=model.ela)
        line_df['vFlow'      ] = 0.0
        line_df['utilization'] = 0.0
        line_df['color'      ] = '0.0'
        line_df['voltage'    ] = 0.0
        line_df['width'      ] = 0.0
        line_df['lon'        ] = 0.0
        line_df['lat'        ] = 0.0
        line_df['ni'         ] = '0.0'
        line_df['nf'         ] = '0.0'
        line_df['cc'         ] = 0.0

        line_df = line_df.groupby(level=[0,1]).sum(numeric_only=False)
        ncolors = 11
        colors = list(Color('lightgreen').range_to(Color('darkred'), ncolors))
        colors = ['rgb'+str(x.rgb) for x in colors]

        for ni,nf,cc in model.ela:
            line_df['vFlow'      ][ni,nf] += OutputToFile['MW'][p,sc,n,ni,nf,cc]
            line_df['utilization'][ni,nf]  = max(line_df['vFlow'][ni,nf]/line_df['NTCFrw'][ni,nf],-line_df['vFlow'][ni,nf]/line_df['NTCBck'][ni,nf])*100.0
            line_df['lon'        ][ni,nf]  = (model.Par['pNodeLon'][ni]+model.Par['pNodeLon'][nf]) * 0.5
            line_df['lat'        ][ni,nf]  = (model.Par['pNodeLat'][ni]+model.Par['pNodeLat'][nf]) * 0.5
            # warnings
            line_df['ni'         ][ni,nf]  = ni
            # warnings
            line_df['nf'         ][ni,nf]  = nf
            line_df['cc'         ][ni,nf] += 1

            for i in range(len(colors)):
                if 10*i <= line_df['utilization'][ni,nf] <= 10*(i+1):
                    line_df['color'][ni,nf] = colors[i]

            line_df['voltage'][ni,nf] = model.Par['pEleNetVoltage'][ni,nf,cc]
            if   700 < line_df['voltage'][ni,nf] <= 900:
                line_df['width'][ni,nf] = 5
            elif 500 < line_df['voltage'][ni,nf] <= 700:
                line_df['width'][ni,nf] = 4
            elif 350 < line_df['voltage'][ni,nf] <= 500:
                line_df['width'][ni,nf] = 3.5
            elif 290 < line_df['voltage'][ni,nf] <= 350:
                line_df['width'][ni,nf] = 3
            elif 200 < line_df['voltage'][ni,nf] <= 290:
                line_df['width'][ni,nf] = 2.5
            elif  50 < line_df['voltage'][ni,nf] <= 200:
                line_df['width'][ni,nf] = 2
            else:
                line_df['width'][ni,nf] = 1.5

        # Rounding to decimals
        line_df = line_df.round(decimals=2)

        return loc_df, line_df

    p  = list(model.p)[0]
    sc = list(model.sc)[0]
    n  = list(model.n)[0]

    loc_df, line_df = selecting_data(p,sc,n)

    # Making the network
    # Get node position dict
    x, y = loc_df['Lon'].values, loc_df['Lat'].values
    pos_dict = {}
    for index, iata in enumerate(loc_df['index']):
        pos_dict[iata] = (x[index], y[index])

    # Setting up the figure
    token = open(DIR+'/oHySTEM.mapbox_token').read()

    fig = go.Figure()

    # Add edges
    for ni,nf,cc in model.ela:
        fig.add_trace(go.Scattermapbox(lon=[pos_dict[ni][0], pos_dict[nf][0]], lat=[pos_dict[ni][1], pos_dict[nf][1]], mode='lines', line=dict(width=line_df['width'][ni,nf], color=line_df['color'][ni,nf]), opacity=1, hoverinfo='text', textposition='middle center',))

    # Add legends related to the lines
    fig.add_trace(go.Scattermapbox(lat=line_df['lat'], lon=line_df['lon'], mode='markers', marker=go.scattermapbox.Marker(size=20, sizeref=1.1, sizemode='area', color='LightSteelBlue',), opacity=0, hoverinfo='text', text='<br>Line: '+line_df['ni']+' → '+line_df['nf']+'<br># circuits: '+line_df['cc'].astype(str)+'<br>NTC Forward: '+line_df['NTCFrw'].astype(str)+'<br>NTC Backward: '+line_df['NTCBck'].astype(str)+'<br>Power flow: '+line_df['vFlow'].astype(str)+'<br>Utilization [%]: '+line_df['utilization'].astype(str),))

    # Add nodes
    fig.add_trace(go.Scattermapbox(lat=loc_df['Lat'], lon=loc_df['Lon'], mode='markers', marker=go.scattermapbox.Marker(size=loc_df['Size']*10, sizeref=1.1, sizemode='area', color='DarkBlue',), opacity=1, hoverinfo='text', text='<br>Node: ' + loc_df['index'] + '<br>[Lon, Lat]: ' + '(' + loc_df['Lon'].astype(str) + ', ' + loc_df['Lat'].astype(str) + ')' + '<br>Zone: ' + loc_df['Zone'] + '<br>Demand: ' + loc_df['Demand'].astype(str) + ' MW',))

    # Setting up the layout
    fig.update_layout(title={'text': 'Power Network: '+CaseName+'<br>Period: '+str(p)+'; LoadLevel: '+n, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, font=dict(size=14), hovermode='closest', geo=dict(projection_type='azimuthal equal area', showland=True,), mapbox=dict(style='open-street-map', accesstoken=token, bearing=0, center=dict(lat=(loc_df['Lat'].max()+loc_df['Lat'].min())*0.5, lon=(loc_df['Lon'].max()+loc_df['Lon'].min())*0.5), pitch=0, zoom=5), showlegend=False,)

    # Saving the figure
    fig.write_html(_path+'/oH_Plot_MapNetwork_'+CaseName+'.html')

    PlottingNetMapsTime = time.time() - StartTime
    print('Plotting  electric network maps        ... ', round(PlottingNetMapsTime), 's')


if __name__ == '__main__':
    main(oHySTEM)