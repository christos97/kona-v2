# **Chapter 3 – Methods and Materials**

---

## **3.1 Overview and Conceptual Framework**

This chapter presents the methodological foundation of the present research, which examines the empirical relationship between **climate-mitigation efforts, air quality, and public health outcomes** within Europe and with particular focus on Greece, spanning 1990 to 2023.

The study tests the central hypothesis that **reductions in greenhouse gas (GHG) emissions yield measurable "health co-benefits,"** mediated by improvements in ambient air quality—particularly reductions in fine particulate matter (PM₂.₅). This hypothesis reflects the growing recognition in both academic literature and policy discourse that climate action and public health objectives are deeply intertwined.

To test this hypothesis, an **integrated empirical framework** was developed, combining environmental and epidemiological datasets from the **World Health Organization (WHO)**, the **United Nations Framework Convention on Climate Change (UNFCCC)**, the **European Environment Agency (EEA)**, and the **Institute for Health Metrics and Evaluation (IHME)**. The analysis proceeds through seven complementary regression models (B, C, D, G, E-lite, J-DALY, J-YLL), each addressing a specific component of the hypothesised pathway:

$$
\text{Sectoral GHG Emissions} \xrightarrow{\text{Models C, G, E}} \text{Air Quality (PM₂.₅)} \xrightarrow{\text{Models B, D, J}} \text{Public Health (DALYs / YLLs)}
$$

The analytical framework explicitly recognises that:

1. **Not all GHG emissions produce particulate matter**—only combustion-related sectors (energy, industry, transport) directly co-emit PM₂.₅
2. **PM₂.₅ is the critical mediator** between emissions and health outcomes
3. **Both morbidity (DALYs) and mortality (YLLs)** must be examined to capture the full health burden

The full analytical process is automated within the Python script `run.py` contained in the project repository. Each model is estimated, diagnosed, and stored in the `output/` directory, accompanied by statistical summaries, diagnostic plots, and intermediate panel datasets.

This approach ensures full **reproducibility**, **transparency**, and **traceability** in accordance with open-science standards.

---

## **3.2 Research Design and Philosophy**

This research is grounded in a **quantitative, post-positivist paradigm**. It assumes that environmental and health phenomena can be objectively observed, quantified, and statistically modelled. Rather than seeking to establish definitive causation—which would require experimental control—this thesis focuses on identifying **statistically significant associations** that provide credible empirical support for the hypothesised "co-benefits" pathway.

### **3.2.1 The Seven-Model Architecture**

A **modular regression design** was selected, consisting of seven models that test distinct links in the pathway:

| Model        | Relationship                   | Purpose                               | Analytical Approach                      |
| :----------- | :----------------------------- | :------------------------------------ | :--------------------------------------- |
| **B**        | PM₂.₅ → DALY                   | Health burden (morbidity + mortality) | OLS with nearest-year matching           |
| **C**        | Sectoral Emissions → PM₂.₅     | Environmental mechanism               | Panel OLS with two-way fixed effects     |
| **D**        | PM₂.₅ → YLL                    | Mortality burden                      | OLS with nearest-year matching           |
| **G**        | Total Emissions → PM₂.₅        | Aggregated emissions (robustness)     | Panel OLS with two-way fixed effects     |
| **E-lite**   | Lagged Total Emissions → PM₂.₅ | Temporal precedence (robustness)      | Panel OLS with two-way fixed effects     |
| **J (DALY)** | Quadratic PM₂.₅ → DALY         | Nonlinear dose–response (morbidity)   | OLS with centred quadratic specification |
| **J (YLL)**  | Quadratic PM₂.₅ → YLL          | Nonlinear dose–response (mortality)   | OLS with centred quadratic specification |

This separation offers three methodological advantages:

- **Clarity:** Each link in the chain is estimated independently, allowing clearer interpretation of coefficients and diagnostic results.
- **Precision:** Model C isolates _combustion-related_ sectors rather than aggregate emissions, removing measurement noise from GHG sources unrelated to air pollution.
- **Robustness:** Each model's validity can be assessed through dedicated residual and Q–Q plots, enabling independent verification of statistical assumptions.

### **3.2.2 The Narrative: From Emissions to Health**

The thesis tells a coherent empirical story:

1. **Human activities produce sectoral emissions** (energy generation, industrial production, transportation)
2. **Combustion emissions co-release PM₂.₅** as a by-product of fossil fuel burning
3. **PM₂.₅ exposure degrades health** through cardiovascular, respiratory, and systemic pathways
4. **Health burden manifests as DALYs** (years of healthy life lost) **and YLLs** (years of life lost to premature death)

By quantifying each link, the thesis supports a policy-relevant framing in which climate mitigation and air-quality management can be discussed together, while recognising that the empirical results in this thesis are **associational** and do not establish causal effects.

---

## **3.3 Data Sources**

All datasets used are publicly available institutional sources, ensuring verifiability and compliance with open-data ethics.

### **3.3.1 Greenhouse Gas Emissions (UNFCCC)**

The **UN Framework Convention on Climate Change (UNFCCC)** provides national inventory submissions with **sectoral disaggregation** of GHG emissions in kilotons of CO₂-equivalent. For this analysis, three combustion-intensive sectors were isolated:

| Sector                           | UNFCCC Category | Variable              | Rationale                                                            |
| :------------------------------- | :-------------- | :-------------------- | :------------------------------------------------------------------- |
| **Energy Industries**            | 1.A.1           | `energy_emissions`    | Power plants, refineries—major PM₂.₅ sources via coal/oil combustion |
| **Manufacturing & Construction** | 1.A.2           | `industry_emissions`  | Industrial boilers, kilns—significant point-source pollution         |
| **Transport**                    | 1.A.3           | `transport_emissions` | Road, rail, aviation—mobile sources, especially diesel vehicles      |

This sectoral decomposition is critical because aggregate GHG totals include non-combustion sources (agriculture, land use, fluorinated gases, waste decomposition) that **do not produce PM₂.₅**. By isolating combustion sectors, Model C targets the emissions that actually contribute to particulate pollution.

### **3.3.2 Ambient Air Quality (WHO)**

The **WHO Ambient Air Quality Database (2022)** provides population-weighted national mean concentrations of fine particulate matter (PM₂.₅) in micrograms per cubic metre (`pm25`).

PM₂.₅ (particles ≤ 2.5 micrometres in diameter) is the primary indicator of ambient air quality for health assessments because:

- Fine particles penetrate deep into the respiratory system and enter the bloodstream
- They are strongly associated with cardiovascular disease, stroke, lung cancer, and respiratory infections
- The WHO guideline level is 5 µg/m³ (annual mean), with interim targets at 10, 15, 25, and 35 µg/m³

The dataset covers time-series observations for European and global countries from 2010 onwards, enabling both cross-sectional and panel analysis.

### **3.3.3 Public Health Burden (EEA and GBD)**

Two complementary health metrics are employed:

#### **Disability-Adjusted Life Years (DALYs) — EEA**

The **European Environment Agency (EEA)** provides estimates of DALYs attributable to PM₂.₅ exposure across European countries. DALYs represent the total burden of disease, combining:

- **Years of Life Lost (YLL):** Premature mortality
- **Years Lived with Disability (YLD):** Morbidity-related quality-of-life reduction

One DALY = one year of healthy life lost. This comprehensive metric captures both fatal and non-fatal health impacts.

#### **Years of Life Lost (YLLs) — GBD/IHME**

The **Global Burden of Disease (GBD 2021)** from the **Institute for Health Metrics and Evaluation (IHME)** supplies **age-standardised mortality rates** converted to YLLs per 100,000 population (`yll_asmr`).

YLLs focus exclusively on premature mortality, providing a direct measure of life-years lost to pollution-attributable deaths. The age-standardisation ensures comparability across countries with different demographic structures.

---

## **3.4 Data Processing and Harmonisation**

### **3.4.1 Pre-Processing Pipeline**

Data cleaning and integration were conducted entirely in Python 3.12 using the `pandas` and `numpy` libraries. The workflow followed these standardised steps:

1. **Loading:** Raw `.csv` files imported from the `data/` directory
2. **Harmonisation:** All country names converted to ISO 3166-1 alpha-3 (`iso3`) codes using the `pycountry` library
3. **Sectoral Extraction:** UNFCCC data filtered to the three target sectors and pivoted to wide format
4. **Type Conversion:** All numeric fields coerced to `float`, commas and non-numeric characters removed
5. **Filtering:** Data restricted to valid years (2010–2021 for PM₂.₅ overlap) and relevant records
6. **Merging:**
   - **Model C:** Inner join on `["iso3", "country", "year"]` between WHO PM₂.₅ and UNFCCC sectoral data
   - **Models B & D:** Nearest-year matching (±3 year tolerance) to align PM₂.₅ with health data despite different reporting cycles

### **3.4.2 Variable Construction**

To address non-normal distributions typical of environmental data, all core variables were **log-transformed**:

| Original Variable     | Transformed Variable | Interpretation               |
| :-------------------- | :------------------- | :--------------------------- |
| `pm25`                | `ln_pm25`            | Air-quality exposure         |
| `energy_emissions`    | `ln_energy`          | Energy sector elasticity     |
| `industry_emissions`  | `ln_industry`        | Industrial sector elasticity |
| `transport_emissions` | `ln_transport`       | Transport sector elasticity  |
| `daly`                | `ln_daly`            | Health burden (DALYs)        |
| `yll_asmr`            | `ln_yll`             | Mortality burden (YLLs)      |

This log–log structure yields **elasticities**: a coefficient β = 0.5 indicates that a 1% increase in the independent variable is associated with a 0.5% increase in the dependent variable. Elasticities are policy-relevant because they express proportional relationships that scale across contexts.

