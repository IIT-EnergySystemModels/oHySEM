.. oHySEM documentation master file, created by Erik Alvarez

Mathematical Formulation
========================
Here we present the mathematical formulation of the optimization problem solved by the **oHySEM** model.

Acronyms
--------

===========  ====================================================================
**Acronym**  **Description**
===========  ====================================================================
BESS         Battery Energy Storage System
DA           Day-Ahead Market
ESS          Energy Storage System (includes BESS and HESS)
H-VPP        Hydrogen-based Virtual Power Plant
HESS         Hydrogen Energy Storage System
ID           Intraday Markets
RT           Real Time Market
SoC          State of Charge
VRE          Variable Renewable Energy
===========  ====================================================================

Indices
-------

============  =======================================================================================================================
**Index**     **Description**
============  =======================================================================================================================
:math:`ω`     Scenario (e.g., solar generation, ID prices, etc.)
:math:`nd`    Node
:math:`n`     Load level
:math:`\nu`   Duration of the time step for the load levels (e.g., 0.25 h for 15 min load levels, 0.5 h for half an hour load levels)
:math:`eg`    Electricity unit (thermal or hydro unit or ESS)
:math:`et`    Electricity thermal unit
:math:`es`    Electricity energy storage system (eESS)
:math:`hg`    Hydrogen unit (e.g., electrolyzer, hydrogen tank)
:math:`hz`    Hydrogen electrolyzer
:math:`hs`    Hydrogen energy storage system (e.g., hydrogen tank)
:math:`R_i`   Reserve market number :math:`i` (secondary and tertiary)
============  =======================================================================================================================

Parameters
----------

They are written in **uppercase** letters.

=============================================  ===================================================================  ========  ===========================================================================
**Demand**                                     **Description**                                                      **Unit**  **oHySEM.py**
---------------------------------------------  -------------------------------------------------------------------  --------  ---------------------------------------------------------------------------
:math:`ED_{nnd}`                               Electricity demand                                                   GW        «``pElectricityDemand``»
:math:`HD_{nnd}`                               Hydrogen demand                                                      kgH2      «``pHydrogenDemand``»
:math:`DUR_n`                                  Duration of each load level                                          h         «``pDuration``»
:math:`CEB_{nnd},    PES^{DA}_{nnd}`           Cost/price of electricity bought/sold                                €/MWh     «``pElectricityCost``, ``pElectricityPrice``»
:math:`CHB_{nnd},    PHS^{DA}_{nnd}`           Cost/price of hydrogen bought/sold                                   €/kgH2    «``pHydrogenCost``, ``pHydrogenPrice``»
:math:`UP^{SR}_{n},  DP^{SR}_{n}`              Price of :math:`SR` upward and downward secondary reserve            €/MW      «``pOperatingReservePrice_Up_SR``, ``pOperatingReservePrice_Down_SR``»
:math:`UR^{SR}_{n},  DR^{SR}_{n}`              Requirement for :math:`SR` upward and downward secondary reserve     €/MW      «``pOperatingReserveRequire_Up_SR``, ``pOperatingReserveRequire_Down_SR``»
:math:`UEI^{TR}_{n}, DEI^{TR}_{n}`             Expected income of :math:`TR` upward and downward tertiary reserve   €/MW      «``pOperatingReservePrice_Up_TR``, ``pOperatingReservePrice_Down_TR``»
:math:`CENS`                                   Cost of electricity not served. Value of Lost Load (VoLL)            €/MWh     «``pParENSCost``»
:math:`CHNS`                                   Cost of hydrogen not served.                                         €/tH2     «``pParHNSCost``»
=============================================  ===================================================================  ========  ===========================================================================

==============  =============================  ========  ===========================================================================
**Scenarios**   **Description**                **Unit**  **oHySEM.py**
--------------  -----------------------------  --------  ---------------------------------------------------------------------------
:math:`P^ω`     Probability of each scenario   p.u.      «``pScenProb``»
==============  =============================  ========  ===========================================================================

==========================================================================================  =======================================================================================================  ===========  =======================================================================================================
**Generation system**                                                                       **Description**                                                                                          **Unit**     **oHySEM.py**
------------------------------------------------------------------------------------------  -------------------------------------------------------------------------------------------------------  -----------  -------------------------------------------------------------------------------------------------------
:math:`\underline{EP}_{neg},     \overline{EP}_{neg}`                                       Minimum and maximum electricity generation  of a generator                                               MWh          «``pMaxPower``, ``pMinPower``»
:math:`\widehat{EP}_{neg}`                                                                  Last update of the position in the market of the electricity generation of a generator                   MWh          «``pVarPositionGeneration``»
:math:`\underline{EC}_{neg},     \overline{EC}_{neg}`                                       Minimum and maximum electricity consumption of an ESS                                                    MWh          «``pMaxCharge``, ``pMinCharge``»
:math:`\overline{EC}^{comp}_{nhs}`                                                          Maximum electricity consumption of a compressor unit to compress hydrogen                                MWh          «``pGenMaxCompressorConsumption``»
:math:`\overline{EC}^{standby}_{nhz}`                                                       Maximum electricity consumption of an electrolyzer unit during the standby mode                          MWh          «``pGenStandByPower``»
:math:`\widehat{EC}_{neg}`                                                                  Last update of the position in the market of the electricity consumption of a generator                  MWh          «``pVarPositionConsumption``»
:math:`\underline{EI}_{neg},     \overline{EI}_{neg}`                                       Maximum and minimum electricity storage  of an ESS                                                       MWh          «``pMaxStorage``, ``pMinStorage``»
:math:`\underline{EEO}_{neg},    \overline{EEO}_{neg}`                                      Maximum and minimum electricity outflows of an ESS (e.g., kg of H2)                                      MW           «``pMaxOutflows``, ``pMinOutflows``»
:math:`\underline{EEI}_{neg},    \overline{EEI}_{neg}`                                      Maximum and minimum electricity inflows  of an ESS                                                       MW           «``pMaxInflows``, ``pMinInflows``»
:math:`\underline{HP}_{nhg},     \overline{HP}_{nhg}`                                       Minimum and maximum hydrogen generation  of a generator                                                  kgH2         «``pMaxPower``, ``pMinPower``»
:math:`\widehat{HP}_{nhg}`                                                                  Last update of the position in the market of the hydrogen generation of a generator                      MWh          «``pVarPositionGeneration``»
:math:`\underline{HC}_{nhg},     \overline{HC}_{nhg}`                                       Minimum and maximum hydrogen consumption of an ESS                                                       kgH2         «``pMaxCharge``, ``pMinCharge``»
:math:`\widehat{HC}_{nhg}`                                                                  Last update of the position in the market of the hydrogen consumption of a generator                     kgH2         «``pVarPositionConsumption``»
:math:`\underline{HI}_{nhg},     \overline{HI}_{nhg}`                                       Maximum and minimum hydrogen storage     of an ESS                                                       kgH2         «``pMaxStorage``, ``pMinStorage``»
:math:`\underline{HEO}_{nhg},    \overline{HEO}_{nhg}`                                      Maximum and minimum hydrogen outflows    of an ESS                                                       kgH2         «``pMaxOutflows``, ``pMinOutflows``»
:math:`\underline{HEI}_{nhg},    \overline{HEI}_{nhg}`                                      Maximum and minimum hydrogen inflows     of an ESS (e.g., kg of H2)                                      kgH2         «``pMaxInflows``, ``pMinInflows``»
:math:`CF_g, CV_g`                                                                          Fixed and variable cost of an electricity generator. Variable cost includes fuel, O&M and emission cost  €/h, €/MWh   «``pGenConstantVarCost``, ``pGenLinearVarCost``»
:math:`RU_t, RD_t`                                                                          Ramp up and ramp down of an electricity thermal unit                                                     MW/h         «``pGenRampUp``, ``pGenRampDown``»
:math:`RC^{+}_{hz}, RC^{-}_{hz}`                                                            Ramp up and ramp down of a hydrogen unit                                                                 kgH2/h       «``pGenRampUp``, ``pGenRampDown``»
:math:`TU_t, TD_t`                                                                          Minimum uptime and downtime of an electricity thermal unit                                               h            «``pGenUpTime``, ``pGenDownTime``»
:math:`CSU_g, CSD_g`                                                                        Startup and shutdown cost of an electricity committed unit                                               M€           «``pGenStartUpCost``, ``pGenShutDownCost``»
:math:`CRU_h, CRD_h`                                                                        Ramp up and ramp down cost of a hydrogen unit                                                            M€/MWh       «``pGenRampUpCost``, ``pGenRampDownCost``»
:math:`EF_e`                                                                                Round-trip efficiency of the charge/discharge of an electricity ESS                                      p.u.         «``pGenEfficiency``»
:math:`EF_h`                                                                                Round-trip efficiency of the charge/discharge of a hydrogen ESS                                          p.u.         «``pGenEfficiency``»
:math:`PF_{he}`                                                                             Production function of electricity from hydrogen                                                         kWh/kgH2     «``pGenProductionFunction``»
:math:`PF_{eh}`                                                                             Production function of hydrogen from electricity                                                         kgH2/kWh     «``pGenProductionFunction``»
:math:`URA^{SR}_{n}, DRA^{SR}_{n}`                                                          :math:`SR` upward and downward activation                                                                p.u.         «``pOperatingReserveActivation_Up_SR``, ``pOperatingReserveActivation_Down_SR``»
:math:`URA^{TR}_{n}, DRA^{TR}_{n}`                                                          :math:`TR` upward and downward activation                                                                p.u.         «``pOperatingReserveActivation_Up_TR``, ``pOperatingReserveActivation_Down_TR``»
==========================================================================================  =======================================================================================================  ===========  =======================================================================================================

