.. oHySEM documentation master file, created by Erik Alvarez

----------
Input Data
----------

Electric System Input Data
==========================

All the input files must be located in a folder with the name of the case study.

Acronyms
--------

==========  ====================================================================
Acronym     Description
==========  ====================================================================
aFRR        Automatic Frequency Restoration Reserve
AWE         Alkaline Water Electrolyzer
BESS        Battery Energy Storage System
CCGT        Combined Cycle Gas Turbine
EFOR        Equivalent Forced Outage Rate
ENS         Energy Not Served
ESS         Energy Storage System
mFRR        Manual Frequency Restoration Reserve
H2          Hydrogen
HNS         Hydrogen Not Served
OCGT        Open Cycle Gas Turbine
PHS         Pumped-Hydro Storage
PNS         Power Not Served
PV          Photovoltaics
RR          Replacement Reserve
VRE         Variable Renewable Energy
VRES        Variable Renewable Energy Source
==========  ====================================================================

Dictionaries. Sets
------------------
The dictionaries include all the possible elements of the corresponding sets in the optimization problem. **You can't use non-English characters (e.g., ó, º)**

=============================  ===================================================================================================================================================================================================================
File                           Description
=============================  ===================================================================================================================================================================================================================
``oH_Dict_Period.csv``         Period (e.g., 0, 1, 2). **It must be a positive integer equivalent to hours**
``oH_Dict_Scenario.csv``       Scenario. Short-term uncertainties (scenarios) (e.g., s001 to s100)
``oH_Dict_Stage.csv``          Stage
``oH_Dict_LoadLevel.csv``      Load level (e.g., 01-01 00:00:00+01:00 to 01-01 00:45:00+01:00). Load levels with duration 0 are ignored
``oH_Dict_Generation.csv``     Generation units (thermal -nuclear, CCGT, OCGT, coal-, ESS -hydro, pumped-hydro storage PHS, battery BESS, electric vehicle EV, demand response DR, alkaline water electrolyzer AWE, solar thermal- and VRE -wind onshore and offshore, solar PV, run-of-the-river hydro-)
``oH_Dict_Technology.csv``     Generation technologies. The technology order is used in the temporal result plot.
``oH_Dict_Storage.csv``        ESS storage type (daily < 12 h, weekly < 40 h, monthly > 60 h)
=============================  ===================================================================================================================================================================================================================

Input files
-----------
This is the list of the input data files and their brief description.

=======================================  ==========================================================================================================
File                                        Description
=======================================  ==========================================================================================================
``oH_Data_Option.csv``                   Options of use of the **oHySEM** model
``oH_Data_Parameter.csv``                General system parameters
``oH_Data_Period.csv``                   Weight of each period
``oH_Data_Duration.csv``                 Duration of the load levels
``oH_Data_Scenario.csv``                 Short-term uncertainties
``oH_Data_Demand.csv``                   Demand
``oH_Data_EnergyCostPrice.csv``          Cost of the energy bought and price of the energy sold
``oH_Data_OperatingReserve.csv``         Upward and downward operating reserves (include aFRR, mFRR and RR for electricity balancing from ENTSO-E)
``oH_Data_OperatingReservePrice.csv``    Price of the operating reserve sold
``oH_Data_Generation.csv``               Generation data
``oH_Data_EnergyInflows.csv``            Energy inflows  for ESS (e.g., storage hydro or open-loop pumped-storage hydro) by load level
``oH_Data_VariableMinOutflows.csv``      Minimum product outflows for ESS (e.g., kgH2) by load level
``oH_Data_VariableMaxOutflows.csv``      Maximum product outflows for ESS (e.g., kgH2) by load level
``oH_Data_VariableMaxGeneration.csv``    Variable maximum power generation  by load level
``oH_Data_VariableMinGeneration.csv``    Variable minimum power generation  by load level
``oH_Data_VariableMaxConsumption.csv``   Variable maximum power consumption by load level
``oH_Data_VariableMinConsumption.csv``   Variable minimum power consumption by load level
``oH_Data_VariableMaxStorage.csv``       Variable maximum storage           by load level
``oH_Data_VariableMinStorage.csv``       Variable minimum storage           by load level
=======================================  ==========================================================================================================

In any input file, only the columns indicated in this document will be read. For example, you can add a column for comments or additional information as needed, but it will not be read by the model.