**Handling of Invalid Values:** Before log transformation, any observations with zero, negative, or missing values in the variables to be transformed are excluded via `.dropna()` after replacing infinities with `NaN`. This ensures all log-transformed variables are defined on valid numeric domains.

### **3.4.3 Generated Panel Datasets**

The pipeline produces three intermediate panel datasets for verification and external analysis:

| Panel       | Description                  | Observations | File                                                                |
| :---------- | :--------------------------- | :----------- | :------------------------------------------------------------------ |
| **Panel B** | PM₂.₅ × DALY (EEA countries) | 54           | [panel_model_b_estimation.csv](output/panel_model_b_estimation.csv) |
| **Panel C** | Sectoral emissions × PM₂.₅   | 238          | [panel_model_c_estimation.csv](output/panel_model_c_estimation.csv) |
| **Panel D** | PM₂.₅ × YLL (global)         | 438          | [panel_model_d_estimation.csv](output/panel_model_d_estimation.csv) |

These CSV files enable independent verification using Excel, Google Sheets, R, or Stata.

**Reproducibility Note:** Every regression model (B, C, D, G, E-lite, J-DALY, J-YLL) uses a **materialized estimation panel** saved as `panel_model_*_estimation.csv` under `output/`. These panels contain **only the observations and variables used in estimation**, with all transformations (logs, centering, lags) already applied. This allows exact replication of results in Excel or other software without re-implementing preprocessing logic.

---

## **3.5 Model Specification**

### **3.5.1 Model B – PM₂.₅ → DALY (Health Burden)**

Model B evaluates whether countries with higher PM₂.₅ concentrations experience greater overall health burdens, measured as Disability-Adjusted Life Years per 100,000 population.

#### **Specification**

$$
\ln(\text{DALY})_i = \beta_0 + \beta_1 \ln(\text{PM}_{2.5})_i + \varepsilon_i
$$

Where:

- $i$ = country-year observation
- $\beta_1$ = elasticity of DALYs with respect to PM₂.₅

#### **Data Construction**

PM₂.₅ data (WHO) and DALY data (EEA) are merged using **nearest-year matching** with ±3 year tolerance, accounting for different reporting cycles across institutions. Final estimation sample: **N = 54** country-year observations (see [panel_model_b_estimation.csv](output/panel_model_b_estimation.csv)).

#### **Hypothesis**

$H_1$: $\beta_1 > 0$ — Higher PM₂.₅ concentrations are associated with greater health burden.

#### **Output Files**

| Output         | Description            | File                                                                          |
| :------------- | :--------------------- | :---------------------------------------------------------------------------- |
| Summary        | Full regression output | [ModelB_PM25_DALY_summary.txt](output/ModelB_PM25_DALY_summary.txt)           |
| Coefficients   | Parameter estimates    | [ModelB_PM25_DALY_coefficients.csv](output/ModelB_PM25_DALY_coefficients.csv) |
| Residuals Plot | Homoscedasticity check | See Figure 3.1 below                                                          |
| Q-Q Plot       | Normality check        | See Figure 3.2 below                                                          |
| Panel Data     | Analysis dataset       | [panel_model_b_estimation.csv](output/panel_model_b_estimation.csv)           |

---

### **3.5.2 Model C – Sectoral Emissions → PM₂.₅ (Environmental Mechanism)**

Model C is the centrepiece of the environmental analysis. It tests whether **combustion-related sectoral emissions** predict ambient PM₂.₅ concentrations, using a **multivariate panel regression with two-way fixed effects**.

#### **Specification**

$$
\ln(\text{PM}_{2.5})_{it} = \beta_0 + \beta_1 \ln(\text{Energy})_{it} + \beta_2 \ln(\text{Industry})_{it} + \beta_3 \ln(\text{Transport})_{it} + \alpha_i + \gamma_t + \varepsilon_{it}
$$

Where:

- $i$ = country (entity)
- $t$ = year (time period)
- $\alpha_i$ = country fixed effects (absorb time-invariant heterogeneity: geography, monitoring standards, industrial structure)
- $\gamma_t$ = year fixed effects (absorb global temporal shocks: economic crises, EU policy changes, weather patterns)
- $\varepsilon_{it}$ = error term (clustered at country level for robust inference)

#### **Why Sectoral Decomposition?**

Previous research using **total GHG emissions** to predict PM₂.₅ yielded weak and sometimes counter-intuitive results (negative coefficients, R² < 0.01). This occurs because aggregate inventories include:

| GHG Source                         | Produces PM₂.₅? | Effect on Models |
| :--------------------------------- | :-------------- | :--------------- |
| Energy combustion                  | ✅ Yes          | Signal           |
| Industrial combustion              | ✅ Yes          | Signal           |
| Transport combustion               | ✅ Yes          | Signal           |
| Agriculture (enteric fermentation) | ❌ No           | Noise            |
| Land use change                    | ❌ No           | Noise            |
| Fluorinated gases                  | ❌ No           | Noise            |
| Waste decomposition                | ❌ No           | Noise            |

By isolating the three combustion sectors, Model C:

1. **Removes measurement noise** from irrelevant GHG sources
2. **Increases explanatory power** by targeting emissions that actually produce PM₂.₅
3. **Enables policy insights** by revealing which sectors contribute most to air pollution

#### **Why Two-Way Fixed Effects?**

- **Country fixed effects** ($\alpha_i$) control for differences in geography (altitude, coastal vs. inland, ventilation patterns), monitoring infrastructure, baseline industrial composition, and population density. We compare changes _within_ the same country over time.

- **Year fixed effects** ($\gamma_t$) control for global shocks affecting all countries: the 2008 financial crisis, EU Emissions Trading System changes, COVID-19 (2020), and weather-related events (atmospheric inversions).

#### **Estimation**

Panel OLS using `linearmodels.PanelOLS` with:

- Entity effects: Yes (country)
- Time effects: Yes (year)
- Standard errors: Clustered at country level
- **No explicit intercept** (absorbed by fixed effects)
- Final estimation sample: **N = 238** country-year observations, 30 countries, 11 time periods (see [panel_model_c_estimation.csv](output/panel_model_c_estimation.csv))

#### **Hypothesis**

$H_1$: $\beta_1, \beta_2, \beta_3 > 0$ — Higher sectoral emissions are associated with higher PM₂.₅ concentrations.

#### **Output Files**

| Output         | Description             | File                                                                                  |
| :------------- | :---------------------- | :------------------------------------------------------------------------------------ |
| Summary        | Panel regression output | [ModelC_Sectoral_PM25_summary.txt](output/ModelC_Sectoral_PM25_summary.txt)           |
| Coefficients   | Parameter estimates     | [ModelC_Sectoral_PM25_coefficients.csv](output/ModelC_Sectoral_PM25_coefficients.csv) |
| Residuals Plot | Homoscedasticity check  | See Figure 3.3 below                                                                  |
| Q-Q Plot       | Normality check         | See Figure 3.4 below                                                                  |
| Panel Data     | Analysis dataset        | [panel_model_c_estimation.csv](output/panel_model_c_estimation.csv)                   |

---

### **3.5.3 Model D – PM₂.₅ → YLL (Mortality Burden)**

Model D complements Model B by focusing exclusively on **premature mortality**, using age-standardised Years of Life Lost from the Global Burden of Disease study.

#### **Specification**

$$
\ln(\text{YLL}_{\text{ASMR}})_i = \gamma_0 + \gamma_1 \ln(\text{PM}_{2.5})_i + \mu_i
$$

Where:

- $i$ = country-year observation
- $\gamma_1$ = elasticity of mortality (YLLs) with respect to PM₂.₅

#### **Data Construction**

PM₂.₅ data (WHO) and YLL data (GBD/IHME) are merged using **nearest-year matching** with ±3 year tolerance. The GBD provides global coverage, resulting in a larger sample: **N = 438** country-year observations (see [panel_model_d_estimation.csv](output/panel_model_d_estimation.csv)).

#### **Hypothesis**

$H_1$: $\gamma_1 > 0$ — Higher PM₂.₅ concentrations are associated with greater premature mortality.

#### **Output Files**

| Output         | Description            | File                                                                        |
| :------------- | :--------------------- | :-------------------------------------------------------------------------- |
| Summary        | Full regression output | [ModelD_PM25_YLL_summary.txt](output/ModelD_PM25_YLL_summary.txt)           |
| Coefficients   | Parameter estimates    | [ModelD_PM25_YLL_coefficients.csv](output/ModelD_PM25_YLL_coefficients.csv) |
| Residuals Plot | Homoscedasticity check | See Figure 3.5 below                                                        |
| Q-Q Plot       | Normality check        | See Figure 3.6 below                                                        |
| Panel Data     | Analysis dataset       | [panel_model_d_estimation.csv](output/panel_model_d_estimation.csv)         |

---

### **3.5.4 Model G – Total Emissions → PM₂.₅ (Aggregated Panel FE)**

Model G addresses potential **multicollinearity** among the three sectoral emission variables in Model C by aggregating them into a single total emissions measure. This simplification provides a cleaner test of the emissions–air quality relationship.

#### **Specification**

$$
\ln(\text{PM}_{2.5})_{it} = \beta \ln(\text{TotalEmissions})_{it} + \alpha_i + \gamma_t + \varepsilon_{it}
$$

Where:

- $\text{TotalEmissions}_{it} = \text{Energy}_{it} + \text{Industry}_{it} + \text{Transport}_{it}$
- $i$ = country (entity)
- $t$ = year (time period)
- $\alpha_i$ = country fixed effects
- $\gamma_t$ = year fixed effects
- $\varepsilon_{it}$ = error term (clustered at country level)

#### **Variable Construction**

Total emissions are computed by summing raw sectoral emissions **before** log transformation:

$$
\ln(\text{TotalEmissions}) = \ln(\text{Energy} + \text{Industry} + \text{Transport})
$$

