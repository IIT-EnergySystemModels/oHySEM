# oHySEM: Optimized Hybrid Systems for Energy and Market management

## Overview

**oHySEM** is an open-source model distributed as a Python library, designed to provide optimal planning, operation, and management strategies for hybrid renewable electricity-hydrogen systems. It supports both stand-alone and grid-connected systems in participating in electricity and hydrogen markets, ensuring the seamless integration of new assets and efficient system scheduling.

**oHySEM** provides a robust framework for optimizing hybrid energy systems, incorporating renewable electricity and hydrogen networks. The library is designed for users needing advanced tools for integrated resource planning, asset integration, system scheduling, and market participation in electricity and hydrogen markets.

### Key Applications:
- **Optimal Planning & Scheduling**: Ensure efficient energy resource management in hybrid systems.
- **Integrated Resource Planning (IRP)**: Plan long-term energy strategies integrating multiple energy sources.
- **Market Participation**: Engage in real-time electricity markets and future hydrogen markets.
- **Asset Integration**: Seamlessly incorporate new assets (e.g., renewable generators, storage units) into the system.
- **Self-scheduling**: Operation planning of the hybrid system.

## Features

- **Hybrid System Modeling**: Simulate and optimize the interaction between renewable electricity and hydrogen systems.
- **Market Integration**: Enable systems to participate in energy markets and optimize based on market conditions.
- **Asset Integration**: Support dynamic integration of new energy assets into the system.
- **Grid and Stand-alone Systems**: Model systems that are either grid-connected or self-sufficient.
- **Scalable**: Suitable for small- to large-scale hybrid power plants and virtual power plants (VPPs).

## Architecture

oHySEM is built around a core optimization model developed in Python using the Pyomo library. The main logic resides in `oHySEM/oHySEM.py`.

The system takes input data primarily from CSV files, typically located in a case-specific directory (e.g., `oHySEM/VPP1/`). These files define parameters for the energy system, market conditions, and other operational constraints.

oHySEM processes this data to find optimal strategies and outputs the results in CSV format for detailed analysis and generates various plots for visualization.

A Streamlit-based API (`oHySEM/oHySEM_API.py`) is also available to provide a user interface for interacting with the model.

The following diagram illustrates the general system components and interactions that oHySEM models:

![oHySEM System Architecture](doc/img/System.png)

## Installation

Before installing oHySEM, you need to install the required solvers.

### 1. Install Solvers

You can install the solvers using Conda or pip:

-   **Gurobi:**
    ```bash
    conda install -c gurobi gurobi
    ```
    *(Note: Gurobi is a commercial solver; an academic license is available. Refer to the [Gurobi website](https://www.gurobi.com/) for details.)*
-   **HiGHS (free):**
    ```bash
    pip install highspy
    ```
    *(Refer to the [HiGHS website](https://ergo-code.github.io/HiGHS/) for details.)*
-   **SCIP (free for academic use):**
    ```bash
    conda install -c conda-forge pyscipopt
    ```
    *(Refer to the [SCIP website](https://www.scipopt.org/) for details.)*
-   **GLPK (free):**
    ```bash
    conda install glpk
    ```
    *(Refer to the [GLPK website](https://www.gnu.org/software/glpk/) for details.)*
-   **CBC (free):**
    *(Refer to the [CBC GitHub page](https://github.com/coin-or/Cbc) for installation instructions.)*

For a comprehensive setup guide, including solver installation, refer to the full `installation guide <https://pascua.iit.comillas.edu/aramos/oHySEM_installation.pdf>`_ (PDF).

### 2. Install oHySEM

You can install oHySEM using pip or directly from the GitHub repository.

**Via pip (recommended):**

```bash
pip install ohysem
```

**From GitHub (for the latest development version):**

1.  Clone the oHySEM repository:
    ```bash
    git clone https://github.com/IIT-EnergySystemModels/oHySEM.git
    ```
2.  Navigate to the cloned directory:
    ```bash
    cd oHySEM
    ```
3.  Install the package:
    ```bash
    pip install .
    ```

### Additional Requirements

oHySEM also depends on the following Python libraries:

-   Pandas
-   psutil
-   Plotly
-   Altair
-   Colour
-   NetworkX

These are typically installed automatically when you install oHySEM via pip.

## Usage

After successful installation, you can run oHySEM in several ways:

### Command Line Interface (CLI)

You can run the model directly from your terminal:

```bash
oHySEM
```
This will typically prompt you for input directory, case name, and solver if not provided as arguments or defaults are not set.

Alternatively, you can specify arguments:

```bash
python -m oHySEM --dir {path_to_input_data} --case {case_name} --solver {solver_name}
```

Replace `{path_to_input_data}`, `{case_name}`, and `{solver_name}` with your specific paths and choices. For example:
-   `--dir ./oHySEM/VPP1`
-   `--case VPP1`
-   `--solver gurobi`

### Streamlit API (Web Interface)

oHySEM includes a Streamlit-based API for a more interactive experience. To run it:

1.  Navigate to the directory containing the `oHySEM_API.py` file (usually the root of the `oHySEM` package or the repository root if running from source).
    ```bash
    # Example: if you installed from GitHub and are in the repo root
    cd oHySEM
    ```
2.  Run the Streamlit application:
    ```bash
    streamlit run oHySEM_API.py
    ```
This will open the interface in your web browser.

## Contributing

Contributions to oHySEM are welcome! If you are interested in contributing, please feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/IIT-EnergySystemModels/oHySEM).

We appreciate contributions of all kinds, including:
- Bug fixes
- New features
- Documentation improvements
- Test cases

## License

oHySEM is licensed under the **GNU General Public License v3.0**.

See the [LICENSE](LICENSE) file for full license text.
