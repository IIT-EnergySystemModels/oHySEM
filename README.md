# oHYSEM – <span style="color:blue;">H</span>ybrid <span style="color:blue;">S</span>ystems for <span style="color:blue;">E</span>nergy management and <span style="color:blue;">M</span>arket strategies

``Simplicity and Transparency in Power Systems Operation and Planning``

**oHYSEM** is an open-source model distributed as a Python library, designed to provide optimal planning, operation, and management strategies for hybrid renewable electricity-hydrogen systems. It supports both stand-alone and grid-connected systems in participating in energy and hydrogen markets, ensuring the seamless integration of new assets and efficient system scheduling.

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [API Reference](#api-reference)
6. [Use Cases](#use-cases)
7. [Contributing](#contributing)
8. [License](#license)

---

## Overview

**oHYSEM** provides a robust framework for optimizing hybrid energy systems, incorporating renewable electricity and hydrogen networks. The library is designed for users needing advanced tools for integrated resource planning, asset integration, system scheduling, and market participation in electricity and hydrogen markets.

### Key Applications:
- **Optimal Planning & Scheduling**: Ensure efficient energy resource management in hybrid systems.
- **Integrated Resource Planning (IRP)**: Plan long-term energy strategies integrating multiple energy sources.
- **Market Participation**: Engage in real-time electricity markets and future hydrogen markets.
- **Asset Integration**: Seamlessly incorporate new assets (e.g., renewable generators, storage units) into the system.
- **Self-scheduling**: Operation planning of the hybrid system. 

---

## Features

- **Hybrid System Modeling**: Simulate and optimize the interaction between renewable electricity and hydrogen systems.
- **Market Integration**: Enable systems to participate in energy markets and optimize based on market conditions.
- **Asset Integration**: Support dynamic integration of new energy assets into the system.
- **Grid and Stand-alone Systems**: Model systems that are either grid-connected or self-sufficient.
- **Scalable**: Suitable for small- to large-scale hybrid power plants and virtual power plants (VPPs).

---

## Installation

Install **oHYSEM** using pip:

```bash
pip install ohysem
```
Alternatively, clone the GitHub repository and install it manually:
```
git clone https://github.com/yourusername/ohysem.git
cd oHYSEM
pip install .
```

---

## Getting Started
Here’s a basic example of how to create and run an optimization model using oHYSEM:

```
import oHYSEM as hs

# Define your hybrid system
system = hs.HybridSystem()

# Add energy assets
system.add_asset(hs.SolarPlant(capacity=100))  # 100 MW solar plant
system.add_asset(hs.HydrogenStorage(capacity=50))  # 50 MWh hydrogen storage

# Define market participation and scheduling parameters
market = hs.MarketParticipation()
scheduler = hs.Scheduler(system, market)

# Run optimization
results = scheduler.optimize()

# Display results
print(results)
```

This example shows how to create a basic hybrid system, integrate assets, and run an optimization for market participation and scheduling.


---

## API Reference
The API gives users full flexibility in defining, integrating, and optimizing hybrid systems. The following are key components:
```
HybridSystem()
```
- Purpose: Represents the hybrid energy system, including both electricity and hydrogen networks.
- Methods: add_asset(), optimize(), schedule(), etc.
```
MarketParticipation()
```
- Purpose: Represents the system's participation in electricity and hydrogen markets.
- Methods: define_market_conditions(), participate(), etc.
```
Scheduler()
```
- Purpose: Optimizes the hybrid system's operation based on system constraints and market signals.
- Methods: optimize(), get_results()

Please refer to the full API documentation for more detailed usage and advanced configurations.


---

## Use Cases
Grid-connected Hybrid Systems: Optimize energy flows between electricity and hydrogen markets while meeting grid regulations.
Stand-alone VPPs: Use oHYSEM to ensure optimal operation for off-grid renewable systems.
Integrated Resource Planning (IRP): Plan the addition of new renewable assets and storage units to meet long-term energy goals.
Market Participation: Optimize market bids for both electricity and future hydrogen markets.

---

## Contributing
Contributions to oHYSEM are welcome! Please refer to our Contributing Guide for more information on how to contribute to the project.

---

## License
oHYSEM is licensed under the MIT License. See the LICENSE file for details.