==========================================================================================  =======================================================================================================  ===========  =======================================================================================================
**Network system**                                                                          **Description**                                                                                          **Unit**     **oHySEM.py**
------------------------------------------------------------------------------------------  -------------------------------------------------------------------------------------------------------  -----------  -------------------------------------------------------------------------------------------------------
:math:`\underline{ENF}_{nijc}, \overline{ENF}_{nijc}`                                       Minimum and maximum electricity network flow through the line ijc                                        MWh          «``pEleNetTTCBck``, ``pEleNetTTC``»
:math:`\underline{HNF}_{nijc}, \overline{HNF}_{nijc}`                                       Minimum and maximum hydrogen network flow through the line ijc                                           MWh          «``pHydNetTTCBck``, ``pHydNetTTC``»
:math:`\overline{X}_{nijc}`                                                                 Reactance of the line ijc                                                                                p.u.         «``pEleNetReactance``»
==========================================================================================  =======================================================================================================  ===========  =======================================================================================================

Variables
---------

They are written in **lowercase** letters.

==========================================    ======================================================  ========  ============================================
**Demand**                                    **Description**                                         **Unit**  **oHySEM.py**
------------------------------------------    ------------------------------------------------------  --------  --------------------------------------------
:math:`e^{b}_{nnd}, e^{s}_{nnd}`              Electricity bought and sold in the electricity market   GW        «``vElectricityBuy``, ``vElectricitySell``»
:math:`ens_{nnd}`                             Electricity not served                                  GW        «``vENS``»
:math:`ed_{nnd}`                              Electricity demand                                      GW        «``vEleTotalDemand``»
:math:`ed^{\Delta}_{nnd}`                     Electricity demand due to market correction             GW        «``vEleTotalDemandDelta``»
:math:`h^{b}_{nnd}, h^{s}_{nnd}`              Hydrogen bought and sold in the hydrogen market         kgH2      «``vHydrogenBuy``, ``vHydrogenSell``»
:math:`hns_{nnd}`                             Hydrogen not served                                     kgH2      «``vHNS``»
:math:`hd_{nnd}`                              Hydrogen demand                                         kgH2      «``vHydTotalDemand``»
:math:`hd^{\Delta}_{nnd}`                     Hydrogen demand due to market correction                kgH2      «``vHydTotalDemandDelta``»
==========================================    ======================================================  ========  ============================================

