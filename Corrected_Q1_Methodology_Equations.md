---
title: "Corrected Mathematical Formulation of the Current HVAC Framework"
subtitle: "Q1-journal-ready replacement methodology section"
author: ""
date: ""
geometry: margin=1in
fontsize: 11pt
---

# Editorial note

This section reports the equations that are actually implemented in the current `hvac_v3_engine.py` configuration. It intentionally describes Strategy S3 as **condition-based maintenance combined with continuous online control optimization**. It does not describe S3 as forecast-based predictive maintenance, because no future degradation horizon or remaining-useful-life model is currently used in the maintenance decision.

The present default configuration also activates a dynamic reduced-order thermal model, monthly component corrections, and a rule-based operational-state correction layer. These layers must be reported because they modify the final energy values used by the S3 objective function. Optional modules that are disabled by default are not presented as active parts of the reported formulation.

# 1. Design quantities

The nominal cooling capacity, heating capacity, airflow rate, maximum occupant count, and maximum internal electrical gain are calculated from the conditioned floor area, $A$.

**Equation (1): nominal cooling capacity**

$$
Q_{c,des}=\frac{A\,q_{c,A}}{1000}
$$

**Equation (2): nominal heating capacity**

$$
Q_{h,des}=\frac{A\,q_{h,A}}{1000}
$$

**Equation (3): nominal airflow rate**

$$
\dot V_{air,nom}=A\,\dot v_{air,A}
$$

**Equation (4): maximum occupant count**

$$
N_{max}=A\,\rho_{occ}
$$

Here, $q_{c,A}$ and $q_{h,A}$ are the area-normalized design cooling and heating intensities in W m$^{-2}$, $\dot v_{air,A}$ is the airflow rate in m$^3$ h$^{-1}$ m$^{-2}$, and $\rho_{occ}$ is the occupant density in person m$^{-2}$.

# 2. Occupancy and internal gains

At time step $t$, the effective occupant count is

**Equation (5): occupant count**

$$
N_t=N_{max}\,o_t
$$

where $o_t$ is the calendar- and hour-dependent occupancy fraction.

Lighting and equipment powers are

**Equation (6): installed lighting and equipment powers**

$$
P_L=\frac{A\,p_{L,A}}{1000}, \qquad
P_E=\frac{A\,p_{E,A}}{1000}
$$

The internal electrical gain used by the load model is

**Equation (7): internal electrical gain**

$$
Q_{int,t}=(P_L+P_E)\max\left[0.20,\;0.20+f_{use}o_t\right]
$$

The sensible occupant gain is

**Equation (8): sensible occupant gain**

$$
Q_{occ,t}=\frac{N_t\,q_{sens}}{1000}
$$

# 3. Static cooling and heating loads

The cooling and heating temperature differences are

**Equation (9): temperature differences**

$$
\Delta T_{c,t}=\max(T_{a,t}-T_{sp,t},0), \qquad
\Delta T_{h,t}=\max(T_{sp,t}-T_{a,t},0)
$$

The normalized solar term and humidity multiplier are

**Equation (10): solar and humidity modifiers**

$$
g_t=\operatorname{clip}\left(\frac{GHI_t}{700},0,1.5\right)
$$

$$
\mu_{RH,t}=1+k_{RH}\max(RH_t-60,0)
$$

For a daily simulation, the seasonal solar factor is

**Equation (11): daily solar-season factor**

$$
s_t=\max\left[\sin\left(\frac{\pi d_t}{365}\right),0\right]
$$

For a sub-daily simulation, the code uses $s_t=1$ because the uploaded or generated irradiance series already contains the diurnal variation.

The static cooling-load components are

**Equation (12): envelope cooling load**

$$
Q_{c,env,t}=\chi_{env}\,a_c\,Q_{c,des}\frac{\Delta T_{c,t}}{\Delta T_{c,ref}}
$$