Options
----------
A description of the options included in the file ``oH_Data_Option.csv`` follows:

===================  ===============================================================   ====================================================
File                 Description
===================  ===============================================================   ====================================================
IndActIntraDay       Indicator of activation of the intra-day decisions                {0 deactivation, 1 activation}
===================  ===============================================================   ====================================================

If the investment decisions are ignored (IndBinGenInvest, IndBinGenRetirement, and IndBinNetInvest take value 2) or there are no investment decisions, all the scenarios with a probability > 0 are solved sequentially (assuming a probability 1) and the periods are considered with a weight 1.

Parameters
----------
A description of the system parameters included in the file ``oH_Data_Parameter.csv`` follows:

==================  =============================================================================================  ================
File                Description
==================  =============================================================================================  ================
ENSCost             Cost of energy not served. Cost of load curtailment. Value of Lost Load (VoLL)                 €/MWh
HNSCost             Cost of hydrogen not served (HNS)                                                              €/kgH2
PNSCost             Cost of power not served (PNS) associated with the deficit in operating reserve by load level  €/MW
CO2Cost             Cost of CO2 emissions                                                                          €/tCO2
Sbase               Base power used in the DCPF                                                                    MW
TimeStep            Duration of the time step for the load levels (hourly, bi-hourly, trihourly, etc.)             h
EconomicBaseYear    Base year for economic parameters affected by the discount rate                                year
AnnualDiscountRate  Annual discount rate                                                                           p.u.
==================  =============================================================================================  ================

A time step greater than one hour it is a convenient way to reduce the load levels of the time scope. The moving average of the demand, operating reserve, variable generation and ESS product inflows and outflows over
the time step load levels is assigned to active load levels (e.g., the mean value of the three hours is associated to the third hour in a trihourly time step).

Duration
--------

A description of the data included in the file ``oH_Data_Duration.csv`` follows:

==========  ========  ===================================================================  ==
Identifier  Header    Description
==========  ========  ===================================================================  ==
Load level  Duration  Duration of the load level. Load levels with duration 0 are ignored  h
==========  ========  ===================================================================  ==

It is a simple way to use isolated snapshots or representative days or just the first three months instead of all the hours of a year to simplify the optimization problem.
A load level duration of 0.25 h would be used for defining all the data in quarters of an hour.

Period
------

A description of the data included in the file ``oH_Data_Period.csv`` follows:

==============  ============  =====================
Identifier      Header        Description
==============  ============  =====================
Scenario        Weight        Weight of each period
==============  ============  =====================

This weight allows the definition of equivalent (representative) hours (e.g., hour 0 with a weight of 7 would represent the first hour of 7 equivalent days). Periods are not mathematically connected between them, i.e., no constraints link the operation
at different periods.

Scenario
--------

A description of the data included in the file ``oH_Data_Scenario.csv`` follows:

==============  ==============  ============  ===========================================  ====
Identifier      Identifier      Header        Description
==============  ==============  ============  ===========================================  ====
Period          Scenario        Probability   Probability of each scenario in each period  p.u.
==============  ==============  ============  ===========================================  ====

For example, the scenarios can be used for obtaining the optimal participation of the H-VPP considering renewables uncertainty represented (windy/cloudy orcalm/sunny).
The sum of the probabilities of all the scenarios of a period must be 1.

Stage
-----

A description of the data included in the file ``oH_Data_Stage.csv`` follows:

==============  ============  =====================
Identifier      Header        Description
==============  ============  =====================
Scenario        Weight        Weight of each stage
==============  ============  =====================

This weight allows the definition of equivalent (representative) periods (e.g., one representative week with a weight of 52). Stages are not mathematically connected between them, i.e., no constraints link the operation
at different stages.

Adequacy reserve margin
-----------------------

A description of the data included in the file ``oH_Data_ReserveMargin.csv`` follows:

==============  =============  ======================================
Identifier      Header         Description
==============  =============  ======================================
Scenario        ReserveMargin  Adequacy reserve margin for each area
==============  =============  ======================================

This parameter is only used for system generation expansion, not for the system operation.

Duration
--------

A description of the data included in the file ``oH_Data_Duration.csv`` follows:

==========  ===================================================================  ========
Header      Description
==========  ===================================================================  ========
LoadLevel   Load level                                                           datetime
Duration    Duration of the load level. Load levels with duration 0 are ignored  h
Stage       Assignment of the load level to a stage
==========  ===================================================================  ========

It is a simple way to use isolated snapshots or representative days or just the first three months instead of all the hours of a year to simplify the optimization problem.

The stage duration as sum of the duration of all the load levels must be larger or equal than the shortest duration of any storage type or any outflows type (both given in the generation data) and multiple of it.
Consecutive stages are not tied between them. Consequently, the objective function must be a bit lower.

The initial storage of the ESSs is also fixed at the beginning and end of each stage. For example, the initial storage level is set for the hour 8736 in case of a single stage or for the hours 4368 and 4369
(end of the first stage and beginning of the second stage) in case of two stages, each with 4368 hours.

Electricity demand
------------------

A description of the data included in the file ``oH_Data_Demand.csv`` follows:

==========  ==============  ==========  ======  ============================================  ==
Identifier  Identifier      Identifier  Header  Description
==========  ==============  ==========  ======  ============================================  ==
Period      Scenario        Load level  Node    Power demand of the node for each load level  MW
==========  ==============  ==========  ======  ============================================  ==

The electricity demand can be negative for the (transmission) nodes where there is (renewable) generation in lower voltage levels. This negative demand is equivalent to generate that power amount in this node.
Internally, all the values below if positive demand (or above if negative demand) 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

System inertia
--------------

A description of the data included in the files ``oH_Data_Inertia.csv`` follows:

==========  ==============  ==========  ======  ================================================  ==
Identifier  Identifier      Identifier  Header  Description
==========  ==============  ==========  ======  ================================================  ==
Period      Scenario        Load level  Area    System inertia of the area for each load level    s
==========  ==============  ==========  ======  ================================================  ==

Given that the system inertia depends on the area, it can be sensible to assign an area as a country, for example. The system inertia can be used for imposing a minimum synchronous power and, consequently, force the commitment of at least some rotating units.

Internally, all the values below 2.5e-5 times the maximum system electricity demand of each area will be converted into 0 by the model.

Upward and downward operating reserves
--------------------------------------

A description of the data included in the files ``oH_Data_OperatingReserveUp.csv`` and ``oH_Data_OperatingReserveDown.csv`` follows:

==========  ==============  ==========  ======  ===================================================================  ==
Identifier  Identifier      Identifier  Header  Description
==========  ==============  ==========  ======  ===================================================================  ==
Period      Scenario        Load level  Area    Upward/downward operating reserves of the area for each load level   MW
==========  ==============  ==========  ======  ===================================================================  ==

Given that the operating reserves depend on the area, it can be sensible to assign an area as a country, for example.
These operating reserves must include Automatic Frequency Restoration Reserves (aFRR), Manual Frequency Restoration Reserves (mFRR) and Replacement Reserves (RR) for electricity balancing from ENTSO-E.

Internally, all the values below 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Generation
----------
A description of the data included for each generating unit in the file ``oH_Data_Generation.csv`` follows:

====================  ================================================================================================================================  ===================================
Header                Description
====================  ================================================================================================================================  ===================================
Node                  Name of the node where generator is located. If left empty, the generator is ignored
Technology            Technology of the generator (nuclear, coal, CCGT, OCGT, ESS, solar, wind, biomass, etc.)
MutuallyExclusive     Mutually exclusive generator. Only exclusion in one direction is needed
BinaryCommitment      Binary unit commitment decision                                                                                                   Yes/No
NoOperatingReserve    No contribution to operating reserve. Yes if the unit doesn't contribute to the operating reserve                                 Yes/No
StorageType           Storage type based on storage capacity (hourly, daily, weekly, 4-week, yearly)                                                    Hourly/Daily/Weekly/Monthly/Yearly
OutflowsType          Outflows type based on the electricity demand extracted from the storage (daily, weekly, 4-week, yearly)                          Daily/Weekly/Monthly/Yearly
EnergyType            Energy type based on the max/min energy to be produced by the unit (daily, weekly, 4-week, yearly)                                Daily/Weekly/Monthly/Yearly
MustRun               Must-run unit                                                                                                                     Yes/No
InitialPeriod         Initial period (year) when the unit is installed or can be installed, if candidate                                                Year
FinalPeriod           Final   period (year) when the unit is installed or can be installed, if candidate                                                Year
MaximumPower          Maximum power output (generation/discharge for ESS units)                                                                         MW
MinimumPower          Minimum power output (i.e., minimum stable load in the case of a thermal power plant)                                             MW
MaximumReactivePower  Maximum reactive power output (discharge for ESS units) (not used in this version)                                                MW
MinimumReactivePower  Minimum reactive power output (not used in this version)                                                                          MW
MaximumCharge         Maximum consumption/charge when the ESS unit is storing energy                                                                    MW
MinimumCharge         Minimum consumption/charge when the ESS unit is storing energy                                                                    MW
InitialStorage        Initial energy stored at the first instant of the time scope                                                                      GWh
MaximumStorage        Maximum energy that can be stored by the ESS unit                                                                                 GWh
MinimumStorage        Minimum energy that can be stored by the ESS unit                                                                                 GWh
Efficiency            Round-trip efficiency of the pump/turbine cycle of a pumped-hydro storage power plant or charge/discharge of a battery            p.u.
ProductionFunction    Production function from water inflows to energy (only used for hydropower plants modeled with water units and basin topology)    kWh/m\ :sup:`3`
ProductionFunctionH2  Production function from energy to hydrogen (only used for electrolyzers)                                                         kWh/kgH2
Availability          Unit availability for system adequacy reserve margin                                                                              p.u.
Inertia               Unit inertia constant                                                                                                             s
EFOR                  Equivalent Forced Outage Rate                                                                                                     p.u.
RampUp                Ramp up   rate for generating units or maximum discharge rate for ESS discharge                                                   MW/h
RampDown              Ramp down rate for generating units or maximum    charge rate for ESS    charge                                                   MW/h
UpTime                Minimum uptime                                                                                                                    h
DownTime              Minimum downtime                                                                                                                  h
ShiftTime             Maximum shift time                                                                                                                h
FuelCost              Fuel cost                                                                                                                         €/Mcal
LinearTerm            Linear term (slope) of the heat rate straight line                                                                                Mcal/MWh
ConstantTerm          Constant term (intercept) of the heat rate straight line                                                                          Mcal/h
OMVariableCost        Variable O&M cost                                                                                                                 €/MWh
OperReserveCost       Operating reserve cost                                                                                                            €/MW
StartUpCost           Startup  cost                                                                                                                     M€
ShutDownCost          Shutdown cost                                                                                                                     M€
CO2EmissionRate       CO2 emission rate. It can be negative for units absorbing CO2 emissions as biomass                                                tCO2/MWh
FixedInvestmentCost   Overnight investment (capital and fixed O&M) cost                                                                                 M€
FixedRetirementCost   Overnight retirement (capital and fixed O&M) cost                                                                                 M€
FixedChargeRate       Fixed-charge rate to annualize the overnight investment cost                                                                      p.u.
StorageInvestment     Storage capacity and energy inflows linked to the investment decision                                                             Yes/No
BinaryInvestment      Binary unit investment decision                                                                                                   Yes/No
InvestmentLo          Lower bound of investment decision                                                                                                p.u.
InvestmentUp          Upper bound of investment decision                                                                                                p.u.
BinaryRetirement      Binary unit retirement decision                                                                                                   Yes/No
RetirementLo          Lower bound of retirement decision                                                                                                p.u.
RetirementUp          Upper bound of retirement decision                                                                                                p.u.
====================  ================================================================================================================================  ===================================

Daily *storage type* means that the ESS inventory is assessed every time step, for weekly storage type it is assessed at the end of every day, and monthly/yearly storage type is assessed at the end of every week.
*Outflows type* represents the interval when the energy extracted from the storage must be satisfied (for daily outflows type at the end of every day, i.e., the sum of the energy consumed must be equal to the sum of outflows for every day).
*Energy type* represents the interval when the minimum or maximum energy to be produced by a unit must be satisfied (for daily energy type at the end of every day, i.e., the sum of the energy generated by the unit must be lower/greater to the sum of max/min energy for every day).
The *storage cycle* is the minimum between the inventory assessment period (defined by the storage type), the outflows period (defined by the outflows type), and the energy period (defined by the energy type) (only if outflows or energy power values have been introduced).
It can be one time step, one day, and one week.
The ESS inventory level at the end of a larger storage cycle is fixed to its initial value, i.e., the inventory of a daily storage type (evaluated on a time step basis) is fixed at the end of the week,
the inventory of weekly/monthly storage is fixed at the end of the year, only if the initial inventory lies between the storage limits.