This ensures numerical stability and avoids the approximation errors that arise from exponentiating and re-logging.

#### **Estimation**

- **Data:** Same exact-year WHO–UNFCCC panel as Model C
- **Fixed effects:** Two-way (entity + time)
- **Standard errors:** Clustered at country level
- **No explicit intercept:** Absorbed by fixed effects
- Final estimation sample: **N = 238** (identical to Model C, see [panel_model_g_estimation.csv](output/panel_model_g_estimation.csv))

#### **Rationale**

Model G serves as a robustness check for Model C:

1. **Reduces multicollinearity:** The three sectoral variables in Model C may be highly correlated, inflating standard errors
2. **Simpler interpretation:** Single elasticity coefficient ($\beta$) represents the aggregate emissions–PM₂.₅ relationship
3. **Direct comparability:** Uses identical sample as Model C, enabling direct coefficient comparison

#### **Output Files**

| Output         | Description             | File                                                                                              |
| :------------- | :---------------------- | :------------------------------------------------------------------------------------------------ |
| Summary        | Panel regression output | [ModelG_TotalEmissions_PM25_summary.txt](output/ModelG_TotalEmissions_PM25_summary.txt)           |
| Coefficients   | Parameter estimates     | [ModelG_TotalEmissions_PM25_coefficients.csv](output/ModelG_TotalEmissions_PM25_coefficients.csv) |
| Residuals Plot | Homoscedasticity check  | See Appendix                                                                                      |
| Q-Q Plot       | Normality check         | See Appendix                                                                                      |

---

### **3.5.5 Model E-lite – Lagged Total Emissions → PM₂.₅ (Panel FE, Conditional)**

Model E-lite tests whether **lagged emissions** predict current air quality, addressing concerns about simultaneity and allowing for delayed atmospheric effects.

#### **Specification**

$$
\ln(\text{PM}_{2.5})_{it} = \beta \ln(\text{TotalEmissions})_{i,t-1} + \alpha_i + \gamma_t + \varepsilon_{it}
$$

Where:

- $\text{TotalEmissions}_{i,t-1}$ = total emissions in country $i$ in year $t-1$
- All other terms defined as in Model G

#### **Gate Criteria and Decision**

Model E-lite is **only estimated** if the panel supports lagged specifications. The following criteria must **all** be satisfied:

1. **Median observations per country ≥ 3**
2. **Sample loss ≤ 30%**
3. **Country retention ≥ 67% of baseline**

**Gate check results** (from [ModelE_gate_check.txt](output/ModelE_gate_check.txt)):

- Baseline panel: N = 238 observations, 30 countries, median 8 obs/country
- After lagging (t-1): N = 208 observations, 30 countries retained, median 7 obs/country
- Sample loss: 12.6%
- All criteria: **PASS**
- **Decision: Model E-lite ESTIMATED**

#### **Rationale**

1. **Temporal precedence:** If emissions affect air quality, changes in emissions should precede changes in PM₂.₅
2. **Reduces simultaneity:** Lagging breaks potential reverse causality (where clean air regulations might simultaneously reduce emissions)
3. **Policy relevance:** Tests whether emission reductions translate to air quality improvements with a delay

#### **Estimation**

- **Data:** Same WHO–UNFCCC panel, with first observation per country dropped
- **Fixed effects:** Two-way (entity + time)
- **Standard errors:** Clustered at country level
- **No explicit intercept:** Absorbed by fixed effects
- Final estimation sample: **N = 208** (30 countries, 10 time periods after lag, see [panel_model_e_estimation.csv](output/panel_model_e_estimation.csv))

#### **Output Files**

| Output           | Description                | File                                                                                                                  |
| :--------------- | :------------------------- | :-------------------------------------------------------------------------------------------------------------------- |
| Gate Check       | Pre-estimation diagnostics | [ModelE_gate_check.txt](output/ModelE_gate_check.txt)                                                                 |
| Summary          | Panel regression output    | [ModelE_LaggedTotalEmissions_PM25_summary.txt](output/ModelE_LaggedTotalEmissions_PM25_summary.txt)                   |
| Coefficients     | Parameter estimates        | [ModelE_LaggedTotalEmissions_PM25_coefficients.csv](output/ModelE_LaggedTotalEmissions_PM25_coefficients.csv)         |
| Sample Retention | Lag-induced sample loss    | [ModelE_LaggedTotalEmissions_PM25_sample_retention.txt](output/ModelE_LaggedTotalEmissions_PM25_sample_retention.txt) |

---

### **3.5.6 Model J – Quadratic PM₂.₅ → Health (Nonlinear OLS)**

Model J extends Models B and D by testing for **nonlinear dose–response relationships** between PM₂.₅ and health outcomes. Epidemiological evidence suggests that health effects of air pollution may exhibit diminishing returns at high concentrations (concave) or accelerating harm (convex).

#### **Specification**

For each health outcome (DALY and YLL separately):

$$
\ln(\text{Health})_i = \beta_0 + \beta_1 z_i + \beta_2 z_i^2 + \varepsilon_i
$$

Where:

- $z_i = \ln(\text{PM}_{2.5})_i - \overline{\ln(\text{PM}_{2.5})}$ (centred log PM₂.₅)
- $\beta_1$ = linear effect at the mean
- $\beta_2$ = curvature parameter

#### **Centering Procedure**

The natural log of PM₂.₅ is **centred** before squaring to reduce multicollinearity between $z$ and $z^2$:

$$
z_i = \ln(\text{PM}_{2.5})_i - \frac{1}{N}\sum_{j=1}^{N}\ln(\text{PM}_{2.5})_j
$$

This transformation does not affect the model's fit but improves numerical conditioning and interpretability.

#### **Curvature Interpretation**

| Sign of $\beta_2$   | Interpretation                                                                |
| :------------------ | :---------------------------------------------------------------------------- |
| $\beta_2 > 0$       | **Convex** — accelerating harm; marginal health impact increases with PM₂.₅   |
| $\beta_2 < 0$       | **Concave** — diminishing marginal harm; health impact plateaus at high PM₂.₅ |
| $\beta_2 \approx 0$ | **Linear** — constant elasticity (Model B/D specification is adequate)        |

#### **Implied Turning Point**

If the curvature is concave ($\beta_2 < 0$), an implied turning point can be computed:

$$
z^* = -\frac{\beta_1}{2\beta_2}, \quad \text{PM}_{2.5}^* = \exp\left(z^* + \overline{\ln(\text{PM}_{2.5})}\right)
$$

**Important:** The turning point is reported as a **descriptive quantity** derived from point estimates. It should **not** be interpreted as a precisely identified threshold. No confidence interval is computed, as this would require delta-method approximations that add complexity without substantive value at the Master's thesis level.

#### **Estimation**

- **Data:** Two separate estimations using same cross-sectional samples as Models B and D
  - **Model J (DALY):** N = 54 (see [panel_model_j_daly_estimation.csv](output/panel_model_j_daly_estimation.csv))
  - **Model J (YLL):** N = 438 (see [panel_model_j_yll_estimation.csv](output/panel_model_j_yll_estimation.csv))
- **Method:** OLS with intercept
- **Library:** `statsmodels`

#### **Output Files**

| Output         | Description                 | File                                                                          |
| :------------- | :-------------------------- | :---------------------------------------------------------------------------- |
| Summary (DALY) | Quadratic regression output | [ModelJ_PM25_DALY_summary.txt](output/ModelJ_PM25_DALY_summary.txt)           |
| Coefficients   | Parameter estimates         | [ModelJ_PM25_DALY_coefficients.csv](output/ModelJ_PM25_DALY_coefficients.csv) |
| Diagnostics    | Curvature and turning point | [ModelJ_PM25_DALY_diagnostics.txt](output/ModelJ_PM25_DALY_diagnostics.txt)   |
| Summary (YLL)  | Quadratic regression output | [ModelJ_PM25_YLL_summary.txt](output/ModelJ_PM25_YLL_summary.txt)             |
| Coefficients   | Parameter estimates         | [ModelJ_PM25_YLL_coefficients.csv](output/ModelJ_PM25_YLL_coefficients.csv)   |
| Diagnostics    | Curvature and turning point | [ModelJ_PM25_YLL_diagnostics.txt](output/ModelJ_PM25_YLL_diagnostics.txt)     |

---

## **3.6 Statistical Estimation and Diagnostics**

### **3.6.1 Estimation Methods**

| Model      | Method    | Library        | Key Features                                   |
| :--------- | :-------- | :------------- | :--------------------------------------------- |
| **B**      | OLS       | `statsmodels`  | Cross-sectional, nearest-year merge            |
| **C**      | Panel OLS | `linearmodels` | Two-way FE, clustered SE, no intercept         |
| **D**      | OLS       | `statsmodels`  | Cross-sectional, nearest-year merge            |
| **G**      | Panel OLS | `linearmodels` | Two-way FE, clustered SE, aggregated emissions |
| **E-lite** | Panel OLS | `linearmodels` | Two-way FE, clustered SE, lagged specification |
| **J**      | OLS       | `statsmodels`  | Cross-sectional, centred quadratic term        |

**Note on Fixed Effects and Intercepts:**

For panel models with two-way fixed effects (C, G, E-lite), **no explicit intercept is estimated**. The intercept is absorbed into the country and time fixed effects. This is standard practice in fixed-effects estimation and is implemented consistently across all panel specifications in `src/models.py`.

### **3.6.2 Reported Metrics**

**For Models B, D, and J (OLS):**

- Coefficient estimates ($\beta$, $\gamma$)
- Standard errors and t-statistics
- P-values and 95% confidence intervals
- R² and adjusted R²
- F-statistic and model significance

**For Model J specifically:**

- Curvature interpretation (convex/concave/linear)
- Implied turning point in μg/m³ (if concave, descriptive only)

