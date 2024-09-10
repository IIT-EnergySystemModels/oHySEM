.. oHySEM documentation master file, created by Erik Alvarez

============================
Welcome to oHySEM - Overview
============================

The *optimized Hybrid Systems for Energy and Market management* (**oHySEM**) model is a state-of-the-art Python library designed for the optimization of hybrid renewable energy systems, particularly hydrogen-based virtual power plants (H-VPPs), in short-term electricity markets. Developed with a focus on efficient energy management, **oHySEM** also enables strategic decisions regarding the **location and sizing of new energy assets**, ensuring optimal system design and market participation.

By integrating renewable energy sources like Solar PV, Wind, and CCGT with hydrogen-based energy storage and battery systems, **oHySEM** allows H-VPPs to operate as a unified, flexible entity in various electricity markets. The model helps users maximize operational efficiency, profitability, and the overall performance of hybrid systems by dynamically optimizing energy dispatch, storage, and market bids.

.. image:: /../img/System.png
   :scale: 35%
   :align: center

Hybrid Systems for the Energy Transition
----------------------------------------

As energy systems increasingly incorporate hybrid resources, **oHySEM** plays a pivotal role by enabling users to design, operate, and optimize their hybrid virtual power plants. Whether managing existing assets or planning the **location and sizing of new energy assets**, the model provides essential decision support tools to balance renewable energy generation, hydrogen as a long-term storage solution, and battery systems for short-term energy flexibility.

The model addresses uncertainties inherent in renewable energy production and market conditions, making it ideal for both operational optimization and strategic asset planning.

Multi-Stage Market Optimization and Asset Planning
---------------------------------------------------

**oHySEM** goes beyond operational optimization by enabling strategic asset placement and capacity planning. With its advanced multi-stage optimization capabilities, the model covers various time-sensitive operations across different markets while also facilitating the location and sizing of new assets to meet market needs and ensure efficient operation.

1. **Day-Ahead Market (DA)**:
   The day-ahead market sets the foundation for electricity transactions over the next 24 hours. **oHySEM** optimizes bids for energy production and consumption, ensuring that renewable generation, hydrogen production, and battery storage systems are used efficiently. Additionally, the model can assess the best locations and sizes for new generation or storage assets to enhance profitability and grid stability.

2. **Secondary Reserve Market (SR)**:
   By participating in the secondary reserve market, **oHySEM** enables H-VPPs to provide balancing services to the grid. The model optimizes bids for upward and downward reserves, contributing to grid reliability while generating additional revenue. For new assets, **oHySEM** can analyze which locations and sizes provide the most effective reserve contributions.

3. **Intraday Market (ID)**:
   Intraday market participation requires continuous adjustments to day-ahead schedules. **oHySEM** dynamically adapts to real-time fluctuations in renewable energy production and market conditions, optimizing intraday bids. The model also helps determine the ideal location and capacity of assets to handle these fluctuations and meet intraday market demands.

4. **Imbalance Settlement (IB)**:
   Imbalance settlement addresses deviations between actual generation and market-cleared energy. **oHySEM** ensures that these imbalances are managed efficiently, minimizing penalties and maximizing rewards for over-delivery. The model helps users strategically plan asset placement to reduce imbalances and optimize system performance.

Optimized Scheduling, Operation, and Asset Design
--------------------------------------------------

The **oHySEM** model is highly versatile, designed not only to optimize operational schedules over short-term horizons but also to provide insights into the **optimal location and sizing of new energy assets**. The model supports detailed decision-making with time scopes ranging from 1 to 7 days and high temporal granularity (15-minute to 1-hour intervals).

- **Day-Ahead Scheduling and Asset Planning**: Optimize bids for day-ahead markets, considering forecasts of renewable generation, hydrogen storage levels, and battery state-of-charge. Simultaneously, analyze the best locations and sizes for new assets to ensure they enhance market participation.

- **Real-Time Dispatch and Asset Integration**: Operate BESS and hydrogen systems in real-time to meet market-cleared commitments, while adapting to actual generation conditions. **oHySEM** helps ensure that newly placed assets are effectively integrated into the real-time operation of the H-VPP.

- **Reserve Market and Asset Expansion**: Analyze reserve market opportunities and determine the optimal sizing and placement of assets to maximize reserve capacity contributions while supporting grid stability.

Tailored Decision Support for Assets and Operations
---------------------------------------------------

**oHySEM** allows users to predefine the structure of their H-VPP, including the placement of new assets. It then determines the optimal operating schedules and market participation strategies for existing and planned resources. Key decision variables include:

- Energy production and asset location from renewable sources (solar, wind, or CCGT)
- Hydrogen production, consumption, and storage design
- Battery energy storage sizing and operational schedules
- Market bids for energy sales and reserve capacity
- Optimal sizing and location of new energy assets

This tailored decision support enables energy managers and system operators to make informed choices about not only operations but also the strategic expansion of their H-VPP infrastructure.

Key Features of oHySEM
======================

- **Comprehensive Market and Asset Integration**:
  - Day-ahead, intraday, real-time, and secondary reserve markets
  - Location and sizing of new energy assets to enhance market participation
  - Imbalance settlement to manage deviations and maximize profitability

- **Multi-Period Decision Making**:
  **oHySEM** supports detailed decision-making with time scopes from 1 to 7 days, offering fine-grained temporal resolution (15 minutes to 1 hour) for operational scheduling and asset planning.

- **Hydrogen and Battery Optimization**:
  The model optimizes hydrogen production, storage, and battery energy storage systems (BESS) to maximize the flexibility and profitability of hybrid energy systems. It can also determine the ideal sizing and placement of hydrogen tanks and battery units.

- **Maximizing Profitability and Asset Utilization**:
  By optimizing market bids, reserve contributions, and the design of new assets, **oHySEM** maximizes profitability while ensuring that hybrid systems operate efficiently and contribute to grid stability.

Outputs and Results
===================

**oHySEM** provides a wide range of output data in both CSV and graphical formats, allowing users to thoroughly analyze the performance of their hybrid systems and asset designs:

- **Electricity Market Results**:
  - Optimized day-ahead, intraday, and real-time bids
  - Secondary reserve offers (upward and downward)
  - Real-time dispatch and adjustments
  - Energy imbalances and financial impact

- **Hydrogen System Results**:
  - Hydrogen production and storage optimization
  - Hydrogen consumption schedules
  - Imbalances in hydrogen systems

- **Asset Location and Sizing Results**:
  - Recommendations for the optimal location and sizing of new generation, hydrogen, and battery storage assets
  - Performance analysis of newly placed assets in operational and market contexts

These outputs provide critical insights into both the operational efficiency and strategic expansion of H-VPPs.

Scalability and Performance
===========================

**oHySEM** is designed for scalability and robustness, using advanced optimisation techniques such as Mixed Integer Linear Programming (MILP). The model is capable of handling large multi-component systems, market scenarios and asset planning considerations.

With the ability to analyse both short-term operations and long-term asset placement, **oHySEM** provides reliable and actionable insights for managing and expanding hybrid energy systems.

---

With **oHySEM**, energy system operators, market participants and researchers can optimise the design, operation and market participation of renewable hybrid systems, integrate hydrogen and battery storage, and make informed decisions about the location and sizing of new assets.

Unlock the full potential of your hybrid energy systems with **oHySEM** today!