==============================================  ==========================================================================================  ========  ==========================================================
**Generation system**                           **Description**                                                                             **Unit**  **oHySEM.py**
----------------------------------------------  ------------------------------------------------------------------------------------------  --------  ----------------------------------------------------------
:math:`ep_{neg}`                                Electricity production (discharge if an ESS)                                                GW        «``vEleTotalOutput``»
:math:`ec_{nes}, ec_{nhz}`                      Electricity consumption of electricity ESS and electrolyzer units                           GW        «``vEleTotalCharge``»
:math:`ep2b_{neg}`                              Electricity production of the second block (i.e., above the minimum load)                   GW        «``vEleTotalOutput2ndBlock``»
:math:`ec2b_{nes}, ec2b_{nhz}`                  Electricity charge of the second block (i.e., above the minimum charge)                     GW        «``vEleTotalCharge2ndBlock``»
:math:`ep^{\Delta}_{neg}`                       Electricity production (discharge if an ESS) for market correction                          GW        «``vEleTotalOutputDelta``»
:math:`ec^{\Delta}_{nes}, ec^{\Delta}_{nhz}`    Electricity consumption of electricity ESS and electrolyzer units for market correction     GW        «``vEleTotalChargeDelta``»
:math:`ec^{R+}_{nes}, ec^{R+}_{nhz}`            Positive ramp of electricity consumption of an ESS and electrolyzer                         GW        «``vEleTotalChargeRampPos``»
:math:`ec^{R-}_{nes}, ec^{R-}_{nhz}`            Negative ramp of electricity consumption of an ESS and electrolyzer                         GW        «``vEleTotalChargeRampNeg``»
:math:`eei_{nes}`                               Electricity inflows of an ESS                                                               GWh       «``vEleEnergyInflows``»
:math:`eeo_{nes}`                               Electricity outflows of an ESS                                                              GWh       «``vEleEnergyOutflows``»
:math:`esi_{nes}`                               Electricity ESS stored energy (inventory, SoC for batteries)                                GWh       «``vEleInventory``»
:math:`ess_{nes}`                               Electricity ESS spilled energy                                                              GWh       «``vEleSpillage``»
:math:`hp_{nhg}`                                Hydrogen production (discharge if an ESS)                                                   kgH2      «``vHydTotalOutput``»
:math:`hc_{nhs}, hc_{neg}`                      Hydrogen consumption of hydrogen ESS and electricity thermal units                          kgH2      «``vHydTotalCharge``»
:math:`hp2b_{nhg}`                              Hydrogen production of the second block (i.e., above the minimum load)                      kgH2      «``vHydTotalOutput2ndBlock``»
:math:`hc2b_{nhs}, hc2b_{neg}`                  Hydrogen charge of the second block (i.e., above the minimum charge)                        kgH2      «``vHydTotalCharge2ndBlock``»
:math:`hp^{\Delta}_{nhg}`                       Hydrogen production (discharge if an ESS) for market correction                             kgH2      «``vHydTotalOutputDelta``»
:math:`hc^{\Delta}_{nhs}, hc^{\Delta}_{neg}`    Hydrogen consumption of hydrogen ESS and electricity thermal units for market correction    kgH2      «``vHydTotalChargeDelta``»
:math:`hei_{nhs}`                               Hydrogen inflows of an ESS                                                                  GWh       «``vHydEnergyInflows``»
:math:`heo_{nhs}`                               Hydrogen outflows of an ESS                                                                 GWh       «``vHydEnergyOutflows``»
:math:`hsi_{nhs}`                               Hydrogen ESS stored energy (inventory, SoC for batteries)                                   GWh       «``vHydInventory``»
:math:`hss_{nhs}`                               Hydrogen ESS spilled energy                                                                 GWh       «``vHydSpillage``»
:math:`ec^{Comp}_{nhs}`                         Electricity consumption of a compressor unit to compress hydrogen                           kgH2      «``vHydCompressorConsumption``»
:math:`ec^{StandBy}_{nhz}`                      Electricity consumption of a electrolyzer unit during the standby mode                      kgH2      «``vHydStandByConsumption``»
:math:`up^{SR}_{neg}, dp^{SR}_{neg}`            Upward and downward :math:`SR` operating reserves of a generating or ESS unit               GW        «``vEleReserveProd_Up_SR``, ``vEleReserveProd_Down_SR``»
:math:`uc^{SR}_{nes}, dc^{SR}_{nes}`            Upward and downward :math:`SR` operating reserves of an ESS as a consumption unit           GW        «``vEleReserveCons_Up_SR``, ``vEleReserveCons_Down_SR``»
:math:`up^{TR}_{ωneg}, dp^{TR}_{ωneg}`          Upward and downward :math:`TR` operating reserves of a generating or ESS unit               GW        «``vEleReserveProd_Up_TR``, ``vEleReserveProd_Down_TR``»
:math:`uc^{TR}_{ωnes}, dc^{TR}_{ωnes}`          Upward and downward :math:`TR` operating reserves of an ESS as a consumption unit           GW        «``vEleReserveCons_Up_TR``, ``vEleReserveCons_Down_TR``»
:math:`euc_{neg}, esu_{neg}, esd_{neg}`         Commitment, startup and shutdown of electricity generation unit per load level              {0,1}     «``vGenCommitment``, ``vGenStartup``, ``vGenShutdown``»
:math:`euc^{max}_{neg}`                         Maximum commitment of electricity generation unit per load level                            {0,1}     «``vGenMaxCommitment``»
:math:`huc_{nhg}`                               Commitment of hydrogen generation unit per load level                                       {0,1}     «``vHydCommitment``, ``vHydStartup``, ``vHydShutdown``»
:math:`huc^{max}_{nhg}`                         Maximum commitment of hydrogen generation unit per load level                                {0,1}     «``vHydMaxCommitment``»
:math:`esf_{nes}`                               Electricity ESS energy functioning per load level, charging or discharging                  {0,1}     «``vEleStorOperat``»
:math:`hsf_{nhs}`                               Hydrogen ESS energy functioning per load level, charging or discharging                     {0,1}     «``vHydStorOperat``»
:math:`hcf_{nhs}`                               Hydrogen compressor functioning, off or on                                                  {0,1}     «``vHydCompressorOperat``»
:math:`hsb_{nhg}`                               Hydrogen electrolyzer StandBy mode, off or on                                               {0,1}     «``vHydStandBy``»
==============================================  ==========================================================================================  ========  ==========================================================

==========================================  ==========================================================================================  ========  ============================================
**Network system**                          **Description**                                                                             **Unit**  **oHySEM.py**
------------------------------------------  ------------------------------------------------------------------------------------------  --------  --------------------------------------------
:math:`ef_{nijc}`                           Electricity transmission flow through a line                                                GW        «``vEleNetFlow``»
:math:`hf_{nijc}`                           Hydrogen transmission flow through a pipeline                                               kgH2      «``vHydNetFlow``
:math:`theta_{ni}`                          Voltage angle of a node                                                                     rad       «``vEleNetTheta``»
==========================================  ==========================================================================================  ========  ============================================

Equations
---------

This formulation corresponds to a **Rolling horizon optimization problem** to schedule the operation of the electricity and hydrogen systems in a multi-energy system. The model is enabled to consider previous information from the Day-Ahead (DA) market, Intraday (ID) markets, and Real-Time (RT) market, and correct the market positions of the systems.
The model is solved using a rolling horizon approach: once the DA market is cleared, the model is solved for the next ID markets, and so on.

**Objective function**: minimization of operation cost for the scope of the model

Market variable cost in [M€] («``eTotalMCost``»)

:math:`\sum_{nnd}DUR_n (CEB_{nnd} e^{b}_{nnd} - PES_{nnd} e^{s}_{nnd} + CHB_{nnd} h^{b}_{nnd} - PHS_{nnd} h^{s}_{nnd} + CENS ens_{nnd} + CHNS hns_{nnd}) +`

Generation operation cost [M€] («``eTotalGCost``»)

:math:`\sum_{neg}DUR_n (CV_g ep_{neg} + CF_g euc_{neg} + CF_h (huc_{nhz} - hsb_{nhz}) + CRU_h ec^{R+}_{nhz} + CSU_g esu_{neg} + CSD_g esd_{neg} + CSU_h hsu_{nhz} + CSD_h hsd_{nhz}) +`

Generation emission cost [M€] («``eTotalECost``»)

:math:`\sum_{neg}DUR_n CE_g ep_{neg} +`

Consumption operation cost [M€] («``eTotalCCost``»)

:math:`\sum_{n}DUR_n (\sum_{es} CV_{es} ec_{nes} + \sum_{hz} CV_{hz}  ec_{nhz}) -`

Operation reserve revenue [M€] («``eTotalRCost``»)operation