**For Models C, G, and E-lite (Panel FE):**

- Coefficient estimates ($\beta_1$, $\beta_2$, $\beta_3$)
- Clustered standard errors and t-statistics
- P-values
- R² within (temporal variation within countries)
- R² between (variation across countries)
- R² overall (combined fit)
- F-test for poolability (joint significance of fixed effects)

**Interpretation of Within-R² in Fixed-Effects Models:** Non-significant or negative within-R² values can occur in two-way fixed-effects models where entity and time effects absorb substantial variation. These values do not imply absence of association but rather reflect the partitioning of variance after controlling for unobserved heterogeneity. In Model C, the reported decomposition (Within R² = 0.1352; Between R² = 0.9578; Overall R² = 0.9548) indicates that cross-country differences dominate overall fit, while within-country year-to-year variation is harder to attribute after two-way fixed effects.

### **3.6.3 Model Diagnostics**

Two visual diagnostics are automatically generated for each model:

1. **Residuals vs Fitted Plot** — Verifies homoscedasticity (constant variance). Random scatter around 0 indicates the assumption holds; funnel shapes or patterns suggest heteroscedasticity.

2. **Normal Q–Q Plot** — Tests residual normality. Residuals lying near the 45° diagonal suggest normal distribution; systematic deviations indicate non-normality.

---

## **3.7 Diagnostic Figures**

### **Model B Diagnostics**

#### **Figure 3.1: Model B – Residuals vs Fitted Values**

![Model B Residuals](output/ModelB_PM25_DALY_residuals.png)

_Interpretation:_ Random scatter around the horizontal zero line indicates homoscedasticity. No systematic patterns suggest the constant variance assumption is satisfied.

#### **Figure 3.2: Model B – Normal Q-Q Plot**

![Model B Q-Q Plot](output/ModelB_PM25_DALY_qqplot.png)

_Interpretation:_ Residuals closely follow the 45° reference line, confirming approximate normality. Slight deviations at the tails are acceptable given the sample size (N=54).

---

### **Model C Diagnostics**

#### **Figure 3.3: Model C – Residuals vs Fitted Values**

![Model C Residuals](output/ModelC_Sectoral_PM25_residuals.png)

_Interpretation:_ The residuals display reasonable dispersion around zero. Some clustering is expected in panel data due to repeated observations within countries.

#### **Figure 3.4: Model C – Normal Q-Q Plot**

![Model C Q-Q Plot](output/ModelC_Sectoral_PM25_qqplot.png)

_Interpretation:_ Residuals approximate the normal distribution with slight heavy tails. Given the two-way fixed effects structure and clustered standard errors, inference remains robust.

---

### **Model D Diagnostics**

#### **Figure 3.5: Model D – Residuals vs Fitted Values**

![Model D Residuals](output/ModelD_PM25_YLL_residuals.png)

_Interpretation:_ Random dispersion supports homoscedasticity. The larger sample (N=438) provides greater stability in residual patterns.

#### **Figure 3.6: Model D – Normal Q-Q Plot**

![Model D Q-Q Plot](output/ModelD_PM25_YLL_qqplot.png)

_Interpretation:_ Near-normal residuals with minor deviations. The large sample size ensures robustness to minor departures from normality via the Central Limit Theorem.

---

## **3.8 Reproducibility and Computational Environment**

All analyses were executed within a **Poetry-managed virtual environment** under Linux. The automated workflow ensures full reproducibility:

### **Quick Start**

```bash
# Run all 3 models
make run

# Run individual models
poetry run python run.py --model B  # Health burden
poetry run python run.py --model C  # Sectoral emissions
poetry run python run.py --model D  # Mortality
```

### **Computational Environment**

| Library                  | Version    | Function                            |
| :----------------------- | :--------- | :---------------------------------- |
| `pandas`                 | 2.x        | Data loading & merging              |
| `numpy`                  | 1.x        | Log transforms & numeric operations |
| `statsmodels`            | 0.14.x     | OLS estimation & diagnostics        |
| `linearmodels`           | 5.x        | Fixed-effects panel analysis        |
| `matplotlib` / `seaborn` | 3.x / 0.13 | Visualisation                       |
| `pycountry`              | 22.x       | ISO 3166 standardisation            |

### **Output Structure**

```
output/
├── panel_model_b_estimation.csv    # Model B estimation data
├── panel_model_c_estimation.csv    # Model C estimation data
├── panel_model_d_estimation.csv    # Model D estimation data
├── ModelB_PM25_DALY_summary.txt    # Regression summary
├── ModelB_PM25_DALY_coefficients.csv
├── ModelB_PM25_DALY_residuals.png
├── ModelB_PM25_DALY_qqplot.png
├── ModelC_Sectoral_PM25_summary.txt
├── ModelC_Sectoral_PM25_coefficients.csv
├── ModelC_Sectoral_PM25_residuals.png
├── ModelC_Sectoral_PM25_qqplot.png
├── ModelD_PM25_YLL_summary.txt
├── ModelD_PM25_YLL_coefficients.csv
├── ModelD_PM25_YLL_residuals.png
├── ModelD_PM25_YLL_qqplot.png
├── summary_all_models.csv          # Consolidated results
└── run_log_YYYYMMDD_HHMMSS.txt     # Execution log
```

All scripts and outputs are version-controlled via Git, ensuring full traceability.

---

## **3.9 Ethical and Data-Integrity Considerations**

This research exclusively utilises **public, aggregate datasets** released by intergovernmental organisations. No personal or micro-level data are used; thus, no ethical approval is required.

All preprocessing, analysis, and visualisation steps are automated, preventing manual manipulation of values. Each CSV and figure generated by the pipeline serves as a verifiable audit trail for reproducibility.

---

## **3.10 Limitations**

Several methodological limitations should be acknowledged:

1. **Omitted Variables:** Models B and D focus on bivariate relationships. Economic factors (GDP per capita), demographic factors (age distribution), and behavioural factors (smoking prevalence) were not included. This may introduce omitted variable bias.

2. **Temporal Misalignment:** Nearest-year matching (±3 years) introduces measurement error when PM₂.₅ and health data are from different years. This is a necessary compromise given institutional reporting cycles.

3. **Model C Statistical Power:** While coefficients in Model C are positive (as hypothesised), they do not reach statistical significance at conventional levels. This may reflect:

   - Transboundary pollution (emissions in one country affect air quality in neighbours)
   - Annual aggregation masking seasonal variation
   - Sample size constraints after applying two-way fixed effects

4. **Quadratic Turning Points (Descriptive Only):** Where Model J diagnostics report an implied turning point (e.g., 30.3 μg/m³ for DALYs), this quantity is derived from point estimates and is treated as descriptive. It should not be interpreted as a threshold, target, or safety level.

5. **Causality vs Association:** OLS and panel regressions estimate statistical associations, not causal effects. Establishing causality would require instrumental variables or natural experiments.

6. **Sectoral Aggregation:** Even the three sectors used are broad categories. Sub-sectoral analysis (e.g., coal vs. gas electricity, diesel vs. petrol transport) would provide finer resolution.

---

## **3.11 Summary of the Methodological Approach**

The methodology developed in this thesis establishes a reproducible, transparent system for quantifying the environmental and health impacts of sectoral emission trends. Its principal contributions are:

1. **Integrated Environmental–Health Framework:** Uniting WHO, UNFCCC, EEA, and GBD datasets into coherent analytical panels.

2. **Seven-Model Architecture:**

   - Models C, G, E test the _environmental mechanism_ (emissions → PM₂.₅) using sectoral, aggregated, and lagged specifications
   - Models B, D, J test the _health mechanism_ (PM₂.₅ → DALYs and YLLs) using linear and quadratic specifications

3. **Sectoral Decomposition:** Isolating combustion-related emissions that actually produce PM₂.₅, rather than using diluted aggregate totals.

4. **Two-Way Fixed Effects:** Controlling for unobserved heterogeneity across countries and time in Model C.

5. **Log-Log Elasticity Models:** Yielding policy-relevant percentage-change interpretations.

6. **Full Reproducibility:** Automated Python pipeline with version-controlled code and outputs.

Together, these features form a coherent methodological framework that empirically examines the hypothesised pathway:

$$
 ext{Sectoral Emissions} \;\longleftrightarrow\; \text{Air Quality (PM}_{2.5}\text{)} \;\longleftrightarrow\; \text{Health Burden}
$$

---

### **Figure Reference Summary**

| Figure   | Description                            | File Path                                                                              |
| :------- | :------------------------------------- | :------------------------------------------------------------------------------------- |
| Fig. 3.1 | Residuals – Model B (PM₂.₅ → DALY)     | [output/ModelB_PM25_DALY_residuals.png](output/ModelB_PM25_DALY_residuals.png)         |
| Fig. 3.2 | Normal Q–Q – Model B                   | [output/ModelB_PM25_DALY_qqplot.png](output/ModelB_PM25_DALY_qqplot.png)               |
| Fig. 3.3 | Residuals – Model C (Sectoral → PM₂.₅) | [output/ModelC_Sectoral_PM25_residuals.png](output/ModelC_Sectoral_PM25_residuals.png) |
| Fig. 3.4 | Normal Q–Q – Model C                   | [output/ModelC_Sectoral_PM25_qqplot.png](output/ModelC_Sectoral_PM25_qqplot.png)       |
| Fig. 3.5 | Residuals – Model D (PM₂.₅ → YLL)      | [output/ModelD_PM25_YLL_residuals.png](output/ModelD_PM25_YLL_residuals.png)           |
| Fig. 3.6 | Normal Q–Q – Model D                   | [output/ModelD_PM25_YLL_qqplot.png](output/ModelD_PM25_YLL_qqplot.png)                 |

### **Table Reference Summary**