The initial storage of the ESSs is also fixed at the beginning and end of each stage, only if the initial inventory lies between the storage limits. For example, the initial storage level is set for the hour 8736 in case of a single stage or for the hours 4368 and 4369
(end of the first stage and beginning of the second stage) in case of two stages, each with 4368 hours.

A generator with operation cost (sum of the fuel and emission cost, excluding O&M cost) > 0 is considered a non-renewable unit. If the unit has no operation cost and its maximum storage = 0,
it is considered a renewable unit. If its maximum storage is > 0, with or without operation cost, is considered an ESS.

Must-run non-renewable units are always committed, i.e., their commitment decision is equal to 1. All must-run units are forced to produce at least their minimum output.

If unit availability is left 0 or empty is changed to 1. For declaring a unit non contributing to system adequacy reserve margin, put the availability equal to a very small number.

EFOR is used to reduce the maximum and minimum power of the unit. For hydro units it can be used to reduce their maximum power by the water head effect. It does not reduce the maximum charge.

Those generators or ESS with fixed cost > 0 are considered candidate and can be installed or not.

Maximum and minimum storage is considered proportional to the invested capacity for the candidate ESS units if StorageInvestment is activated.

If lower and upper bounds of investment/retirement decisions are very close (with a difference < 1e-3) to 0 or 1 are converted into 0 and 1.

Variable maximum and minimum generation
---------------------------------------

A description of the data included in the files ``oH_Data_VariableMaxGeneration.csv`` and ``oH_Data_VariableMinGeneration.csv`` follows:

==========  ==============  ==========  =========  ============================================================  ==
Identifier  Identifier      Identifier  Header     Description
==========  ==============  ==========  =========  ============================================================  ==
Period      Scenario        Load level  Generator  Maximum (minimum) power generation of the unit by load level  MW
==========  ==============  ==========  =========  ============================================================  ==

This information can be used for considering scheduled outages or weather-dependent operating capacity.

To force a generator to produce 0 a lower value (e.g., 0.1 MW) strictly > 0, but not 0 (in which case the value will be ignored), must be introduced. This is needed to limit the solar production at night, for example.
It can be used also for upper-bounding and/or lower-bounding the output of any generator (e.g., run-of-the-river hydro, wind).

Internally, all the values below 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Variable maximum and minimum consumption
----------------------------------------

A description of the data included in the files ``oH_Data_VariableMaxConsumption.csv`` and ``oH_Data_VariableMinConsumption.csv`` follows:

==========  ==============  ==========  =========  =============================================================  ==
Identifier  Identifier      Identifier  Header     Description
==========  ==============  ==========  =========  =============================================================  ==
Period      Scenario        Load level  Generator  Maximum (minimum) power consumption of the unit by load level  MW
==========  ==============  ==========  =========  =============================================================  ==

To force a ESS to consume 0 a lower value (e.g., 0.1 MW) strictly > 0, but not 0 (in which case the value will be ignored), must be introduced.
It can be used also for upper-bounding and/or lower-bounding the consumption of any ESS (e.g., pumped-hydro storage, battery).

Internally, all the values below 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Variable fuel cost
------------------

A description of the data included in the file ``oH_Data_VariableFuelCost.csv`` follows:

==========  ==============  ==========  =========  =============================  ======
Identifier  Identifier      Identifier  Header     Description
==========  ==============  ==========  =========  =============================  ======
Period      Scenario        Load level  Generator  Variable fuel cost             €/Mcal
==========  ==============  ==========  =========  =============================  ======

All the generators must be defined as columns of these files.

Internally, all the values below 1e-4 will be converted into 0 by the model.

Fuel cost affects the linear and constant terms of the heat rate, expressed in Mcal/MWh and Mcal/h respectively.

Energy inflows
--------------

A description of the data included in the file ``oH_Data_EnergyInflows.csv`` follows:

==========  ==============  ==========  =========  =============================  =====
Identifier  Identifier      Identifier  Header     Description
==========  ==============  ==========  =========  =============================  =====
Period      Scenario        Load level  Generator  Energy inflows by load level   MWh/h
==========  ==============  ==========  =========  =============================  =====