:math:`\sum_{neg}  UP^{SR}_{n} up^{SR}_{neg}  + DP^{SR}_{n} dp^{SR}_{neg}  + DUR_n (UEI^{SR}_{n} URA^{SR}_{n} up^{SR}_{neg}  + DEI^{SR}_{n} DRA^{SR}_{n} dp^{SR}_{neg}  + UEI^{TR}_{n} URA^{TR}_{n} up^{TR}_{neg}  + DEI^{TR}_{n} DRA^{TR}_{n} dp^{TR}_{neg}) +`

:math:`\sum_{nes} UP^{SR}_{n} uc^{SR}_{nes} + DP^{SR}_{n} dc^{SR}_{nes} + DUR_n (UEI^{SR}_{n} URA^{SR}_{n} uc^{SR}_{nes} + DEI^{SR}_{n} DRA^{SR}_{n} dc^{SR}_{nes} + UEI^{TR}_{n} URA^{TR}_{n} uc^{TR}_{nes} + DEI^{TR}_{n} DRA^{TR}_{n} dc^{TR}_{nes}) +`

**Constraints**
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Corrections of the units in the electricity and hydrogen markets:

- Electricity production («``eMarketCorrectionEleProd``»)

:math:`ep_{neg} = \widehat{EP}_{neg} + ep^{\Delta}_{neg} \quad \forall neg`

- Electricity consumption («``eMarketCorrectionEleCharge``»)

:math:`ec_{nes} = \widehat{EC}_{nes} + ec^{\Delta}_{nes} \quad \forall nes`

- Hydrogen production («``eMarketCorrectionHydProd``»)

:math:`ec_{nhz} = \widehat{EC}_{nhz} + ec^{\Delta}_{nhz} \quad \forall nhz`

- Hydrogen consumption («``eMarketCorrectionHydCharge``»)

:math:`hp_{neg} = \widehat{HP}_{nhg} + hp^{\Delta}_{nhg} \quad \forall nhg`

- Electricity consumption («``eMarketCorrectionEleCharge``»)

:math:`hc_{nes} = \widehat{HC}_{nhs} + hc^{\Delta}_{nhs} \quad \forall nhs`

- Hydrogen demand («``eMarketCorrectionHydDemand``»)

:math:`hc_{net} = \widehat{HC}_{net} + hc^{\Delta}_{net} \quad \forall net`

Electricity balance of generation and demand [GW] («``eElectricityBalance``»)

:math:`\sum_{g\in nd} ep_{neg} - \sum_{es\in nd} ec_{nes} - \sum_{hz\in nd} (ec_{nhz} + ec^{StandBy}_{nhz}) - \sum_{hs\in nd} (ec^{Comp}_{nhs}) + ens_{nnd} + eb_{nnd} - es_{nnd} = ED_{nnd} + \sum_{jc} ef_{nndjc} - \sum_{jc} ef_{njndc} \quad \forall nnd`

Hydrogen balance of generation and demand [GW] («``eHydrogenBalance``»)

:math:`\sum_{h\in nd} hp_{nhg} - \sum_{hs\in nd} hc_{nhs} - \sum_{g\in nd} hc_{net} + hns_{nnd} + hb_{nnd} - hs_{nnd} = HD_{nnd} + \sum_{jc} hf_{nndjc} - \sum_{jc} hf_{njndc} \quad \forall nnd`

Upward and downward operating secondary reserves provided by non-renewable generators, and ESS when charging for each area [GW] («``eReserveRequire_Up_SR``, ``eReserveRequire_Dw_SR``»)

:math:`\sum_{neg} up^{SR}_{neg} + \sum_{nes} uc^{SR}_{nes} \leq UR^{SR}_{n} \quad \forall n`

:math:`\sum_{neg} dp^{SR}_{neg} + \sum_{nes} dc^{SR}_{nes} \leq DR^{SR}_{n} \quad \forall n`

Upward and downward operating tertiary reserves provided by non-renewable generators, and ESS when charging for each area [GW] («``eReserveRequire_Up_TR``, ``eReserveRequire_Dw_TR``»)

:math:`\sum_{neg} up^{TR}_{neg} + \sum_{nes} uc^{TR}_{nes} \leq UR^{TR}_{n} \quad \forall n`

:math:`\sum_{neg} dp^{TR}_{neg} + \sum_{nes} dc^{TR}_{nes} \leq DR^{TR}_{n} \quad \forall n`

operating reserves from ESS can only be provided if enough energy is available for producing [GW] («``eReserveUpIfEnergyProd``, ``eReserveDwIfEnergyProd``»)

:math:`URA^{SR}_{n}up^{SR}_{nes} + URA^{TR}_{n}up^{TR}_{nes} \leq \frac{                      esi_{nes}}{DUR_n} \quad \forall nes`

:math:`DRA^{SR}_{n}dp^{SR}_{nes} + DRA^{TR}_{n}dp^{TR}_{nes} \leq \frac{\overline{EI}_{nes} - esi_{nes}}{DUR_n} \quad \forall nes`

or for storing [GW] («``eReserveUpIfEnergyCons``, ``eReserveDwIfEnergyCons``»)

:math:`URA^{SR}_{n}uc^{SR}_{nes} + URA^{TR}_{n}uc^{TR}_{nes} \leq \frac{\overline{EI}_{nes} - esi_{nes}}{DUR_n} \quad \forall nes`

:math:`DRA^{SR}_{n}dc^{SR}_{nes} + DRA^{TR}_{n}dc^{TR}_{nes} \leq \frac{                      esi_{nes}}{DUR_n} \quad \forall nes`

Maximum and minimum relative inventory of ESS (only for load levels multiple of 1, 24, 168, 8736 h depending on the ESS storage type) constrained by the ESS commitment decision times the maximum capacity [p.u.] («``eMaxInventory2Comm``, ``eMinInventory2Comm``»)

:math:`\frac{esi_{nes}}{\overline{EI}_{nes}}  \leq euc_{nes} \quad \forall nes`

:math:`\frac{esi_{nes}}{\underline{EI}_{nes}} \geq euc_{nes} \quad \forall nes`

:math:`\frac{hsi_{nhs}}{\overline{HI}_{nhs}}  \leq huc_{nhs} \quad \forall nhs`

:math:`\frac{hsi_{nhs}}{\underline{HI}_{nhs}} \geq huc_{nhs} \quad \forall nhs`

Energy inflows of ESS (only for load levels multiple of 1, 24, 168, 8736 h depending on the ESS storage type) constrained by the ESS commitment decision times the inflows data [p.u.] («``eMaxInflows2Commitment``, ``eMinInflows2Commitment``»)

:math:`\frac{eei_{nes}}{EEI_{nes}} \leq euc_{nes} \quad \forall nes`

:math:`\frac{hei_{nhs}}{HEI_{nhs}} \leq huc_{nhs} \quad \forall nhs`

ESS energy inventory (only for load levels multiple of 1, 24, 168 h depending on the ESS storage type) [GWh] («``eEleInventory``, ``eHydInventory``»)

