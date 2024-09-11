.. oHySEM documentation master file, created by Erik Alvarez

Output Results
==============

Some maps of the electricity transmission network and the energy share of different technologies is plotted.

Some other additional plots are also plotted by the model. The CSV files used for outputting the results are briefly described in the following items.
There are three types of CSV files: 1) those related to the value of each variable in the optimisation problem, 2) those related to the dual values of the constraints, and 3) those derived and transformed from the value of the variables.

For the first two types of CSV files, the power is expressed in GW, and costs in M€. Hydrogen is expressed in tH2.
And, for the last type of CSV files, the power is expressed in MW, energy in GWh, and costs in M€. Hydrogen is expressed in kgH2.

CSV files related to the value of each variable in the optimisation problem
---------------------------------------------------------------------------

File ``oH_Result_v**{Variable Name}**_{Case Name}.csv``

=============  =====  =====  ==========  ==========
Variable Name  Index  Value  LowerBound  UpperBound
=============  =====  =====  ==========  ==========

File ``oH_Result_e**{Constraint Name}**_{Case Name}.csv``

===============  =====  =====  ==========  ==========
Constraint Name  Index  Value  LowerBound  UpperBound
===============  =====  =====  ==========  ==========