**Equation (13): solar cooling load**

$$
Q_{c,sol,t}=\chi_{sol}\,f_{sol}\,Q_{c,des}\,g_t\,s_t
$$

**Equation (14): infiltration cooling load**

$$
Q_{c,inf,t}=\chi_{inf}\,f_{inf,c}\,Q_{c,des}\frac{\Delta T_{c,t}}{\Delta T_{c,ref}}
$$

The resulting static cooling load is

**Equation (15): total static cooling load**

$$
Q_{c,stat,t}=\left(Q_{c,env,t}+Q_{c,sol,t}+Q_{int,t}+Q_{occ,t}+Q_{c,inf,t}\right)\mu_{RH,t}+Q_{lat,t}
$$

where $Q_{lat,t}=0$ in the present default configuration because latent-load coupling is disabled by default.

The static heating-load components are

**Equation (16): envelope and infiltration heating loads**

$$
Q_{h,env,t}=\chi_{env}\,a_h\,Q_{h,des}\frac{\Delta T_{h,t}}{\Delta T_{h,ref}}
$$

$$
Q_{h,inf,t}=\chi_{inf}\,f_{inf,h}\,Q_{h,des}\frac{\Delta T_{h,t}}{\Delta T_{h,ref}}
$$

The internal-gain credit is

**Equation (17): internal heating credit**

$$
Q_{credit,t}=f_{credit}\left(Q_{int,t}+Q_{occ,t}\right)
$$

and the static heating demand is

**Equation (18): total static heating load**

$$
Q_{h,stat,t}=Q_{h,env,t}+Q_{h,inf,t}-Q_{credit,t}
$$

# 4. Dynamic reduced-order thermal layer

The current default configuration activates a two-state reduced-order dynamic layer. The equivalent zone-air and thermal-mass capacitances are

**Equation (19): thermal capacitances**

$$
C_z=A\,c_z, \qquad C_m=A\,c_m
$$

The effective envelope heat-transfer coefficient is

**Equation (20): effective envelope coefficient**

$$
H_{env}=\frac{1}{2}\left(
\frac{a_cQ_{c,des}}{\Delta T_{c,ref}}+
\frac{a_hQ_{h,des}}{\Delta T_{h,ref}}
\right)f_{UA}
$$

The ventilation/infiltration coefficient and mass-zone coupling coefficient are

**Equation (21): ventilation and mass-coupling coefficients**

$$
H_{vent}=\frac{ACH\,V\,\rho_{air}\,c_{p,air}}{3600}f_{vent}
$$

$$
H_{mz}=\frac{A\,h_{mz}}{1000}
$$

where $V=A h_f$ is the building air volume.

The free-floating zone temperature is calculated as

**Equation (22): free-floating zone temperature**

$$
T_{z,t}^{free}=T_{z,t}+\frac{\Delta t}{C_z}
\left[
(H_{env}+H_{vent})(T_{a,t}-T_{z,t})
+H_{mz}(T_{m,t}-T_{z,t})
+Q_{sol,a,t}+Q_{int,a,t}
\right]
$$

The dynamic cooling and heating demands are

**Equation (23): dynamic thermostat demands**

$$
Q_{c,dyn,t}=\max\left[
\frac{(T_{z,t}^{free}-T_{c,sp})C_z}{\Delta t},0
\right]
$$

$$
Q_{h,dyn,t}=\max\left[
\frac{(T_{h,sp}-T_{z,t}^{free})C_z}{\Delta t},0
\right]
$$

The accepted zone temperature and next thermal-mass temperature are

**Equation (24): state update**

$$
T_{z,t+1}=\operatorname{clip}\left[
T_{z,t}^{free}-\varepsilon\frac{Q_{c,dyn,t}\Delta t}{C_z}
+\varepsilon\frac{Q_{h,dyn,t}\Delta t}{C_z},
T_{min},T_{max}
\right]
$$