All the generators must be defined as columns of these files.

If you have daily energy inflows data just input the daily amount at the first hour of every day if the ESS have daily or weekly storage capacity.

Internally, all the values below 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Energy inflows are considered proportional to the invested capacity for the candidate ESS units if StorageInvestment is activated.

Energy outflows
---------------

A description of the data included in the file ``oH_Data_EnergyOutflows.csv`` follows:

==========  ==============  ==========  =========  =============================  =====
Identifier  Identifier      Identifier  Header     Description
==========  ==============  ==========  =========  =============================  =====
Period      Scenario        Load level  Generator  Energy outflows by load level  MWh/h
==========  ==============  ==========  =========  =============================  =====

All the generators must be defined as columns of these files.

These energy outflows can be used to represent the energy extracted from an ESS to produce H2 from electrolyzers, to move EV or as hydro outflows for irrigation.
The use of these outflows is incompatible with the charge of the ESS within the same time step (as the discharge of a battery is incompatible with the charge in the same hour).

If you have daily/weekly/monthly/yearly outflows data, you can just input the daily/weekly/monthly/yearly amount at the first hour of every day/week/month/year.

Internally, all the values below 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Variable maximum and minimum storage
------------------------------------

A description of the data included in the files ``oH_Data_VariableMaxStorage.csv`` and ``oH_Data_VariableMinStorage.csv`` follows:

==========  ==============  ==========  =========  ====================================================  ===
Identifier  Identifier      Identifier  Header     Description
==========  ==============  ==========  =========  ====================================================  ===
Period      Scenario        Load level  Generator  Maximum (minimum) storage of the ESS by load level    GWh
==========  ==============  ==========  =========  ====================================================  ===

All the generators must be defined as columns of these files.

For example, these data can be used for defining the operating guide (rule) curves for the ESS.

Variable maximum and minimum energy
-----------------------------------

A description of the data included in the files ``oH_Data_VariableMaxEnergy.csv`` and ``oH_Data_VariableMinEnergy.csv`` follows:

==========  ==============  ==========  =========  ====================================================  ===
Identifier  Identifier      Identifier  Header     Description
==========  ==============  ==========  =========  ====================================================  ===
Period      Scenario        Load level  Generator  Maximum (minimum) energy of the unit by load level    MW
==========  ==============  ==========  =========  ====================================================  ===

All the generators must be defined as columns of these files.

For example, these data can be used for defining the minimum and/or maximum energy to be produced on a daily/weekly/4-week/yearly basis (depending on the EnergyType).

Electricity transmission network
--------------------------------

A description of the circuit (initial node, final node, circuit) data included in the file ``oH_Data_Network.csv`` follows:

===================  ===============================================================================================================  ======
Header               Description
===================  ===============================================================================================================  ======
LineType             Line type {AC, DC, Transformer, Converter}
Switching            The transmission line is able to switch on/off                                                                   Yes/No
InitialPeriod        Initial period (year) when the unit is installed or can be installed, if candidate                               Year
FinalPeriod          Final   period (year) when the unit is installed or can be installed, if candidate                               Year
Voltage              Line voltage (e.g., 400, 220 kV, 220/400 kV if transformer). Used only for plotting purposes                     kV
Length               Line length (only used for reporting purposes). If not defined, computed as 1.1 times the geographical distance  km
LossFactor           Transmission losses equal to the line flow times this factor                                                     p.u.
Resistance           Resistance (not used in this version)                                                                            p.u.
Reactance            Reactance. Lines must have a reactance different from 0 to be considered                                         p.u.
Susceptance          Susceptance (not used in this version)                                                                           p.u.
AngMax               Maximum angle difference (not used in this version)                                                              º
AngMin               Minimum angle difference (not used in this version)                                                              º
Tap                  Tap changer (not used in this version)                                                                           p.u.
Converter            Converter station (not used in this version)                                                                     Yes/No
TTC                  Total transfer capacity (maximum permissible thermal load) in forward  direction. Static line rating             MW
TTCBck               Total transfer capacity (maximum permissible thermal load) in backward direction. Static line rating             MW
SecurityFactor       Security factor to consider approximately N-1 contingencies. NTC = TTC x SecurityFactor                          p.u.
FixedInvestmentCost  Overnight investment (capital and fixed O&M) cost                                                                M€
FixedChargeRate      Fixed-charge rate to annualize the overnight investment cost                                                     p.u.
BinaryInvestment     Binary line/circuit investment decision                                                                          Yes/No
InvestmentLo         Lower bound of investment decision                                                                               p.u.
InvestmentUp         Upper bound of investment decision                                                                               p.u.
SwOnTime             Minimum switch-on time                                                                                           h
SwOffTime            Minimum switch-off time                                                                                          h
===================  ===============================================================================================================  ======

