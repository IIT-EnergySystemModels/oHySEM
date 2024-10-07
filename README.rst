
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
3. `Installation <#installation>`_
4. `Use Cases <#use-cases>`_
5. `Contributing <#contributing>`_
6. `License <#license>`_

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

- **Hybrid System Modeling**: Simulate and optimize the interaction between renewable electricity and hydrogen systems.
- **Market Integration**: Enable systems to participate in energy markets and optimize based on market conditions.
- **Asset Integration**: Support dynamic integration of new energy assets into the system.
- **Grid and Stand-alone Systems**: Model systems that are either grid-connected or self-sufficient.
- **Scalable**: Suitable for small- to large-scale hybrid power plants and virtual power plants (VPPs).

---

Installation
============

**Installing solvers:**

- Gurobi: ``conda install -c gurobi gurobi``
- HiGHS: ``pip install highspy``
- SCIP: ``conda install -c conda-forge pyscipopt``
- GLPK: ``conda install glpk``

**Installing oHySEM** via `pip <https://pypi.org/project/oHySEM/>`_:

.. code-block:: bash

    pip install ohysem

For the full setup guide, refer to the `installation guide <https://pascua.iit.comillas.edu/aramos/oHySEM_installation.pdf>`_.

**From GitHub:**

1. Clone the `oHySEM repository <https://github.com/IIT-EnergySystemModels/oHySEM.git>`_
2. Navigate to the folder: ``cd path_to_repository``
3. Install with: ``pip install .``

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

    streamlit run API3.py

**Solvers**:

- `HiGHS <https://ergo-code.github.io/HiGHS/>`_ (free)
- `Gurobi <https://www.gurobi.com/>`_ (academic license available)
- `GLPK <https://www.gnu.org/software/glpk/>`_ (free)
- `CBC <https://github.com/coin-or/Cbc>`_ (free)

**Additional requirements:**

- `Pandas <https://pandas.pydata.org/>`_
- `psutil <https://pypi.org/project/psutil/>`_
- `Plotly <https://plotly.com/python/>`_, `Altair <https://altair-viz.github.io/#>`_, `Colour <https://pypi.org/project/colour/>`_
- `NetworkX <https://networkx.org/>`_

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