$$
T_{m,t+1}=\operatorname{clip}\left[
T_{m,t}+\frac{\Delta t}{C_m}
\left[
H_{mz}(T_{z,t+1}-T_{m,t})
+Q_{sol,m,t}+Q_{int,m,t}
+0.15H_{env}(T_{a,t}-T_{m,t})
\right],
T_{min},T_{max}
\right]
$$

**Correction for Word insertion:** in the second expression above, the term must read

$$
H_{mz}(T_{z,t+1}-T_{m,t})
$$

without any additional symbol before $H_{mz}$.

The static and dynamic loads are blended using the replacement fraction $\beta_{RC}$:

**Equation (25): blended cooling and heating loads**

$$
Q_{c,RC,t}=(1-\beta_{RC})\max(Q_{c,stat,t},0)+\beta_{RC}Q_{c,dyn,t}
$$

$$
Q_{h,RC,t}=(1-\beta_{RC})\max(Q_{h,stat,t},0)+\beta_{RC}Q_{h,dyn,t}
$$

The current default value is $\beta_{RC}=0.75$.

# 5. Monthly availability and minimum operational loads

The present default configuration applies month-dependent availability factors:

**Equation (26): monthly availability correction**

$$
Q_{c,av,t}=a_{c,m}Q_{c,RC,t}, \qquad
Q_{h,av,t}=a_{h,m}Q_{h,RC,t}
$$

The occupancy factor used by the minimum-load calculation is

**Equation (27): minimum-load occupancy factor**

$$
f_{occ,t}=\operatorname{clip}\left[(1-w_o)+w_oo_t,0.25,1.20\right]
$$

The month-specific minimum operational loads are

**Equation (28): minimum operational loads**

$$
Q_{c,min,t}=r_{c,m}Q_{c,des}f_{occ,t}a_{c,m}
$$

$$
Q_{h,min,t}=r_{h,m}Q_{h,des}f_{occ,t}a_{h,m}
$$

The accepted pre-capacity loads are

**Equation (29): accepted operational loads**

$$
Q_{c,op,t}=\max(Q_{c,av,t},Q_{c,min,t})
$$

$$
Q_{h,op,t}=\max(Q_{h,av,t},Q_{h,min,t})
$$

These empirical monthly terms are calibration terms and must be identified as such in the manuscript. They are not universal physical constants.

# 6. Physical degradation model

Let $\tau=\Delta t/24$ be the time-step duration in days. Heat-exchanger fouling resistance is updated as

**Equation (30): fouling-resistance update**

$$
R_{f,t+1}=R_f^{*}-\left(R_f^{*}-R_{f,t}\right)\exp(-B_f\tau)
$$

Filter dust accumulation is

**Equation (31): filter-dust update**

$$
m_{d,t+1}=m_{d,t}+\dot m_d\,\alpha_t\tau
$$

The resulting pressure drop is

**Equation (32): filter pressure drop**

$$
\Delta P_{t+1}=\min\left(\Delta P_{clean}+k_{clog}m_{d,t+1},\Delta P_{max}\right)
$$

The composite degradation indicator currently implemented in the code is

**Equation (33): implemented composite degradation indicator**

$$
\delta_{t+1}=\frac{1}{2}\frac{R_{f,t+1}}{R_f^{*}}+
\frac{1}{2}\frac{\Delta P_{t+1}}{\Delta P_{max}}
$$

This is the exact implemented equation. It does not equal zero at a clean filter. With the current defaults, $\Delta P_{clean}=150$ Pa and $\Delta P_{max}=450$ Pa, giving $\delta_{clean}=0.1667$. The manuscript must not claim that the current $\delta$ is a zero-to-one percentage of deterioration.

# 7. Degradation-dependent coefficient of performance

The implemented cooling coefficient of performance is

**Equation (34): cooling COP**

