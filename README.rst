
.. image:: https://pascua.iit.comillas.edu/aramos/oHySEM_v2.png
   :target: https://ohysem.readthedocs.io/en/latest/index.html
   :alt: logo
   :align: center

|

\ **o**\ptimized \ **Hy**\brid  \ **S**\ystems for \ **E**\nergy and \ **M**\arket management **(oHySEM)**

|

.. image:: https://img.shields.io/pypi/v/ohysem
    :target: https://badge.fury.io/py/oHySEM
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/ohysem
   :target: https://pypi.org/project/oHySEM/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/readthedocs/ohysem
   :target: https://ohysem.readthedocs.io/en/latest/index.html#
   :alt: Read the Docs

.. image:: https://app.codacy.com/project/badge/Grade/c676f237a6cc4fc88a2439da0611ae2f    
   :target: https://app.codacy.com/gh/IIT-EnergySystemModels/oHySEM/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade
   :alt: Codacy Badge

.. image:: https://img.shields.io/pypi/l/ohysem
   :target: https://github.com/IIT-EnergySystemModels/oHySEM/blob/main/LICENSE
   :alt: PyPI - License

.. image:: https://img.shields.io/pepy/dt/ohysem
   :target: https://www.pepy.tech/projects/ohysem
   :alt: Pepy Total Downloads

======================================================================================================

``Simplicity and Transparency in Power Systems Operation and Planning``

**oHySEM** is an open-source model distributed as a Python library, designed to provide optimal planning, operation, and management strategies for hybrid renewable electricity-hydrogen systems. It supports both stand-alone and grid-connected systems in participating in electricity and hydrogen markets, ensuring the seamless integration of new assets and efficient system scheduling.

Table of Contents
=================

1. `Overview <#overview>`_
2. `Features <#features>`_
3. `Architecture <#architecture>`_
4. `Installation <#installation>`_
5. `Usage <#usage>`_
6. `Use Cases <#use-cases>`_
7. `Contributing <#contributing>`_
8. `License <#license>`_

---

Overview
========

**oHySEM** provides a robust framework for optimizing hybrid energy systems, incorporating renewable electricity and hydrogen networks. The library is designed for users needing advanced tools for integrated resource planning, asset integration, system scheduling, and market participation in electricity and hydrogen markets.

Key Applications:
-----------------

- **Optimal Planning & Scheduling**: Ensure efficient energy resource management in hybrid systems.
- **Integrated Resource Planning (IRP)**: Plan long-term energy strategies integrating multiple energy sources.
- **Market Participation**: Engage in real-time electricity markets and future hydrogen markets.
- **Asset Integration**: Seamlessly incorporate new assets (e.g., renewable generators, storage units) into the system.
- **Self-scheduling**: Operation planning of the hybrid system. 

---

Features
========

oHySEM offers a comprehensive suite of features for advanced energy system management:

- **Integrated Energy System Modeling**:
    - Simulate and optimize hybrid systems combining renewable electricity sources (e.g., Solar PV, Wind), conventional generation (e.g., CCGT), and hydrogen technologies (production, storage).
    - Model Battery Energy Storage Systems (BESS) for short-term flexibility.

- **Multi-Horizon Planning and Optimization**:
    - **Long-Term Asset Planning**: Support for strategic decisions on the optimal location and sizing of new energy assets (hydrogen tanks, BESS units, generation).
    - **Mid-Term Asset Optimization**: Tools for yearly planning to optimize asset utilization and adapt to market changes.
    - **Short-Term Operational Planning**: Detailed weekly and daily operational scheduling with fine-grained temporal resolution (15-minute to 1-hour intervals).

- **Advanced Operational Capabilities**:
    - **Hydrogen and Battery Optimization**: Optimize the coordinated operation of hydrogen systems (electrolyzers, storage) and BESS.
    - **Efficient Scheduling**: Align system operations with energy demands, grid requirements, and market conditions in real-time.

- **Comprehensive Market Participation**:
    - **Multi-Market Integration**: Participate in various electricity markets, including day-ahead, intraday, real-time, and secondary reserve markets.
    - **Profitability Maximization**: Optimize market bids and reserve contributions to enhance profitability.
    - **Imbalance Management**: Address deviations in energy supply and demand through effective imbalance settlement mechanisms.