:math:`esi_{n-\frac{\tau_e}{\nu},es} + \sum_{n' = n-\frac{\tau_e}{\nu}}^n DUR_{n'} (eei_{n'es} - eeo_{n'es} - ep_{n'es} + EF_{es} ec_{n'es}) = esi_{nes} + ess_{nes} \quad \forall nes`

:math:`hsi_{n-\frac{\tau_h}{\nu},hs} + \sum_{n' = n-\frac{\tau_h}{\nu}}^n DUR_{n'} (hei_{n'hs} - heo_{n'hs} - hp_{n'hs} + EF_{hs} hc_{n'hs}) = hsi_{nhs} + hss_{nhs} \quad \forall nhs`

Energy conversion from energy from electricity to hydrogen and vice versa [p.u.] («``eAllEnergy2Ele``, ``eAllEnergy2Hyd``»)

:math:`ep_{neg} = PF_{he} hc_{neg} \quad \forall neg`

:math:`hp_{nhz} = PF_{eh} gc_{nhz} \quad \forall nhz`

Relationship between electricity outflows and commitment of the units [p.u.] («``eMaxEleOutflows2Commitment``, ``eMinEleOutflows2Commitment``»)

:math:`\frac{eeo_{nes}}{\overline{EEO}_{nes}} \leq euc_{nes} \quad \forall nes`

:math:`\frac{eeo_{nes}}{\underline{EEO}_{nes}} \geq euc_{nes} \quad \forall nes`

Relationship between hydrogen outflows and commitment of the units [p.u.] («``eMaxHydOutflows2Commitment``, ``eMinHydOutflows2Commitment``»)

:math:`\frac{heo_{nhs}}{\overline{HEO}_{nhs}} \leq huc_{nhs} \quad \forall nhs`

:math:`\frac{heo_{nhs}}{\underline{HEO}_{nhs}} \geq huc_{nhs} \quad \forall nhs`

ESS electricity outflows (only for load levels multiple of 1, 24, 168, 672, and 8736 h depending on the ESS outflow cycle) must be satisfied [GWh] («``eEleEnergyOutflows``»)

:math:`\sum_{n' = n-\frac{\tau_e}{\rho_e}}^n DUR_{n'} (eeo_{n'es} - EEO_{n'es}) = 0 \quad \forall nes, n \in \rho_e`

ESS hydrogen minimum and maximum outflows (only for load levels multiple of 1, 24, 168, 672, and 8736 h depending on the ESS outflow cycle) must be satisfied [GWh] («``eHydMinEnergyOutflows``, ``eHydMaxEnergyOutflows``»)

:math:`\sum_{n' = n-\frac{\tau_h}{\rho_h}}^n DUR_{n'} (heo_{n'hs} - HEO_{n'hs}) \geq 0 \quad \forall nhs, n \in \rho_h`

:math:`\sum_{n' = n-\frac{\tau_h}{\rho_h}}^n DUR_{n'} (heo_{n'hs} - HEO_{n'hs}) \leq 0 \quad \forall nhs, n \in \rho_h`

Demand cycle target [GWh] («``eHydDemandCycleTarget``»)

:math:`\sum_{n' = n-\frac{\tau_d}{\nu}}^n DUR_{n'} (hd_{n'nd} - HD_{n'nd}) = 0 \quad \forall nnd, n \in \rho_d`

Maximum and minimum electricity generation of the second block of a committed unit (all except the VRE and ESS units) [p.u.] («``eMaxEleOutput2ndBlock``, ``eMinEleOutput2ndBlock``»)

* D.A. Tejada-Aranego, S. Lumbreras, P. Sánchez-Martín, and A. Ramos "Which Unit-Commitment Formulation is Best? A Systematic Comparison" IEEE Transactions on Power Systems 35 (4):2926-2936 Jul 2020 `10.1109/TPWRS.2019.2962024 <https://doi.org/10.1109/TPWRS.2019.2962024>`_

* C. Gentile, G. Morales-España, and A. Ramos "A tight MIP formulation of the unit commitment problem with start-up and shut-down constraints" EURO Journal on Computational Optimization 5 (1), 177-201 Mar 2017. `10.1007/s13675-016-0066-y <https://doi.org/10.1007/s13675-016-0066-y>`_

* G. Morales-España, A. Ramos, and J. Garcia-Gonzalez "An MIP Formulation for Joint Market-Clearing of Energy and Reserves Based on Ramp Scheduling" IEEE Transactions on Power Systems 29 (1): 476-488, Jan 2014. `10.1109/TPWRS.2013.2259601 <https://doi.org/10.1109/TPWRS.2013.2259601>`_

* G. Morales-España, J.M. Latorre, and A. Ramos "Tight and Compact MILP Formulation for the Thermal Unit Commitment Problem" IEEE Transactions on Power Systems 28 (4): 4897-4908, Nov 2013. `10.1109/TPWRS.2013.2251373 <https://doi.org/10.1109/TPWRS.2013.2251373>`_

:math:`\frac{ep2b_{net} + up^{SR}_{net} + up^{TR}_{net}}{\overline{EP}_{net} - \underline{EP}_{net}} \leq euc_{net} \quad \forall net`

:math:`\frac{ep2b_{net} - dp^{SR}_{net} - dp^{TR}_{net}}{\overline{EP}_{net} - \underline{EP}_{net}} \geq 0         \quad \forall net`

Maximum and minimum hydrogen generation of the second block of a committed unit [p.u.] («``eMaxHydOutput2ndBlock``, ``eMinHydOutput2ndBlock``»)

:math:`\frac{hp2b_{nhg}}{\overline{HP}_{nhg} - \underline{HP}_{nhg}} \leq huc_{nhg} \quad \forall nhg`

:math:`\frac{hp2b_{nhg}}{\overline{HP}_{nhg} - \underline{HP}_{nhg}} \geq 0         \quad \forall nhg`

Maximum and minimum discharge of the second block of an electricity ESS [p.u.] («``eMaxEleESSOutput2ndBlock``, ``eMinEleESSOutput2ndBlock``»)

:math:`\frac{ep2b_{nes} + up^{SR}_{nes} + up^{TR}_{nes}}{\overline{EP}_{nes} - \underline{EP}_{nes}} \leq 1 \quad \forall nes`

:math:`\frac{ep2b_{nes} - dp^{SR}_{nes} - dp^{TR}_{nes}}{\overline{EP}_{nes} - \underline{EP}_{nes}} \geq 0 \quad \forall nes`

Maximum and minimum discharge of the second block of a hydrogen ESS [p.u.] («``eMaxHydESSOutput2ndBlock``, ``eMinHydESSOutput2ndBlock``»)

:math:`\frac{hp2b_{nhs}}{\overline{HP}_{nhs} - \underline{HP}_{nhs}} \leq 1 \quad \forall nhs`

:math:`\frac{hp2b_{nhs}}{\overline{HP}_{nhs} - \underline{HP}_{nhs}} \geq 0 \quad \forall nhs`

