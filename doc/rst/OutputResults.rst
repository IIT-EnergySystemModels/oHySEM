.. oHySEM documentation master file, created by Erik Alvarez

Output results
==============

The output includes several maps of the electricity transmission network and plots showing the energy share of different technologies.

In addition, the model generates several other plots to visualise key results. The CSV files used to store the output results are of three types:

1. **Optimisation variable values**: Files related to the values of each variable in the optimisation problem.
2. **Dual Values of Constraints: Files containing the dual values associated with the constraints.
3. **Derived/Transformed Values: Files that are derived or transformed from the values of variables.

### Unit conventions:

- For the first two types of CSV files (values of optimisation variables and dual values of constraints), power is expressed in **GW**, cost in **M€** and hydrogen in **tH2**.
- For the third type (derived/transformed values), power is expressed in **MW**, energy in **GWh**, cost in **M€** and hydrogen in **kgH2**.

CSV files for optimisation variables
------------------------------------------

Each file in this category is named
``oH_Result_v**{Variable Name}**_{Case Name}.csv``

The structure of the CSV file is as follows

============= ===== ===== ========== ==========
Variable Name Index Value LowerBound UpperBound
============= ===== ===== ========== ==========

CSV files for dual values of constraints
----------------------------------------

Each file in this category is named
``oH_Result_e**{Constraint Name}**_{Case Name}.csv``

The structure of the CSV file is as follows

=============== ===== ===== ========== ==========
Constraint Name Index Value LowerBound UpperBound
=============== ===== ===== ========== ==========