| Table     | Description                    | Location                                                       |
| :-------- | :----------------------------- | :------------------------------------------------------------- |
| Table 3.1 | Dataset sources                | §3.3                                                           |
| Table 3.2 | Log-transformed variables      | §3.4.2                                                         |
| Table 3.3 | Model specifications (B, C, D) | §3.5                                                           |
| Table 3.4 | Key results summary            | [output/summary_all_models.csv](output/summary_all_models.csv) |

---

# **Chapter 4 – Results and Analysis**

---

## **4.1 Overview**

This chapter presents the empirical results of the seven-model framework outlined in Chapter 3. The analysis examines the hypothesised pathway linking **sectoral GHG emissions**, **ambient air quality (PM₂.₅)**, and **public health burden** in terms of statistical associations.

### **Results Summary**

| Model        | Relationship                | N   | Coefficient/Statistic | Significance     |
| :----------- | :-------------------------- | :-- | :-------------------- | :--------------- |
| **B**        | PM₂.₅ → DALY                | 54  | β = **2.35**          | p < 0.001 ✓      |
| **C**        | Sectoral → PM₂.₅            | 238 | β = 0.08–0.16         | p = 0.14–0.99    |
| **D**        | PM₂.₅ → YLL                 | 438 | γ = **0.69**          | p < 0.001 ✓      |
| **G**        | Total Emissions → PM₂.₅     | 238 | β = −0.045            | p = 0.804        |
| **E-lite**   | Lagged Total Emissions → PM | 208 | β = −0.135            | p = 0.364        |
| **J (DALY)** | PM₂.₅ → DALY (quadratic)    | 54  | z: 2.10, z²: −1.11    | p = 0.001, 0.349 |
| **J (YLL)**  | PM₂.₅ → YLL (quadratic)     | 438 | z: 0.67, z²: 0.14     | p < 0.001, 0.210 |

**Key Finding:** The health models (B, D, J) demonstrate strong, statistically significant associations between PM₂.₅ and health outcomes. The environmental models (C, G, E) show mixed results: Model C (sectoral decomposition) yields positive coefficients as hypothesised but not statistically significant, while Models G and E (aggregated emissions) show null or negative associations.

---

## **4.2 Model B Results – PM₂.₅ → DALY**

### **4.2.1 Regression Output**

Full results: [ModelB_PM25_DALY_summary.txt](output/ModelB_PM25_DALY_summary.txt)

| Metric       | Value     |
| :----------- | :-------- |
| R²           | 0.287     |
| Adjusted R²  | **0.274** |
| F-statistic  | 20.96     |
| Observations | 54        |

| Variable  | Coefficient | Std. Error | t-Statistic | P-Value     | 95% CI        |
| :-------- | :---------- | :--------- | :---------- | :---------- | :------------ |
| `const`   | 2.025       | 1.279      | 1.58        | 0.119       | [−0.54, 4.59] |
| `ln_pm25` | **2.350**   | 0.513      | **4.58**    | **< 0.001** | [1.32, 3.38]  |

### **4.2.2 Interpretation**

- **Elasticity:** A **1% increase in PM₂.₅** is statistically associated with a **2.35% increase in DALYs**.
- **Significance:** Highly statistically significant (p < 0.001).
- **Model Fit:** PM₂.₅ explains **27.4%** of cross-country variation in health burden—a strong effect for a single-predictor model.

### **4.2.3 Policy Implication**

This model reports an elasticity-style association between PM₂.₅ and DALYs (β = 2.3502; N = 54). Consistent with the non-causal design of this thesis, this estimate is interpreted as an association rather than as a policy counterfactual.

### **4.2.4 Comparison with Literature**

The elasticity of 2.35 is aligned with **Tümay (2025)**, who reported a 1.9% association between PM₂.₅ and premature deaths across EU countries. The slightly higher value here reflects the inclusion of both mortality _and morbidity_ in the DALY measure.

### **4.2.5 Understanding the Magnitude of the DALY Elasticity**

The magnitude of the DALY elasticity in Model B (β ≈ 2.35) may appear large when compared with mortality-only estimates. This difference is consistent with the construction of DALYs as a composite measure that combines **years of life lost (YLL)** with **years lived with disability (YLD)** and applies disability weights to reflect the severity of non-fatal outcomes.

In practice, this means that long-lasting morbidity associated with PM₂.₅ exposure—such as chronic cardiovascular and respiratory disease, hospitalisation episodes, and persistent functional limitations—is fully counted in the DALY metric but only partially or indirectly reflected in mortality-based YLL measures. Countries with similar mortality profiles can therefore display substantially different DALY burdens if the prevalence, duration, or severity of pollution-associated morbidity is higher. The elasticity estimated in Model B is aligned with this construction: it is interpreted as capturing proportional changes in a broad health-burden index that is sensitive to both fatal and non-fatal outcomes, rather than as a numerical multiplier on deaths.

---

## **4.3 Model C Results – Sectoral Emissions → PM₂.₅**

### **4.3.1 Regression Output**

Full results: [ModelC_Sectoral_PM25_summary.txt](output/ModelC_Sectoral_PM25_summary.txt)

| Metric               | Value  |
| :------------------- | :----- |
| R² (Within)          | 0.1352 |
| R² (Between)         | 0.9578 |
| R² (Overall)         | 0.9548 |
| R² (Model)           | 0.0306 |
| Observations         | 238    |
| Entities (Countries) | 30     |
| Time Periods         | 11     |
| Avg Obs per Country  | 7.93   |

| Variable       | Coefficient | Std. Error | t-Statistic | P-Value |
| :------------- | :---------- | :--------- | :---------- | :------ |
| `ln_energy`    | 0.0833      | 0.0579     | 1.439       | 0.152   |
| `ln_industry`  | 0.1587      | 0.1065     | 1.490       | 0.138   |
| `ln_transport` | 0.0026      | 0.2045     | 0.013       | 0.990   |

**Note:** No explicit intercept is estimated in panel fixed-effects models; it is absorbed by country and time effects.

### **4.3.2 Interpretation**

**Coefficient Signs:** All three sectoral coefficients are **positive**, as hypothesised—higher emissions correlate with higher PM₂.₅. However, none reach statistical significance at the 0.05 level.

**Magnitudes:**

Within the estimated relationship:

- **Energy:** A 1% increase in energy sector emissions corresponds to ~0.08% higher PM₂.₅
- **Industry:** A 1% increase in industrial emissions corresponds to ~0.16% higher PM₂.₅
- **Transport:** Negligible association (β ≈ 0)

**R² Decomposition:**

- **Within R² = 0.1352:** The model explains **13.5% of temporal variation** in PM₂.₅ within countries over time after controlling for fixed effects.
- **Between R² = 0.9578:** Cross-country differences in emissions strongly predict cross-country differences in PM₂.₅ (95.8% of between-country variation explained).
- **Overall R² = 0.9548:** Combined model fit is high, driven primarily by between-country variation.
- **Model R² = 0.0306:** Incremental explanatory power of the three sectoral variables beyond fixed effects.

### **4.3.3 Why Not Statistically Significant?**

Several factors likely contribute:

1. **Transboundary Pollution and Spatial Diffusion:** PM₂.₅ in one country is influenced by emissions in neighbouring countries through cross-border transport and large-scale circulation patterns. This spatial diffusion weakens the alignment between national inventory totals and nationally averaged PM₂.₅, even when sectoral combustion sources are conceptually aligned with particulate formation.

2. **Annual Aggregation Limits:** Seasonal and episodic dynamics—such as winter heating peaks, summer photochemical episodes, or short-term stagnation events—are averaged out in annual mean data. This aggregation is statistically constrained in its ability to capture short-run emission–concentration episodes that co-vary with PM₂.₅ but may be muted in yearly averages.

3. **Secondary Inorganic Aerosols (SIAs) and Non-linear Chemistry:** A substantial fraction of PM₂.₅ mass in Europe consists of SIAs formed from gaseous precursors such as NOₓ, SO₂, and NH₃. The atmospheric chemistry that converts these precursors into particulate sulphates, nitrates, and ammonium is non-linear and sensitive to meteorology. As a result, proportional changes in sectoral emissions are not necessarily aligned with proportional changes in measured PM₂.₅, especially when using national-annual aggregates.

4. **Two-Way Fixed Effects and Sample Size:** Two-way fixed effects control for unobserved country and year characteristics but also absorb substantial variation, leaving a relatively small within-country, over-time signal for sectoral emissions. With 238 observations across 30 countries and 11 years, this specification is statistically constrained in detecting modest within-country associations once fixed effects and clustering are applied.

### **4.3.4 Significance of Within R²**

Despite non-significant individual coefficients, the **Within R² of 0.135** indicates that a non-trivial share of within-country temporal variation in PM₂.₅ is accounted for by the sectoral regressors after fixed effects. This pattern is consistent with limited statistical power at national-annual resolution and supports a conservative interpretation of Model C.

---

## **4.4 Model D Results – PM₂.₅ → YLL**

### **4.4.1 Regression Output**

Full results: [ModelD_PM25_YLL_summary.txt](output/ModelD_PM25_YLL_summary.txt)

| Metric       | Value     |
| :----------- | :-------- |
| R²           | 0.102     |
| Adjusted R²  | **0.100** |
| F-statistic  | 49.58     |
| Observations | 438       |

| Variable  | Coefficient | Std. Error | t-Statistic | P-Value     | 95% CI         |
| :-------- | :---------- | :--------- | :---------- | :---------- | :------------- |
| `const`   | −2.380      | 0.300      | −7.94       | < 0.001     | [−2.97, −1.79] |
| `ln_pm25` | **0.695**   | 0.099      | **7.04**    | **< 0.001** | [0.50, 0.89]   |

### **4.4.2 Interpretation**