$$
COP_{c,t}=\min\left\{
COP_{c,nom},
\max\left[
0.8,
\frac{COP_{c,nom}-k_{age}y_t}
{1+0.45R_{f,t}/R_f^{*}}
\left(1-0.018\max(T_{a,t}-25,0)\right)
\right]
\right\}
$$

The implemented heating coefficient of performance is

**Equation (35): heating COP**

$$
COP_{h,t}=\min\left\{
COP_{h,nom},
\max\left[
0.8,
\frac{COP_{h,nom}-0.6k_{age}y_t}
{1+0.30R_{f,t}/R_f^{*}}
\left(1-0.010\max(18-T_{a,t},0)\right)
\right]
\right\}
$$

# 8. HVAC, fan, pump, and auxiliary powers

Under the current default dominant-mode setting, the active thermal load is the larger branch that exceeds its minimum activation threshold. The corresponding HVAC electrical power is

**Equation (36): thermal HVAC electrical power**

$$
P_{HVAC,t}=\frac{Q_{HVAC,t}}{COP_t}
$$

where $COP_t$ is selected from Equation (34) or Equation (35) according to the dominant operating mode.

The raw fan power is

**Equation (37): raw fan power**

$$
P_{fan,raw,t}=\frac{
(\dot V_{air,nom}\alpha_t/3600)\Delta P_t
}{1000\eta_{fan}}
$$

The default model also applies a schedule-based fan floor. Let

**Equation (38): fan runtime and airflow floors**

$$
r_{fan,t}=\operatorname{clip}\left[
\max(r_{min},w_{occ}o_t+w_{HVAC}I_{HVAC,t})a_{fan,m},0,1.25
\right]
$$

$$
\alpha_{floor,t}=\max(\alpha_t,\alpha_{min,fan})
$$

Then

**Equation (39): schedule-based fan power**

$$
P_{fan,sch,t}=P_{fan,des,t}\max(r_{fan,t},\alpha_{floor,t})
$$

$$
P_{fan,t}=\max(P_{fan,raw,t},P_{fan,sch,t})
$$

where

$$
P_{fan,des,t}=\frac{(\dot V_{air,nom}/3600)\Delta P_t}{1000\eta_{fan}}
$$

Because detailed water-side pressure coupling is disabled by default, pump and auxiliary powers are

**Equation (40): pump and auxiliary powers**

$$
f_{op,t}=\max(o_t,0.35)
$$

$$
P_{pump,t}=\frac{A\,p_{pump,A}}{1000}f_{op,t}(1+0.30\delta_t)
$$

$$
P_{aux,t}=\frac{A\,p_{aux,A}}{1000}f_{op,t}
$$

# 9. Seasonal and operational-state component corrections

The final reported powers are not the raw component powers. The default configuration applies a damped monthly factor to each component $j$:

**Equation (41): monthly component factor**

$$
F_{j,m}=\operatorname{clip}\left[1+\lambda_s(F_{j,m}^{raw}-1),F_{min},F_{max}\right]
$$

$$
P_{j,t}^{(s)}=F_{j,m}P_{j,t}^{raw}
$$

A rule-based operating regime $r_t$ is then assigned, and a second damped factor is applied:

**Equation (42): operational-state factor**

$$
G_{j,r_t}=\operatorname{clip}\left[1+\lambda_o(G_{j,r_t}^{raw}-1),G_{min},G_{max}\right]
$$

$$
P_{j,t}^{final}=G_{j,r_t}P_{j,t}^{(s)}
$$

These correction factors were introduced to reduce residual seasonal mismatch against the reference simulation. They must be reported as calibration layers, and their values and calibration dataset must be made available for reproducibility.

The final total power and period energy are

**Equation (43): final power and energy**

$$
P_{tot,t}=P_{HVAC,t}^{final}+P_{fan,t}^{final}+P_{pump,t}^{final}+P_{aux,t}^{final}
$$

$$
E_t=P_{tot,t}\Delta t
$$