Maximum and minimum charge of the second block of an electricity ESS [p.u.] («``eMaxEleESSCharge2ndBlock``, ``eMinEleESSCharge2ndBlock``»)

:math:`\frac{ec2b_{nes} + dc^{SR}_{nes} + dc^{TR}_{nes}}{\overline{EC}_{nes} - \underline{EC}_{nes}} \leq 1 \quad \forall nes`

:math:`\frac{ec2b_{nes} - uc^{SR}_{nes} - uc^{TR}_{nes}}{\overline{EC}_{nes} - \underline{EC}_{nes}} \geq 0 \quad \forall nes`

Maximum and minimum charge of the second block of a hydrogen unit due to the energy conversion [p.u.] («``eMaxEle2HydCharge2ndBlock``, ``eMinEle2HydCharge2ndBlock``»)

:math:`\frac{ec2b_{nhz} + dc^{SR}_{nhz} + dc^{TR}_{nhz}}{\overline{EC}_{nhz}} \leq 1 \quad \forall nhz`

:math:`\frac{ec2b_{nhz} - uc^{SR}_{nhz} - uc^{TR}_{nhz}}{\overline{EC}_{nhz}} \geq 0 \quad \forall nhz`

Maximum and minimum charge of the second block of a hydrogen ESS [p.u.] («``eMaxHydESSCharge2ndBlock``, ``eMinHydESSCharge2ndBlock``»)

:math:`\frac{hc2b_{nhs}}{\overline{HC}_{nhs} - \underline{HC}_{nhs}} \leq 1 \quad \forall nhs`

:math:`\frac{hc2b_{nhs}}{\overline{HC}_{nhs} - \underline{HC}_{nhs}} \geq 0 \quad \forall nhs`

Incompatibility between charge and discharge of an ESS [p.u.] («``eEleChargingDecision``, ``eEleDischargingDecision``»)

:math:`\frac{ec_{nes}}{\overline{EC}_{nes}} \leq esf_{nes} \quad \forall nes`

:math:`\frac{ep_{nes}}{\overline{EP}_{nes}} \leq 1 - esf_{nes} \quad \forall nes`

Upward operating reserve decision of an ESS when it is consuming and constrained by charging and discharging itself [p.u.] («``eReserveConsChargingDecision_Up``»)

:math:`\frac{uc^{SR}_{nes} + uc^{TR}_{nes}}{\overline{EC}_{nes}} \leq esf_{nes} \quad \forall nes`

Upward operating reserve decision of an ESS when it is producing and constrained by charging and discharging itself [p.u.] («``eReserveProdDischargingDecision_Up``»)

:math:`\frac{up^{SR}_{nes} + up^{TR}_{nes}}{\overline{EP}_{nes}} \leq esf_{nes} \quad \forall nes`

Downward operating reserve decision of an ESS when it is consuming and constrained by charging and discharging itself [p.u.] («``eReserveConsChargingDecision_Dw``»)

:math:`\frac{dc^{SR}_{nes} + dc^{TR}_{nes}}{\overline{EC}_{nes}} \leq 1 - esf_{nes} \quad \forall nes`

Downward operating reserve decision of an ESS when it is producing and constrained by charging and discharging itself [p.u.] («``eReserveProdDischargingDecision_Dw``»)

:math:`\frac{dp^{SR}_{nes} + dp^{TR}_{nes}}{\overline{EP}_{nes}} \leq 1 - esf_{nes} \quad \forall nes`

Energy stored for upward operating reserve in consecutive time steps when ESS is consuming [GWh] («``eReserveConsUpConsecutiveTime``»)

:math:`\sum_{n' = n-\frac{\tau_e}{\nu}}^n DUR_{n'} (uc^{SR}_{nes} + uc^{TR}_{nes}) \leq \overline{EC}_{nes} - esi_{nes} \quad \forall nes`

Energy stored for downward operating reserve in consecutive time steps when ESS is consuming [GWh] («``eReserveConsDwConsecutiveTime``»)

:math:`\sum_{n' = n-\frac{\tau_e}{\nu}}^n DUR_{n'} (dc^{SR}_{nes} + dc^{TR}_{nes}) \leq esi_{nes} - \underline{EC}_{nes} \quad \forall nes`

Energy stored for upward operating reserve in consecutive time steps when ESS is producing [GWh] («``eReserveProdUpConsecutiveTime``»)

:math:`\sum_{n' = n-\frac{\tau_e}{\nu}}^n DUR_{n'} (up^{SR}_{nes} + up^{TR}_{nes}) \leq \overline{EP}_{nes} - esi_{nes} \quad \forall nes`

Energy stored for downward operating reserve in consecutive time steps when ESS is producing [GWh] («``eReserveProdDwConsecutiveTime``»)

:math:`\sum_{n' = n-\frac{\tau_e}{\nu}}^n DUR_{n'} (dp^{SR}_{nes} + dp^{TR}_{nes}) \leq esi_{nes} - \underline{EP}_{nes} \quad \forall nes`

Incompatibility between charge and discharge of a hydrogen ESS [p.u.] («``eHydChargingDecision``, ``eHydDischargingDecision``»)

:math:`\frac{hc_{nhs}}{\overline{HC}_{nhs}} \leq hsf_{nhs} \quad \forall nhs`

:math:`\frac{hp_{nhs}}{\overline{HP}_{nhs}} \leq 1 - hsf_{nhs} \quad \forall nhs`

Total generation of an electricity unit (all except the VRE units) [GW] («``eEleTotalOutput``»)

:math:`\frac{ep_{neg}}{\underline{EP}_{neg}} = euc_{neg} + \frac{ep2b_{neg} + URA^{SR}_{n}up^{SR}_{nes} + URA^{TR}_{n}up^{TR}_{nes} - DRA^{SR}_{n}dp^{SR}_{nes} - DRA^{TR}_{n}dp^{TR}_{nes}}{\underline{EP}_{neg}} \quad \forall neg`

Total generation of a hydrogen unit [kgH2] («``eHydTotalOutput``»)

:math:`\frac{hp_{nhg}}{\underline{HP}_{nhg}} = huc_{nhg} + \frac{hp2b_{nhz}}{\underline{HP}_{nhg}} \quad \forall nh`

Total charge of an electricity ESS [GW,kgH2] («``eEleTotalCharge``»)

:math:`\frac{ec_{nes}}{\underline{EC}_{nes}} = 1 + \frac{ec2b_{nes} - URA^{SR}_{n}uc^{SR}_{nes} - URA^{TR}_{n}uc^{TR}_{nes} + DRA^{SR}_{n}dc^{SR}_{nes} + DRA^{TR}_{n}dc^{TR}_{nes}}{\underline{EC}_{nes}} \quad \forall nes`

Total charge of a hydrogen unit [kgH2] («``eHydTotalCharge``»)

:math:`\frac{hc_{nhs}}{\underline{HC}_{nhs}} = 1 + \frac{hc2b_{nhs}}{\underline{EC}_{nhs}} \quad \forall nhs`

