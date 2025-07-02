.. oHySEM documentation master file, created by Erik Alvarez

Download & Installation
========================

The **oHySEM** model is developed using `Python 3.13.2 <https://www.python.org/>`_ and `Pyomo 6.9.2 <https://pyomo.readthedocs.io/en/stable/>`_, with `Gurobi 12.0.2 <https://www.gurobi.com/products/gurobi-optimizer/>`_ as the commercial solver. Free solvers like `HiGHS`, `SCIP`, `GLPK`, and `CBC` are also supported. List available Pyomo solvers by running::

  pyomo help -s

**Installing solvers:**

- Gurobi: ``conda install -c gurobi gurobi``
- HiGHS: ``pip install highspy``
- SCIP: ``conda install -c conda-forge pyscipopt``
- GLPK: ``conda install glpk``

**Installing oHySEM** via `pip <https://pypi.org/project/oHySEM/>`_:

``pip install oHySEM``

For the full setup guide, refer to the `installation guide <https://pascua.iit.comillas.edu/aramos/oHySEM_installation.pdf>`_.

**From GitHub:**

1. Clone the `oHySEM repository <https://github.com/IIT-EnergySystemModels/oHySEM.git>`_
2. Navigate to the folder: ``cd path_to_repository``
3. Install with: ``pip install .``

**Running oHySEM:**

After installation, you can run the model via the command line:

``oHySEM``

or using the Python script:

``python -m oHySEM --dir {path_to_input_data} --case {case_name} --solver {solver_name}``

**Running the API:**

To run the Streamlit API, execute the following command in the terminal that should be located in the path where the API.py file is located:

``streamlit run oHySEM_API.py``

**Solvers**:

- `HiGHS <https://www.scipopt.org/index.php#download>`_ (free)
- `Gurobi <https://www.gurobi.com/>`_ (academic license available)
- `GLPK <https://www.gnu.org/software/glpk/>`_ (free)
- `CBC <https://github.com/coin-or/Cbc/releases>`_ (free)

**Additional requirements:**

- `Pandas <https://pandas.pydata.org/>`_
- `psutil <https://pypi.org/project/psutil/>`_
- `Plotly <https://plotly.com/python/>`_, `Altair <https://altair-viz.github.io/#>`_, `Colour <https://pypi.org/project/colour/>`_
- `NetworkX <https://networkx.org/>`_