- **System Design and Scalability**:
    - **Grid-Connected & Stand-Alone Systems**: Model both grid-connected systems interacting with the broader network and self-sufficient off-grid systems.
    - **Flexible Asset Integration**: Dynamically incorporate new energy assets into system models.
    - **Scalable Architecture**: Suitable for a range of applications from small-scale VPPs to large-scale hybrid power plants.
    - **Support for Various Solvers**: Compatible with Gurobi, HiGHS, SCIP, GLPK, and CBC.

---

Architecture
============

oHySEM is built around a core optimization model developed in Python using the Pyomo_ library. The main logic resides in ``oHySEM/oHySEM.py``.

The system takes input data primarily from CSV files, typically located in a case-specific directory (e.g., ``oHySEM/VPP1/``). These files define parameters for the energy system, market conditions, and other operational constraints.

oHySEM processes this data to find optimal strategies and outputs the results in CSV format for detailed analysis and generates various plots for visualization.

A Streamlit_-based API (``oHySEM/oHySEM_API.py``) is also available to provide a user interface for interacting with the model.

The following diagram illustrates the general system components and interactions that oHySEM models:

.. image:: doc/img/System.png
   :alt: oHySEM System Architecture
   :align: center

.. _Pyomo: https://pyomo.readthedocs.io/
.. _Streamlit: https://streamlit.io/

---

Installation
============

**Installing solvers:**

- Gurobi: ``conda install -c gurobi gurobi``
- HiGHS: ``pip install highspy``
- SCIP: ``conda install -c conda-forge pyscipopt``
- GLPK: ``conda install glpk``

You can list available Pyomo solvers by running::

  pyomo help -s

**Installing oHySEM** via `pip <https://pypi.org/project/oHySEM/>`_:

.. code-block:: bash

    pip install ohysem

For the full setup guide, refer to the `installation guide <https://pascua.iit.comillas.edu/aramos/oHySEM_installation.pdf>`_.

**From GitHub:**

1. Clone the `oHySEM repository <https://github.com/IIT-EnergySystemModels/oHySEM.git>`_
2. Navigate to the folder: ``cd path_to_repository``
3. Install with: ``pip install .``

**Solvers**:

- `HiGHS <https://ergo-code.github.io/HiGHS/>`_ (free)
- `Gurobi <https://www.gurobi.com/>`_ (academic license available)
- `GLPK <https://www.gnu.org/software/glpk/>`_ (free)
- `CBC <https://github.com/coin-or/Cbc/releases>`_ (free)

**Additional requirements:**

- `Pandas <https://pandas.pydata.org/>`_
- `psutil <https://pypi.org/project/psutil/>`_
- `Plotly <https://plotly.com/python/>`_, `Altair <https://altair-viz.github.io/#>`_, `Colour <https://pypi.org/project/colour/>`_
- `NetworkX <https://networkx.org/>`_

---

Usage
=====

**Running oHySEM:**

After installation, you can run the model via the command line:

.. code-block:: bash

    oHySEM

or using the Python script:

.. code-block:: bash

    python -m oHySEM --dir {path_to_input_data} --case {case_name} --solver {solver_name}

**Running the API:**

To run the Streamlit API, execute the following command in the terminal that should be located in the path where the API.py file is located:

.. code-block:: bash

    streamlit run oHySEM_API.py

---

Use Cases
=========

- **Grid-connected Hybrid Systems**: Optimize energy flows between electricity and hydrogen markets while meeting grid regulations.
- **Stand-alone VPPs**: Use oHySEM to ensure optimal operation for off-grid renewable systems.
- **Integrated Resource Planning (IRP)**: Plan the addition of new renewable assets and storage units to meet long-term energy goals.
- **Market Participation**: Optimize market bids for both electricity and future hydrogen markets.

---

Contributing
============

Contributions to oHySEM are welcome! Please refer to our Contributing Guide for more information on how to contribute to the project.

---

License
=======

oHySEM is licensed under the GPL-3.0 license. See the `LICENSE file <https://github.com/IIT-EnergySystemModels/oHySEM/blob/main/LICENSE>`_ for details.