Incompatibility between charge and outflows use of an electricity ESS [p.u.] («``eIncompatibilityEleChargeOutflows``»)

:math:`\frac{eeo_{nes} + ec2b_{nes}}{\overline{EC}_{nes} - \underline{EC}_{nes}} \leq 1 \quad \forall nes`

Incompatibility between charge and outflows use of a hydrogen ESS [p.u.] («``eIncompatibilityHydChargeOutflows``»)

:math:`\frac{heo_{nhs} + hc2b_{nhs}}{\overline{HC}_{nhs} - \underline{HC}_{nhs}} \leq 1 \quad \forall nhs`

Logical relation between commitment, startup and shutdown status of a committed electricity unit (all except the VRE units) [p.u.] («``eEleCommitmentStartupShutdown``»)
Initial commitment of the units is determined by the model based on the merit order loading, including the VRE and ESS units.

:math:`euc_{neg} - euc_{n-\nu,g} = esu_{neg} - esd_{neg} \quad \forall neg`

Maximum commitment of an electricity unit (all except the VRE units) [p.u.] («``eEleMaxCommitment``»)

:math:`euc_{neg} \leq sum_{n' = n-\nu-TU_t}^n euc^{max}_{n't} \quad \forall neg`

Logical relation between commitment, startup and shutdown status of a committed hydrogen unit [p.u.] («``eHydCommitmentStartupShutdown``»)

:math:`huc_{nhg} - huc_{n-\nu,hg} = hsu_{nhg} - hsd_{nhg} \quad \forall nhg`

Maximum ramp up and ramp down for the second block of a non-renewable (thermal, hydro) electricity unit [p.u.] («``eMaxRampUpEleOutput``, ``eMaxRampDwEleOutput``»)

* P. Damcı-Kurt, S. Küçükyavuz, D. Rajan, and A. Atamtürk, “A polyhedral study of production ramping,” Math. Program., vol. 158, no. 1–2, pp. 175–205, Jul. 2016. `10.1007/s10107-015-0919-9 <https://doi.org/10.1007/s10107-015-0919-9>`_

:math:`\frac{- ep2b_{n-\nu,g} - dp^{SR}_{n-\nu,g} - dp^{TR}_{n-\nu,g} + ep2b_{neg} + up^{SR}_{neg} + up^{TR}_{neg}}{DUR_n RU_g} \leq   euc_{neg}      - esu_{neg} \quad \forall neg`

:math:`\frac{- ep2b_{n-\nu,g} + up^{SR}_{n-\nu,g} + up^{TR}_{n-\nu,g} + ep2b_{neg} - dp^{SR}_{neg} - dp^{TR}_{neg}}{DUR_n RD_g} \geq - euc_{n-\nu,g} + esd_{neg} \quad \forall neg`

Maximum ramp down and ramp up for the charge of an electricity ESS [p.u.] («``eMaxRampUpEleCharge``, ``eMaxRampDwEleCharge``»)

:math:`\frac{- ec2b_{n-\nu,es} + dc^{SR}_{n-\nu,es} + dc^{TR}_{n-\nu,es} + ec2b_{nes} - uc^{SR}_{nes} - uc^{TR}_{nes}}{DUR_n RU_es} \geq - 1 \quad \forall nes`

:math:`\frac{- ec2b_{n-\nu,es} - uc^{SR}_{n-\nu,es} - uc^{TR}_{n-\nu,es} + ec2b_{nes} + dc^{SR}_{nes} + dc^{TR}_{nes}}{DUR_n RD_es} \leq   1 \quad \forall nes`

Maximum ramp up and ramp down for the  second block of a hydrogen unit [p.u.] («``eMaxRampUpHydOutput``, ``eMaxRampDwHydOutput``»)

:math:`\frac{- hp2b_{n-\nu,hg} + hp2b_{nhg}}{DUR_n RU_hg} \leq   huc_{nhg}      - hsu_{nhg} \quad \forall nhg`

:math:`\frac{- hp2b_{n-\nu,hg} + hp2b_{nhg}}{DUR_n RD_hg} \geq - huc_{n-\nu,hg} + hsd_{nhg} \quad \forall nhg`

Maximum ramp down and ramp up for the charge of a hydrogen ESS [p.u.] («``eMaxRampUpHydCharge``, ``eMaxRampDwHydCharge``»)

:math:`\frac{- hc2b_{n-\nu,hs} + hc2b_{nhs}}{DUR_n RU_hs} \geq - 1 \quad \forall nhs`

:math:`\frac{- hc2b_{n-\nu,hs} + hc2b_{nhs}}{DUR_n RD_hs} \leq   1 \quad \forall nhs`

Maximum ramp up and ramp down for the outflows of a hydrogen ESS [p.u.] («``eMaxRampUpHydOutflows``, ``eMaxRampDwHydOutflows``»)

:math:`\frac{- heo_{n-\nu,hs} + heo_{nhs}}{DUR_n RU_hs} \leq   1 \quad \forall nhs`

:math:`\frac{- heo_{n-\nu,hs} + heo_{nhs}}{DUR_n RD_hs} \geq - 1 \quad \forall nhs`

Ramp up and ramp down for the provision of demand to the hydrogen customers [p.u.] («``eMaxRampUpHydDemand``, ``eMaxRampDwHydDemand``»)

:math:`\frac{- hd_{n-\nu,nd} + hd_{nnd}}{DUR_n RU_nd} \leq   1 \quad \forall nnd`

:math:`\frac{- hd_{n-\nu,nd} + hd_{nnd}}{DUR_n RD_nd} \geq - 1 \quad \forall nnd`

Differences between electricity consumption of two consecutive hours [GW] («``eEleConsumptionDiff``»)

:math:`-ec_{n-\nu,es} + ec_{nes} = RC^{+}_{hz} - RC^{-}_{hz}`

Minimum up time and down time of thermal unit [h] («``eMinUpTimeEle``, ``eMinDownTimeEle``»)

- D. Rajan and S. Takriti, “Minimum up/down polytopes of the unit commitment problem with start-up costs,” IBM, New York, Technical Report RC23628, 2005. https://pdfs.semanticscholar.org/b886/42e36b414d5929fed48593d0ac46ae3e2070.pdf

:math:`\sum_{n'=n+\nu-TU_t}^n esu_{n't} \leq     euc_{net} \quad \forall net`

:math:`\sum_{n'=n+\nu-TD_t}^n esd_{n't} \leq 1 - euc_{net} \quad \forall net`

Minimum up time and down time of hydrogen unit [h] («``eMinUpTimeHyd``, ``eMinDownTimeHyd``»)

:math:`\sum_{n'=n+\nu-TU_h}^n hsu_{n'hg} \leq     huc_{nhg} \quad \forall nhg`

:math:`\sum_{n'=n+\nu-TD_h}^n hsd_{n'hg} \leq 1 - huc_{nhg} \quad \forall nhg`