Depending on the voltage lines are plotted with different colors (orange < 200 kV, 200 < green < 350 kV, 350 < red < 500 kV, 500 < orange < 700 kV, blue > 700 kV).

If there is no data for TTCBck, i.e., TTCBck is left empty or is equal to 0, it is substituted by the TTC in the code. Internally, all the TTC and TTCBck values below 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Reactance can take a negative value as a result of the approximation of three-winding transformers. No Kirchhoff's second law disjunctive constraint is formulated for a circuit with negative reactance.

Those lines with fixed cost > 0 are considered candidate and can be installed or not.

If lower and upper bounds of investment decisions are very close (with a difference < 1e-3) to 0 or 1 are converted into 0 and 1.

Node location
-------------

A description of the data included in the file ``oH_Data_NodeLocation.csv`` follows:

==============  ============  ================  ==
Identifier      Header        Description
==============  ============  ================  ==
Node            Latitude      Node latitude     º
Node            Longitude     Node longitude    º
==============  ============  ================  ==

Hydrogen System Input Data
==========================

These input files are specifically introduced for allowing a representation of the hydrogen energy vector to supply hydrogen demand produced with electricity through the hydrogen network.

=========================================  ================================================================================================================================
File                                       Description
=========================================  ================================================================================================================================
``oH_Data_DemandHydrogen.csv``             Hydrogen demand
``oH_Data_NetworkHydrogen.csv``            Hydrogen pipeline network data
=========================================  ================================================================================================================================

Hydrogen demand
---------------

A description of the data included in the file ``oH_Data_DemandHydrogen.csv`` follows:

==========  ==============  ==========  ======  ===============================================  =====
Identifier  Identifier      Identifier  Header  Description
==========  ==============  ==========  ======  ===============================================  =====
Period      Scenario        Load level  Node    Hydrogen demand of the node for each load level  tH2/h
==========  ==============  ==========  ======  ===============================================  =====

Internally, all the values below if positive demand (or above if negative demand) 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Hydrogen transmission pipeline network
--------------------------------------

A description of the circuit (initial node, final node, circuit) data included in the file ``oH_Data_NetworkHydrogen.csv`` follows:

===================  ===================================================================================================================  ======
Header               Description
===================  ===================================================================================================================  ======
InitialPeriod        Initial period (year) when the unit is installed or can be installed, if candidate                                   Year
FinalPeriod          Final   period (year) when the unit is installed or can be installed, if candidate                                   Year
Length               Pipeline length (only used for reporting purposes). If not defined, computed as 1.1 times the geographical distance  km
TTC                  Total transfer capacity (maximum permissible thermal load) in forward  direction. Static pipeline rating             tH2
TTCBck               Total transfer capacity (maximum permissible thermal load) in backward direction. Static pipeline rating             tH2
SecurityFactor       Security factor to consider approximately N-1 contingencies. NTC = TTC x SecurityFactor                              p.u.
FixedInvestmentCost  Overnight investment (capital and fixed O&M) cost                                                                    M€
FixedChargeRate      Fixed-charge rate to annualize the overnight investment cost                                                         p.u.
BinaryInvestment     Binary pipeline investment decision                                                                                  Yes/No
InvestmentLo         Lower bound of investment decision                                                                                   p.u.
InvestmentUp         Upper bound of investment decision                                                                                   p.u.
===================  ===================================================================================================================  ======

If there is no data for TTCBck, i.e., TTCBck is left empty or is equal to 0, it is substituted by the TTC in the code. Internally, all the TTC and TTCBck values below 2.5e-5 times the maximum system demand of each area will be converted into 0 by the model.

Those pipelines with fixed cost > 0 are considered candidate and can be installed or not.

If lower and upper bounds of investment decisions are very close (with a difference < 1e-3) to 0 or 1 are converted into 0 and 1.