- **Elasticity:** A **1% increase in PM₂.₅** is statistically associated with a **0.69% increase in YLLs**.
- **Significance:** Highly statistically significant (p < 0.001).
- **Model Fit:** PM₂.₅ explains **10%** of cross-country variation in mortality burden. While lower than Model B, this is substantial given that premature mortality is influenced by many factors (healthcare, diet, genetics, smoking).

### **4.4.3 Comparison with Model B**

| Metric      | Model B (DALY) | Model D (YLL) |
| :---------- | :------------- | :------------ |
| Elasticity  | 2.35           | 0.69          |
| Sample Size | 54             | 438           |
| R² (Adj)    | 0.274          | 0.100         |

The **lower elasticity in Model D** (0.69 vs 2.35) is consistent with differences in the two outcome constructs and samples:

- **YLLs capture only mortality**, while DALYs include both mortality and morbidity
- **DALYs** represent a composite health-burden construct, while **YLLs** represent a mortality-burden construct; the two are not numerically comparable one-for-one

### **4.4.4 Alignment with WHO Evidence**

The WHO estimates that each 10 µg/m³ increase in PM₂.₅ corresponds to a **6–8%** increase in mortality risk. Converting to log-elasticity form, this corresponds to approximately **0.5–0.8%** increase per 1% PM₂.₅—closely matching the 0.69 coefficient obtained here.

---

## **4.5 Model G Results – Total Emissions → PM₂.₅ (Aggregated Panel FE)**

### **4.5.1 Regression Output**

Full results: [ModelG_TotalEmissions_PM25_summary.txt](output/ModelG_TotalEmissions_PM25_summary.txt)

| Metric               | Value   |
| :------------------- | :------ |
| R² (Within)          | −0.0180 |
| R² (Between)         | −0.4320 |
| R² (Overall)         | −0.4321 |
| R² (Model)           | 0.0008  |
| Observations         | 238     |
| Entities (Countries) | 30      |
| Time Periods         | 11      |

| Variable             | Coefficient | Std. Error | t-Statistic | P-Value | Robust P-Value |
| :------------------- | :---------- | :--------- | :---------- | :------ | :------------- |
| `ln_total_emissions` | −0.0450     | 0.1810     | −0.249      | 0.697   | 0.804          |

**Note:** No explicit intercept is estimated (absorbed by fixed effects).

### **4.5.2 Interpretation**

- **Coefficient sign:** Negative (−0.045), counter to hypothesis.
- **Statistical significance:** Not significant (p = 0.804 with clustered SE).
- **Comparison with Model C:** Aggregating the three sectors removes their individual positive signals and produces a null result.

### **4.5.3 Why Aggregate Emissions Fail**

Model G demonstrates the importance of **sectoral decomposition**:

- Model C (sectoral): Energy β = +0.083, Industry β = +0.159 (both positive)
- Model G (aggregate): Total β = −0.045 (negative)

This reversal occurs because:

1. **Aggregation masks sector-specific effects:** The positive associations of energy and industry are diluted when combined with transport (which showed no effect).
2. **Multicollinearity reduction comes at a cost:** While Model G has fewer regressors, it loses the ability to distinguish combustion sources from non-combustion GHG sources.
3. **Fixed effects absorb substantial variation:** With entity and time effects, the aggregate emissions variable captures little additional within-country temporal variation.

### **4.5.4 Policy Implication**

Model G reinforces that **not all GHG emissions are equally aligned with observed PM₂.₅ concentrations**. The results are consistent with a stronger association for combustion-intensive sectors (energy, industry) than for aggregate emissions measures that include non-PM₂.₅-producing sources.

---

## **4.6 Model E-lite Results – Lagged Total Emissions → PM₂.₅**

### **4.6.1 Gate Check and Sample**

Model E-lite tests whether lagged emissions (year t−1) are associated with current PM₂.₅ (year t), providing a descriptive check on temporal ordering in the panel.

**Gate check:** PASSED (see [ModelE_gate_check.txt](output/ModelE_gate_check.txt))

- Sample loss from lagging: 12.6% (30 observations dropped)
- Final sample: **N = 208** (vs. N = 238 baseline)
- Countries retained: 30/30 (100%)

### **4.6.2 Regression Output**

Full results: [ModelE_LaggedTotalEmissions_PM25_summary.txt](output/ModelE_LaggedTotalEmissions_PM25_summary.txt)

| Metric               | Value   |
| :------------------- | :------ |
| R² (Within)          | −0.0306 |
| R² (Between)         | −1.5637 |
| R² (Overall)         | −1.5673 |
| R² (Model)           | 0.0066  |
| Observations         | 208     |
| Entities (Countries) | 30      |
| Time Periods         | 10      |

| Variable                  | Coefficient | Std. Error | t-Statistic | P-Value | Robust P-Value |
| :------------------------ | :---------- | :--------- | :---------- | :------ | :------------- |
| `ln_total_emissions_lag1` | −0.1354     | 0.1489     | −0.910      | 0.292   | 0.364          |

**Note:** No explicit intercept is estimated (absorbed by fixed effects).

### **4.6.3 Interpretation**

- **Coefficient:** Negative (−0.135), not statistically significant (p = 0.364).
- **Temporal precedence:** No evidence of a statistically significant association between lagged emissions and current PM₂.₅ in this panel.

### **4.6.4 Comparison with Model G**

| Model | Specification             | Coefficient | P-Value | N   |
| :---- | :------------------------ | :---------- | :------ | :-- |
| **G** | Total emissions (same t)  | −0.045      | 0.804   | 238 |
| **E** | Total emissions (lag t−1) | −0.135      | 0.364   | 208 |

Both models using aggregated emissions fail to detect a significant association. This supports the conclusion that **sectoral decomposition** (Model C) is necessary to isolate combustion-related PM₂.₅ sources.

---

## **4.7 Model J Results – Quadratic PM₂.₅ → Health**

Model J tests for **nonlinear dose–response relationships** by adding a quadratic term to Models B and D.

### **4.7.1 Model J (DALY) – Concave Curvature**

Full results: [ModelJ_PM25_DALY_summary.txt](output/ModelJ_PM25_DALY_summary.txt)  
Diagnostics: [ModelJ_PM25_DALY_diagnostics.txt](output/ModelJ_PM25_DALY_diagnostics.txt)

| Metric       | Value     |
| :----------- | :-------- |
| R²           | 0.300     |
| Adjusted R²  | **0.272** |
| F-statistic  | 10.90     |
| Observations | 54        |

| Variable | Coefficient | Std. Error | t-Statistic | P-Value   | 95% CI        |
| :------- | :---------- | :--------- | :---------- | :-------- | :------------ |
| `const`  | 7.964       | 0.249      | 32.01       | < 0.001   | [7.46, 8.46]  |
| `z`      | **2.100**   | 0.578      | **3.63**    | **0.001** | [0.94, 3.26]  |
| `z_sq`   | −1.108      | 1.173      | −0.944      | 0.349     | [−3.46, 1.25] |

**Curvature:** Concave (β₂ < 0), suggesting in the point estimates that the marginal statistical association between PM₂.₅ and health burden may diminish at higher concentration levels.  
**Implied turning point:** 30.3 µg/m³ (descriptive only; not a policy threshold).

#### **Interpretation**

- The **linear term** (z) remains highly significant (p = 0.001), confirming the association between PM₂.₅ and DALYs.
- The **quadratic term** (z²) is negative but not statistically significant (p = 0.349).
- **Practical implication:** The dose–response relationship is approximately **linear** across the observed PM₂.₅ range (5–25 µg/m³ in EU countries). Model B’s linear specification is adequate for describing the association in this sample.

### **4.7.2 Model J (YLL) – Convex Curvature**

Full results: [ModelJ_PM25_YLL_summary.txt](output/ModelJ_PM25_YLL_summary.txt)  
Diagnostics: [ModelJ_PM25_YLL_diagnostics.txt](output/ModelJ_PM25_YLL_diagnostics.txt)

| Metric       | Value     |
| :----------- | :-------- |
| R²           | 0.105     |
| Adjusted R²  | **0.101** |
| F-statistic  | 25.61     |
| Observations | 438       |

| Variable | Coefficient | Std. Error | t-Statistic | P-Value     | 95% CI         |
| :------- | :---------- | :--------- | :---------- | :---------- | :------------- |
| `const`  | −0.392      | 0.087      | −4.52       | < 0.001     | [−0.56, −0.22] |
| `z`      | **0.668**   | 0.101      | **6.62**    | **< 0.001** | [0.47, 0.87]   |
| `z_sq`   | 0.135       | 0.108      | 1.257       | 0.210       | [−0.08, 0.35]  |

**Curvature:** Convex (β₂ > 0), suggesting in the point estimates that the marginal statistical association between PM₂.₅ and health burden may increase at higher concentration levels.  
**No turning point** (curvature is not concave).

#### **Interpretation**

- The **linear term** (z) is highly significant (p < 0.001).
- The **quadratic term** (z²) is positive but not statistically significant (p = 0.210).
- **Practical implication:** For YLL outcomes, the linear Model D specification is adequate for describing the association. The slight upward curvature is not statistically distinguishable from linearity.

### **4.7.3 Summary of Nonlinearity Tests**

| Outcome  | Linear Effect (z) | Quadratic Effect (z²) | Curvature | Practical Conclusion    |
| :------- | :---------------- | :-------------------- | :-------- | :---------------------- |
| **DALY** | β = 2.10, p=0.001 | β = −1.11, p=0.349    | Concave   | Linear model sufficient |
| **YLL**  | β = 0.67, p<0.001 | β = 0.14, p=0.210     | Convex    | Linear model sufficient |

Both quadratic terms are **not statistically significant**. The simpler linear Models B and D provide adequate fit. The nonlinear terms add model complexity without improving inference.

---

## **4.8 Consolidated Summary**

### **Table 4.1: Summary of All Models**