Carbon emissions are

**Equation (44): operational carbon**

$$
M_{CO_2,t}=E_t\,EF_{grid}
$$

# 10. Comfort indicator

The current empirical zone-temperature indicator is

**Equation (45): calculated zone-temperature indicator**

$$
T_{z,ind,t}=T_{sp,t}+2.2(1-\alpha_t)o_t
+0.08\max(T_{a,t}-T_{sp,t},0)
-0.06\max(T_{sp,t}-T_{a,t},0)
+k_{RH,c}\max(RH_t-60,0)
+0.60\delta_to_t
+P_{cap,t}
$$

where the unmet-capacity penalty is

**Equation (46): capacity penalty**

$$
P_{cap,t}=0.015\left(\frac{Q_{unmet,t}}{Q_{c,des}}\right)100
$$

The comfort deviation used by the objective is

**Equation (47): comfort deviation**

$$
D_{T,t}=\left|T_{z,ind,t}-T_{set}\right|
$$

This variable is an empirical comfort-deviation indicator. It is not PMV, PPD, operative temperature, or an ASHRAE 55 compliance calculation and should not be described as such.

# 11. S3 objective function

The S3 control vector is

**Equation (48): decision vector and bounds**

$$
\mathbf{x}_t=\begin{bmatrix}T_{sp,t}\\ \alpha_t\end{bmatrix}
$$

$$
T_{sp,min}\leq T_{sp,t}\leq T_{sp,max}, \qquad
\alpha_{min}\leq\alpha_t\leq\alpha_{max}
$$

The normalized terms used by the current code are

**Equation (49): implemented normalized indicators**

$$
e_t=\frac{E_t}{1.5Q_{c,des}\Delta t}
$$

$$
d_t=\delta_t
$$

$$
c_t=\frac{D_{T,t}}{3}
$$

$$
g_t=\frac{M_{CO_2,t}}{1.5Q_{c,des}EF_{grid}\Delta t}
$$

The implemented objective is

**Equation (50): S3 objective**

$$
J_t=w_Ee_t+w_Dd_t+w_Cc_t+w_Gg_t
$$

The default weights are

$$
(w_E,w_D,w_C,w_G)=(0.35,0.25,0.25,0.15)
$$

Because $M_{CO_2,t}=E_tEF_{grid}$ and $EF_{grid}$ is constant, the code gives

**Equation (51): energy-carbon dependence**

$$
g_t=e_t
$$

Therefore, the current objective is algebraically equivalent to

$$
J_t=0.50e_t+0.25d_t+0.25c_t
$$

The manuscript should disclose this dependence rather than claim four independent optimization objectives.

# 12. S3 stochastic control search

The current search routine is an iterative elite Gaussian stochastic search. It should not be identified as a published APO algorithm unless the actual APO operators are implemented and verified.

The initial centre and standard-deviation vector are

**Equation (52): initial search distribution**

$$
\boldsymbol{\mu}_0=\begin{bmatrix}T_{sp,t-1}\\ \alpha_{t-1}\end{bmatrix}, \qquad
\boldsymbol{\sigma}_0=\begin{bmatrix}1.4\\0.18\end{bmatrix}
$$

A random candidate is generated as

**Equation (53): candidate generation**

$$
\mathbf{x}_{k,i}=\operatorname{clip}
\left(
\boldsymbol{\mu}_k+\boldsymbol{\sigma}_k\odot\boldsymbol{\varepsilon}_{k,i}
\right)
$$

where

$$
\boldsymbol{\varepsilon}_{k,i}\sim\mathcal{N}(\mathbf{0},\mathbf{I})
$$

The candidate set also includes the current best solution, the nominal control $(T_{set},1)$, and the previous accepted control.

After objective evaluation, the elite set contains

**Equation (54): elite-set size**

$$
N_e=\max\left(3,\left\lfloor\frac{N_p}{4}\right\rfloor\right)
$$

