Change Log
==========

[1.0.14] - 2025-03-07
---------------------
- [CHANGED] streamlit shows min and max values of Electrolyzer production function
- [CHANGED] oHySEM has approximated by three piecewise inequalities the electrolyzer hydrogen production

[1.0.13] - 2025-01-17
---------------------
- [CHANGED] streamlit shows Electrolyzer Commitment
- [CHANGED] oHySEM has fixed the use of StandBy status of the electrolyzer

[1.0.12] - 2024-12-15
---------------------
- [CHANGED] streamlit shows Electricity and H2 Storage balances simultaneously with storage levels at ESS and HSS
- [CHANGED] streamlit shows Solar PV Data and Solar PV VarMaxGeneration

[1.0.11] - 2024-11-27
---------------------
- [CHANGED] oHySEM writes Electricity and H2 Storage levels at ESS and HSS contract conditions
- [CHANGED] streamlit shows Electricity and H2 Storage levels at ESS and HSS contract conditions

[1.0.10] - 2024-11-21
---------------------
- [CHANGED] streamlit shows and edit H2 market price/cost and H2 delivery contract conditions
- [UPDATED] streamlit depicts interactive figures of Electricity and H2 balances
- [UPDATED] Excel oHySEM_InputData updates the Generation & Parameter modified by Streamlit
- [CHANGED] oHySEM H2 outputs are in kgH2

[1.0.9] - 2024-11-15
---------------------
- [CHANGED] streamlit includes info buttons for output figures
- [CHANGED] Excel oHySEM_InputData updates the Generation Data modified by Streamlit
- [CHANGED] oHySEM inputs are in MEUR

[1.0.8] - 2024-11-12
---------------------
- [CHANGED] streamlit includes buttons for information help
- [CHANGED] streamlit shows economic outputs in kEUR (need validation)
- [CHANGED] oHySEM outputs are in kEUR

[1.0.7] - 2024-11-05
---------------------
- [CHANGED] streamlit allows change in MaxGeneration

[1.0.7] - 2024-11-05
---------------------
- [CHANGED] streamlit allows change in MaxGeneration

[1.0.6] - 2024-10-15
---------------------
- [CHANGED] allow the use with GAMS-HIGHS
- [CHANGED] allow the use with GLPK

[1.0.5] - 2024-10-11
---------------------
- [CHANGED] allow the use with GAMS-CPLEX
- [CHANGED] added a new function to print plots in the main file

[1.0.4] - 2024-09-12
---------------------
- [CHANGED] added the date, raw data and plots as arguments to be inserted by the user or adopted by default
- [CHANGED] adding a column 'date' in the derivative results

[1.0.3] - 2024-09-11
---------------------

- [FIXED] updated the introduction of the documentation to be shown in readthedocs
- [CHANGED] adding the option to change the solver in the main file
- [FIXED] updated the installation guide in the documentation

[1.0.2] - 2024-09-10
---------------------

- [CHANGED] created the rst files and deployed the documentation in readthedocs

[1.0.1] - 2024-09-10
---------------------

- [FIXED] updated _init_.py

[1.0.0] - 2024-09-09
---------------------

- [CHANGED] included metadata in pyproject.toml and also requirements  (only pyomo, matplotlib, numpy, pandas, and psutil.)
- [CHANGED] created a README.md file
- [FIXED] updated _init_.py