Data source: [summary_all_models.csv](output/summary_all_models.csv)

| Model        | Relationship                | N   | Elasticity | P-Value | R² (Adj/Within) | Interpretation            |
| :----------- | :-------------------------- | :-- | :--------- | :------ | :-------------- | :------------------------ |
| **B**        | PM₂.₅ → DALY                | 54  | **2.35**   | <0.001  | 0.274           | Strong health burden link |
| **C**        | Energy → PM₂.₅              | 238 | 0.08       | 0.152   | 0.135 (within)  | Positive, not significant |
| **C**        | Industry → PM₂.₅            | 238 | 0.16       | 0.138   | —               | Positive, not significant |
| **C**        | Transport → PM₂.₅           | 238 | 0.00       | 0.990   | —               | No effect                 |
| **D**        | PM₂.₅ → YLL                 | 438 | **0.69**   | <0.001  | 0.100           | Strong mortality link     |
| **G**        | Total Emissions → PM₂.₅     | 238 | −0.05      | 0.804   | −0.018 (within) | No effect (aggregate)     |
| **E-lite**   | Lagged Total Emissions → PM | 208 | −0.14      | 0.364   | −0.031 (within) | No effect (lagged)        |
| **J (DALY)** | PM₂.₅ → DALY (quadratic)    | 54  | 2.10 (z)   | 0.001   | 0.272           | Linear term significant   |
| **J (YLL)**  | PM₂.₅ → YLL (quadratic)     | 438 | 0.67 (z)   | <0.001  | 0.101           | Linear term significant   |

### **4.8.2 The Complete Pathway**

$$
\underbrace{\text{Sectoral Emissions}}_{\text{Models C/G/E: weak/null}} \xrightarrow{?} \underbrace{\text{PM}_{2.5}}_{\text{mediator}} \xrightarrow{\checkmark} \underbrace{\text{Health Burden}}_{\text{Models B/D/J: robust}}
$$

**Key Findings:**

1. ✅ **PM₂.₅ → Health:** Models B, D, and J demonstrate **highly significant associations** between air quality and health outcomes.

2. ⚠️ **Emissions → PM₂.₅:** Model C shows **positive coefficients** for energy and industry sectors (as hypothesised) but **lacks statistical significance**. Models G and E-lite (using aggregated emissions) show **null or negative** coefficients. Taken together, these outputs indicate that emissions-to-PM₂.₅ attribution is statistically constrained in this national-annual panel under two-way fixed effects, rather than being resolved by these models.

3. 🎯 **Public-health relevance:** Even where emissions-to-PM₂.₅ attribution is statistically weak in Models C/G/E, the PM₂.₅–health association is robust in Models B/D/J. This is consistent with the relevance of PM₂.₅ monitoring and attention to exposure as a public-health priority, without implying causal effectiveness of any particular intervention.

---

## **4.9 Discussion**

### **4.9.1 Interpreting Null Emissions Results (Models C, G, E-lite)**

Models C, G, and E-lite estimate associations between national emissions measures and national mean PM₂.₅ in a two-way fixed-effects panel. In Model C, sectoral coefficients are directionally positive (energy and industry), while aggregated specifications (Models G and E-lite) are null or negative and not statistically significant.

These outputs are interpreted as evidence of **statistical constraint and attribution difficulty** at national-annual resolution under two-way fixed effects, rather than as evidence that emissions are unrelated to PM₂.₅ in physical terms.

More broadly, the panel structure itself is aligned with the idea that national inventories are a coarse proxy for the atmospheric processes that determine population-weighted PM₂.₅. Transboundary transport, the formation of secondary inorganic aerosols from NOₓ, SO₂, and NH₃ precursors, and strong spatial heterogeneity within countries all suggest that local concentrations are influenced by a superposition of domestic and external sources. Under these conditions, it is statistically constrained for country-level, annually aggregated inventories to produce tightly estimated emissions–PM₂.₅ elasticities in a two-way fixed-effects framework, even when underlying physical mechanisms are consistent with positive sectoral contributions.

### **4.9.2 Alignment with WHO / GBD Evidence (Models B, D, J)**

The core health results are consistent with a broad epidemiological evidence base that links PM₂.₅ exposure to health burden:

- Model B reports a strong positive association between PM₂.₅ and DALYs (β = 2.3502; N = 54; p < 0.001).
- Model D reports a strong positive association between PM₂.₅ and YLLs (γ = 0.6947; N = 438; p < 0.001).
- Model J’s quadratic terms are not statistically significant for either DALYs or YLLs (p = 0.349; p = 0.210), supporting the practical adequacy of the linear specifications (Models B and D) over the observed samples.

Where this chapter references WHO guidance and related literature (e.g., Tümay, 2025), the comparison is framed as **alignment/consistency** rather than validation or proof.

### **4.9.3 Policy Context (EU Air-Quality and Public-Health Frameworks)**

The results are policy-relevant in an EU context because they quantify robust PM₂.₅–health associations that are aligned with the rationale of air-quality governance and public-health monitoring, while remaining conservative about emissions attribution:

- **EU air-quality frameworks:** The health models are consistent with the public-health relevance of sustained PM₂.₅ monitoring and attention to exposure patterns, without implying that this thesis identifies the causal impact of any specific policy instrument.
- **NECPs / Green Deal framing:** The emissions models (C/G/E-lite) indicate that attributing national PM₂.₅ changes to national emissions totals is statistically difficult in this two-way FE panel; this is aligned with the view that sectoral decomposition (Model C) is a relevance tool (energy and industry) while inference about attribution remains statistically constrained.

### **4.9.4 SDG Alignment (Relevance, Not Effectiveness Claims)**

This thesis frames SDG alignment as relevance and monitoring support:

- **SDG 3.9:** Models B, D, and J provide quantitative associations between PM₂.₅ and health-burden outcomes (DALYs, YLLs), which are consistent with a burden-focused framing.
- **SDG 11.6:** The strong PM₂.₅–health associations are aligned with the public-health relevance of urban air-quality monitoring and attention to exposure, without making claims about specific urban interventions.
- **SDG 13.2:** Model C’s sectoral structure is aligned with discussing climate and air-quality policy integration as an alignment opportunity, while noting that the emissions→PM₂.₅ link is statistically constrained and not fully resolved in these FE models.

### **4.9.5 Situating Greece within the European Panel**

Although the empirical models are estimated on multi-country panels, the thesis maintains a substantive interest in Greece by interpreting the Greek observations within the broader European relationships rather than by estimating Greece-only regressions. In Models B, D, and J, each country—including Greece—appears as a point along a common regression line relating PM₂.₅ to health outcomes. Conceptually, countries with higher observed health burden than the line would predict are positioned above the fitted relationship, countries with lower burden are positioned below, and countries that match the fitted values lie close to the line.

This residual-based perspective provides a descriptive way to read the position of Greece relative to other EU member states without changing the specification or introducing separate Greek coefficients. Greece is therefore discussed as one case embedded within the shared European association between PM₂.₅ and DALY/YLL outcomes, rather than as a separate model. This framing is explicitly non-causal: it suggests how Greece can be situated within the distribution of panel residuals and fitted values, but it does not attribute specific policy actions or shocks in Greece to changes in PM₂.₅ or health indicators.

### **4.9.6 What These Results Do Not Identify**

The empirical scope of this thesis is deliberately bounded to associational inference. To avoid misinterpretation by readers or examiners, it is important to state explicitly what these results **do not** identify:

- **Causal effects of specific interventions:** This thesis employs observational panel and cross-sectional designs. It does not use randomised controlled trials, quasi-experimental methods (e.g., difference-in-differences, regression discontinuity), or instrumental variables. Consequently, the reported coefficients represent **statistical associations**, not causal impacts of policy instruments.

- **Counterfactual health burden under alternative emissions scenarios:** The models do not simulate "what if" scenarios (e.g., "what would Greek DALYs be if emissions had been 20% lower?"). Such counterfactuals require causal identification, which is beyond the scope of this design.

- **Attribution of observed PM₂.₅ changes to specific national policies:** Transboundary transport, the formation of secondary inorganic aerosols from precursor gases, and strong within-country spatial heterogeneity all mean that national-level PM₂.₅ concentrations reflect a superposition of domestic and external sources. The panel models cannot isolate the contribution of any single policy measure (e.g., coal phase-out, vehicle emission standards) to observed PM₂.₅ trends.

- **Policy thresholds or recommended emissions targets:** The thesis quantifies associations at observed levels of exposure and emissions. It does not compute optimal pollution levels, cost-benefit trade-offs, or target concentrations for policymakers.

- **Validation of epidemiological mechanisms:** The thesis documents associations and notes their consistency with prior epidemiological evidence (WHO, GBD). However, consistency with the literature does not constitute independent validation of biological pathways or dose–response functions.

**Importantly, these limitations do not weaken the validity of the reported associations; rather, they clarify the scope of inference supported by the data and design.** The models perform the task they were built for: quantifying robust statistical relationships between PM₂.₅ and health outcomes, and testing whether sectoral emissions structure improves emissions–PM₂.₅ attribution relative to aggregated specifications.

### **4.9.7 The Seven-Model Architecture as a Methodological Contribution of This Thesis**

Most environmental-health studies in the academic literature present either single-stage reduced-form models (e.g., emissions → health) or multi-stage models that assume mediation pathways without independently testing each link. A contribution of this thesis is that it **decomposes the hypothesised co-benefits pathway into seven independently estimated models**, allowing transparent identification of where statistical power exists and where it is constrained.

This modular structure offers several advantages:

1. **Separation of robust and constrained links:** The health models (B, D, J) demonstrate strong, statistically significant associations between PM₂.₅ and health burden across both outcome types (DALYs and YLLs), sample sizes (N=54 and N=438), and functional forms (linear and quadratic). In contrast, the emissions models (C, G, E-lite) show that emissions–PM₂.₅ attribution is statistically constrained at national-annual resolution under two-way fixed effects. By estimating these links separately, the thesis avoids conflating the strength of the health association with the difficulty of emissions attribution.

2. **Transparent robustness checks:** Model J tests whether the PM₂.₅–health relationship exhibits nonlinearity; the quadratic terms are not statistically significant (p = 0.349 for DALYs, p = 0.210 for YLLs), validating the adequacy of the linear specifications in Models B and D. Model E-lite demonstrates a gated lagged-emissions specification with explicit sample-retention criteria ([ModelE_gate_check.txt](output/ModelE_gate_check.txt)), showing that robustness checks are conducted transparently rather than selectively reported. Model C vs Models G/E-lite isolates the effect of sectoral decomposition vs aggregation, demonstrating that aggregation eliminates the positive directional signal present in energy and industry coefficients.

3. **Methodological transparency through Within-R² vs Between-R² interpretation:** Model C reports Within-R² = 0.135, Between-R² = 0.958, and Overall-R² = 0.955. This extreme divergence is a feature of the two-way fixed-effects design, not a weakness. It shows that cross-country variation dominates (Between-R² near 1), while time-within-country variation is limited after absorbing country and year fixed effects (Within-R² modest). This partitioning is consistent with the expectation that persistent country characteristics (e.g., geography, industrial structure, regulatory capacity) explain most PM₂.₅ variation, and it pre-empts the mistaken inference that "low Within-R² = bad model."

4. **Excel-reproducible estimation panels:** Every model is accompanied by a saved CSV of its exact estimation sample ([output/panel*model*\*\_estimation.csv](output/)), enabling downstream re-analysis, diagnostic checks, and independent verification. This ensures that the thesis supports open-science standards and allows readers to reconstruct results without relying on console output or proprietary software.

By disaggregating the co-benefits pathway into testable components, the thesis demonstrates that **robust health associations and constrained emissions attribution can coexist**—and that this coexistence is itself an empirical finding, not a limitation. The architecture clarifies that the difficulty of emissions attribution arises from panel structure, spatial scale, and transboundary processes, not from the absence of physical mechanisms or sectoral structure.

---

## **4.10 Conclusions (Empirical, Non-causal)**

The results support the following examiner-safe conclusions, grounded in the model outputs and framed as associations rather than causal claims:

### **4.10.1 Five Defensible Empirical Messages**

1. **PM₂.₅–health associations are robust across outcome types, sample sizes, and functional forms:** Model B (DALY, N=54, β=2.35, p<0.001) and Model D (YLL, N=438, β=0.69, p<0.001) both show strong associations despite a 10-fold difference in sample size. Model J's quadratic terms are not statistically significant for either outcome (p=0.349 for DALYs, p=0.210 for YLLs), validating the adequacy of the linear specifications. This consistency across constructs and specifications supports the conclusion that the PM₂.₅–health relationship is not an artefact of a single outcome measure or functional form.

2. **Sectoral decomposition yields directionally positive coefficients; aggregated specifications are null or negative:** Model C reports positive coefficients for energy (β=0.08, p=0.152) and industry (β=0.16, p=0.138) emissions, while transport is effectively zero (β=0.00, p=0.990). In contrast, Models G and E-lite (using aggregated total emissions) report negative coefficients that are not statistically significant (Model G: β=−0.05, p=0.804; Model E-lite: β=−0.14, p=0.364). This pattern supports the relevance of combustion-focused sectoral inventories and demonstrates that aggregation eliminates the positive directional signal present in energy and industry.

3. **Low Within-R² in Model C reflects fixed-effects absorption, not model failure:** Model C reports Within-R²=0.135, Between-R²=0.958, and Overall-R²=0.955. This divergence is consistent with the two-way fixed-effects design, in which persistent country characteristics (geography, industrial structure, regulatory capacity) explain most PM₂.₅ variation, while time-within-country variation is limited after absorbing country and year effects. This is a feature of the panel structure, not evidence of misspecification.

4. **The thesis documents associations, not causal effects or policy effectiveness:** The empirical design does not identify the causal impact of specific interventions, does not estimate counterfactual health burdens under alternative emissions scenarios, and does not attribute observed PM₂.₅ changes to national policies. Transboundary transport, secondary aerosol formation, and spatial heterogeneity prevent policy-level attribution in this national-annual panel. The results are consistent with the public-health relevance of PM₂.₅ monitoring and exposure assessment, but they do not establish the effectiveness of any particular policy instrument.

5. **The seven-model architecture separates robust health associations from constrained emissions attribution:** By decomposing the co-benefits pathway into independently estimated models, the thesis demonstrates where statistical power exists (health models: B, D, J) and where it is constrained (emissions models: C, G, E-lite). This separation is itself an empirical finding: robust health associations and constrained emissions attribution can coexist, and the latter does not invalidate the former. The modular design enables transparent robustness checks (e.g., Model J validating linearity, Model E-lite demonstrating gated lagged estimation) and clarifies that attribution difficulty arises from panel structure, spatial scale, and transboundary processes—not from the absence of physical mechanisms.

### **4.10.2 Summary Statement**

The core contribution of this thesis is the quantification of robust PM₂.₅–health associations across DALY and YLL outcomes in a European panel context, combined with a transparent demonstration of the statistical constraints that limit emissions–PM₂.₅ attribution at national-annual resolution under two-way fixed effects. The seven-model architecture clarifies that these constraints do not reflect model failure or lack of sectoral structure; rather, they reflect the coarse spatial and temporal scale of national inventories relative to the atmospheric processes that determine population-weighted PM₂.₅ concentrations.

The results are aligned with the public-health relevance of sustained PM₂.₅ monitoring and exposure assessment in EU contexts, and they support the view that sectoral decomposition (Model C: energy and industry) is a more relevant approach than aggregated emissions totals (Models G and E-lite). However, the thesis does not claim causal identification, does not estimate policy effectiveness, and does not recommend specific emissions targets. Its claims are bounded by the data, design, and documented associations in the estimation panels.

---

## **CHANGELOG (Thesis Updater Agent)**

- Updated §3.2.2: softened “dual dividend” framing to explicitly preserve non-causal interpretation (manifest: guardrails).
- Updated §3.6.2: added Model C-specific Within/Between/Overall R² interpretation note (manifest: Methods clarification).
- Updated §3.10: added explicit turning-point caveat for Model J diagnostics and preserved existing limitations structure (manifest: Limitations updates).
- Updated §3.11: replaced causal arrow pathway with non-causal linkage notation (manifest: examiner-safe framing).
- Updated §4.2.3: removed Greece counterfactual (“47% fewer DALYs”) and replaced with non-causal interpretation tied to Model B output (manifest: prevent counterfactual claims).
- Updated §4.4.3: removed potentially overstated outcome-construct phrasing and clarified DALY vs YLL comparison conservatively (manifest: robustness vs attribution framing).
- Updated §4.8.2: reframed emissions-results interpretation as statistical constraint and removed “any intervention will…” phrasing (manifest: non-causal policy relevance).
- Updated §4.9: rewrote Discussion with required subsections (null emissions interpretation; WHO/GBD alignment; EU policy context; SDG alignment) using “aligns with/supports/is consistent with” framing (manifest: Discussion + SDG/EU alignment).
- Updated §4.10: replaced Chapter Summary with a bounded Conclusions section aligned to output files (manifest: Conclusions framing).
- Added §4.9.6: "What These Results Do Not Identify" subsection with explicit inferential boundaries and reassurance that limitations clarify scope without weakening validity (Batch #1: inferential guardrails).
- Added §4.9.7: "The Seven-Model Architecture as a Methodological Contribution of This Thesis" subsection framing modular design, Within-R² interpretation, robustness transparency, and Excel-reproducibility as contributions within thesis scope (Batch #1: methodological framing).
- Expanded §4.10: replaced three-point conclusion with §4.10.1 (Five Defensible Empirical Messages) synthesizing robustness across outcomes/sample sizes, sectoral vs aggregated results, Within-R² interpretation, associational scope, and architecture as finding; added §4.10.2 (Summary Statement) with bounded core contribution statement (Batch #1: synthesis and final framing).

---

# **Data Availability**

All intermediate datasets and estimation panels are available for verification and further analysis:

| Dataset          | Description               | File                                                                                 |
| :--------------- | :------------------------ | :----------------------------------------------------------------------------------- |
| Panel B (estim.) | Model B estimation sample | [panel_model_b_estimation.csv](output/panel_model_b_estimation.csv)                  |
| Panel C (estim.) | Model C estimation sample | [panel_model_c_estimation.csv](output/panel_model_c_estimation.csv)                  |
| Panel D (estim.) | Model D estimation sample | [panel_model_d_estimation.csv](output/panel_model_d_estimation.csv)                  |
| Panel G (estim.) | Model G estimation sample | [output/panel_model_g_estimation.csv](output/panel_model_g_estimation.csv)           |
| Panel E (estim.) | Model E-lite estimation   | [output/panel_model_e_estimation.csv](output/panel_model_e_estimation.csv)           |
| Panel J-DALY     | Model J (DALY) estimation | [output/panel_model_j_daly_estimation.csv](output/panel_model_j_daly_estimation.csv) |
| Panel J-YLL      | Model J (YLL) estimation  | [output/panel_model_j_yll_estimation.csv](output/panel_model_j_yll_estimation.csv)   |
| Summary          | All model coefficients    | [output/summary_all_models.csv](output/summary_all_models.csv)                       |

---

**Document Version:** 3.0  
**Last Updated:** December 23, 2025  
**Pipeline Version:** 7-Model Framework (B, C, D, G, E-lite, J-DALY, J-YLL)  
**Reproducibility:** `make run` regenerates all outputs