The search centre and spread are updated as

**Equation (55): elite update**

$$
\boldsymbol{\mu}_{k+1}=\frac{1}{N_e}
\sum_{i\in\mathcal{E}_k}\mathbf{x}_{k,i}
$$

$$
\boldsymbol{\sigma}_{k+1}=0.72\boldsymbol{\sigma}_k
$$

The current stopping rule is a fixed iteration count:

$$
k=N_{iter}
$$

with $N_p=18$ and $N_{iter}=10$ by default. No convergence tolerance or early-stopping rule is currently implemented.

# 13. S3 condition-based maintenance

S3 control optimization is executed at every simulation time step. Maintenance is subsequently initiated from the current condition indicators.

The heat-exchanger cleaning decision is

**Equation (56): heat-exchanger maintenance trigger**

$$
u_{HX,t}=
\begin{cases}
1, & R_{f,t}\geq R_{f,warn}\;\text{or}\;\delta_t\geq\delta_{trig}\\
0, & \text{otherwise}
\end{cases}
$$

The filter replacement decision is

**Equation (57): filter maintenance trigger**

$$
u_{F,t}=
\begin{cases}
1, & \Delta P_t\geq\Delta P_{warn}\;\text{or}\;\delta_t\geq\delta_{trig}\\
0, & \text{otherwise}
\end{cases}
$$

For the physics-based branch, the current maintenance model applies idealized complete restoration of the affected state:

**Equation (58): implemented maintenance restoration**

$$
R_{f,t}^{+}=0 \quad \text{when } u_{HX,t}=1
$$

$$
m_{d,t}^{+}=0 \quad \text{when } u_{F,t}=1
$$

The current code does not include maintenance downtime, minimum maintenance intervals, action-specific recovery efficiency, crew availability, or a forecasted failure horizon. These elements belong in future work unless they are first implemented and the scenario matrix is rerun.

# 14. Cost accounting

Period energy cost is

**Equation (59): energy cost**

$$
C_{E,t}=p_EE_t
$$

Maintenance cost is

**Equation (60): direct maintenance cost**

$$
C_{M,t}=u_{F,t}C_F+u_{HX,t}C_{HX}
$$

The reported total cost is

**Equation (61): total period cost**

$$
C_{tot,t}=C_{E,t}+C_{M,t}
$$

The current maintenance cost is included in the reported total cost but is not included in the S3 objective function. Therefore, S3 does not currently perform joint economic optimization of control and maintenance timing.

# 15. Honest scope statement for the manuscript

The current contribution should be described as follows:

> Strategy S3 combines continuous time-step-level optimization of the zone temperature setpoint and airflow fraction with threshold-based condition monitoring of heat-exchanger fouling and filter pressure drop. The strategy is condition-based rather than forecast-based: maintenance actions are initiated from current simulated condition indicators, and no remaining-useful-life or future degradation horizon is used. The control search is implemented as an iterative elite Gaussian stochastic search with a fixed population and iteration count.

The following developments must be presented as future research, not as capabilities of the current study:

- forecast-horizon predictive maintenance;
- CatBoost prediction inside the S3 control or maintenance loop;
- remaining-useful-life estimation;
- maintenance downtime and capacity unavailability;
- incomplete and action-specific maintenance recovery;
- minimum service intervals and maintenance-resource constraints;
- independent carbon optimization using time-varying grid intensity;
- fixed reference bounds for all objective terms;
- formal implementation and benchmarking of a published APO algorithm.

# 16. Pre-submission implementation warning

The current physics-based simulation evaluates degradation before the maintenance decision and then re-evaluates the same period after the maintenance reset. This can advance the degradation equations twice for the reported period while the propagated state follows a different update path. The final numerical results, tables, and claimed savings should not be submitted until the state update is corrected to occur exactly once per accepted time step and the complete scenario matrix is regenerated.