Decision variable of the operation of the compressor conditioned by the on/off status variable of itself [GWh] («``eCompressorOperStatus``»)

:math:`ec^{Comp}_{nhs} \geq hp_{nhz}/\overline{HP}_{nhz} \overline{EC}^{comp}_{nhs} - 1e-3 (1 - hcf_{nhs}) \quad \forall nhs`

Decision variable of the operation of the compressor conditioned by the status of energy of the hydrogen tank [kgH2] («``eCompressorOperInventory``»)

:math:`hsi_{nhs} \leq \underline{HI}_{nhs} + (\overline{HI}_{nhs} - \underline{HI}_{nhs}) hcf_{nhs} \quad \forall nhs`

StandBy status of the electrolyzer conditioning its electricity consumption [GWh] («``eEleStandBy_consumption_UpperBound``, ``eEleStandBy_consumption_LowerBound``»)

:math:`ec^{StandBy}_{nhz} \geq \overline{EC}_{nhz} hsf_{nhz} \quad \forall nhz`

:math:`ec^{StandBy}_{nhz} \leq \overline{EC}_{nhz} hsf_{nhz} \quad \forall nhz`

StandBy status of the electrolyzer conditioning its hydrogen production [GWh] («``eHydStandBy_production_UpperBound``, ``eHydStandBy_production_LowerBound``»)

:math:`ec^{StandBy}_{nhz} \geq \overline{EC}_{nhz} (1 - hsf_{nhz}) \quad \forall nhz`

:math:`ec^{StandBy}_{nhz} \leq \underline{EC}_{nhz} (1 - hsf_{nhz}) \quad \forall nhz`

Avoid transition status from off to StandBy of the electrolyzer [p.u.] («``eHydAvoidTransitionOff2StandBy``»)

:math:`hsf_{nhz} \leq huc_{nhz} \quad \forall nhz`

Second Kirchhoff's law for the electricity network [kgH2] («``eKirchhoff2ndLaw``»)

:math:`\frac{ef_{nijc}}{\overline{ENF}_{nijc}} - \frac{\theta_{ni} - \theta_{nj}}{\overline{X}_{nijc}\overline{ENF}_{nijc}} == 0 \quad \forall nijc`

Bounds on variables [GW, kgH2]

:math:`0 \leq ep_{neg}                               \leq \overline{EP}_{neg}                              \quad \forall neg`

:math:`-\widehat{EP}_{neg} \leq ep^{\Delta}_{neg}   \leq \overline{EP}_{neg} - \widehat{EP}_{neg}         \quad \forall neg`

:math:`0 \leq hp_{nhg}   \leq \overline{HP}_{nhg}                                                          \quad \forall nhg`

:math:`-\widehat{HP}_{nhg} \leq hp^{\Delta}_{nhg}   \leq \overline{HP}_{nhg} - \widehat{HP}_{nhg}          \quad \forall nhg`

:math:`0 \leq ec_{nes}  \leq \overline{EC}_{nes}                                                           \quad \forall nes`

:math:`-\widehat{EC}_{nes} \leq ec^{\Delta}_{nes}  \leq \overline{EC}_{nes} - \widehat{EC}_{nes}           \quad \forall nes`

:math:`0 \leq ec_{nhz}  \leq \overline{EC}_{nhz}                                                           \quad \forall nhz`

:math:`-\widehat{EC}_{nhz} \leq ec^{\Delta}_{nhz}  \leq \overline{EC}_{nhz} - \widehat{EC}_{nhz}           \quad \forall nhz`

:math:`0 \leq hc_{nhs}   \leq \overline{HC}_{nhs}                                                          \quad \forall nhs`

:math:`-\widehat{HC}_{nhs} \leq hc^{\Delta}_{nhs}  \leq \overline{HC}_{nhs} - \widehat{HC}_{nhs}           \quad \forall nhs`

:math:`0 \leq hc_{net}   \leq \overline{HC}_{net}                                                          \quad \forall net`

:math:`-\widehat{HC}_{net}\leq hc^{\Delta}_{net}  \leq \overline{HC}_{net} -\widehat{HC}_{net}             \quad \forall net`

:math:`0 \leq ep2b_{neg} \leq \overline{EP}_{neg} - \underline{EP}_{neg}                                   \quad \forall neg`

:math:`0 \leq hp2b_{nhg} \leq \overline{HP}_{nhg} - \underline{HP}_{nhg}                                   \quad \forall nh`

:math:`0 \leq eeo_{nes} \leq \max(\overline{EP}_{nes},\overline{EC}_{nes})                                 \quad \forall nes`

:math:`0 \leq heo_{nhs} \leq \max(\overline{HP}_{nhs},\overline{HC}_{nhs})                                 \quad \forall nhs`

:math:`0 \leq up^{SR}_{neg}, dp^{SR}_{neg}  \leq \overline{EP}_{neg} - \underline{EP}_{neg}                \quad \forall neg`

:math:`0 \leq up^{TR}_{neg}, dp^{TR}_{neg}  \leq \overline{EP}_{neg} - \underline{EP}_{neg}                \quad \forall neg`

:math:`0 \leq uc^{SR}_{nes}, dc^{SR}_{nes} \leq \overline{EC}_{nes} - \underline{EC}_{nes}                 \quad \forall nes`

:math:`0 \leq uc^{TR}_{nes}, dc^{TR}_{nes} \leq \overline{EC}_{nes} - \underline{EC}_{nes}                 \quad \forall nes`

:math:`0 \leq ec2b_{nes}  \leq \overline{EC}_{nes}                                                         \quad \forall nes`

:math:`0 \leq hc2b_{nhs}  \leq \overline{HC}_{nhs}                                                         \quad \forall nhs`

:math:`\underline{EI}_{nes} \leq  esi_{nes}  \leq \overline{EI}_{nes}                                      \quad \forall nes`

:math:`\underline{HI}_{nhs} \leq  hsi_{nhs}  \leq \overline{HI}_{nhs}                                      \quad \forall nhs`

:math:`0 \leq  ess_{nes}                                                                                   \quad \forall nes`

:math:`0 \leq  hss_{nhs}                                                                                   \quad \forall nhs`

:math:`0 \leq ec^{R+}_{nes}, ec^{R-}_{nes} \leq \overline{EC}_{nes}                                        \quad \forall nes`

:math:`0 \leq ec^{R+}_{nhz}, ec^{R-}_{nhz} \leq \overline{EC}_{nhz}                                        \quad \forall nhz`

:math:`0 \leq ec^{Comp}_{nhs} \leq \overline{EC}_{nhs}                                                     \quad \forall nhs`

:math:`0 \leq ec^{StandBy}_{nhz} \leq \overline{EC}_{nhz}                                                  \quad \forall nhz`

:math:`-\overline{ENF}_{nijc} \leq  ef_{nij}  \leq \overline{ENF}_{nijc}                                   \quad \forall nijc`

:math:`-\overline{HNF}_{nijc} \leq  hf_{nij}  \leq \overline{HNF}_{nijc}                                   \quad \forall nijc`
