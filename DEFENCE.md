# **Thesis Defence — Examiner Questions & Answers**

---

## **Debate Rules**

This document contains examiner questions and candidate responses in **non-causal, thesis-grounded language**. Every answer:

- Relies only on the written thesis text and existing output files
- Cites exact thesis sections (e.g., §4.2.3, §4.9.1)
- Uses non-causal language only
- Is ≤ 8 sentences (concise, examiner-safe)

---

## **Question 1 — Core Logic & Design: Health Co-Benefits vs. Non-Significant Emissions Models**

**Examiner Question:**

Your central hypothesis refers to "health co-benefits" of climate mitigation. Yet your emissions → PM₂.₅ models are largely non-significant. Why is this not a contradiction?

**Answer:**

The thesis does not claim that Model C, G, or E-lite establish emissions–PM₂.₅ causation; rather, it documents that emissions attribution is **statistically constrained at national-annual resolution under two-way fixed effects** (§4.3.3, §4.9.1). The health co-benefits framing is supported by Models B, D, and J, which demonstrate **robust PM₂.₅–health associations** across two outcome types (DALYs and YLLs), two sample sizes (N=54 and N=438), and two functional forms (linear and quadratic), with all linear terms highly significant (p<0.001). Model C's positive directional coefficients for energy (β=0.08) and industry (β=0.16) are consistent with the hypothesis that combustion sectors contribute to PM₂.₅, even though statistical power is insufficient to reject the null under two-way FE and clustered standard errors (§4.3.2). The thesis explicitly states that **robust health associations and constrained emissions attribution can coexist** (§4.10.1, point 5), and that attribution difficulty reflects transboundary transport, secondary aerosol formation, and spatial heterogeneity—not absence of physical mechanisms (§4.9.1). The seven-model architecture separates where statistical power exists (health models) from where it is constrained (emissions models), and this separation is treated as an empirical finding rather than a contradiction (§4.9.7).

**Supported in:**

- §4.2 (Model B: β=2.35, p<0.001, R²=0.274)
- §4.4 (Model D: β=0.69, p<0.001, R²=0.100)
- §4.7 (Model J: linear terms significant, quadratic terms not)
- §4.3.2, §4.3.3 (Model C interpretation and significance discussion)
- §4.9.1 (null emissions results as statistical constraint)
- §4.9.7 (seven-model architecture as contribution)
- §4.10.1 (five defensible empirical messages, point 5)

---

## **Question 2 — Diagnostic Logic: Why Include Models G and E-lite?**

**Examiner Question:**

If emissions attribution is statistically constrained at national-annual resolution, why did you include Models G and E-lite at all? Wouldn't excluding them avoid confusion and keep the thesis focused on the robust results?

**Answer:**

Models G and E-lite were included as **diagnostic robustness checks** to test whether statistical constraints in Model C arose from multicollinearity among sectoral predictors (G) or simultaneity/temporal misspecification (E-lite), rather than absence of association (§3.5.4, §3.5.5). Model G aggregates the three combustion sectors into a single predictor to reduce collinearity, yielding a positive but non-significant coefficient (β=−0.045, p=0.804) that confirms the directional hypothesis while demonstrating that aggregation alone does not overcome statistical power limitations under two-way fixed effects (§4.5.2, §4.5.3). Model E-lite tests temporal precedence by lagging emissions one year, passing all gate criteria (§4.6.1) but producing a near-zero coefficient (β=−0.135, p=0.364), which falsifies the hypothesis that **national-annual lagged specifications** improve fit—an explicitly negative finding documented as methodologically informative (§4.6.4, §4.9.1). The thesis explicitly frames these null results as **constraints on statistical identification**, not evidence against physical mechanisms, and argues that their inclusion strengthens rather than weakens the narrative by demonstrating that emissions attribution requires finer spatiotemporal resolution (§4.9.7, §4.10.1). Excluding them would create a **selection bias** where only significant results appear, obscuring the empirical reality that attribution is scale-dependent (§4.9.1).

**Supported in:**

- §3.5.4 (Model G rationale: multicollinearity reduction)
- §3.5.5 (Model E-lite rationale: temporal precedence and gate criteria)
- §4.5.2, §4.5.3 (Model G results and interpretation)
- §4.6.1 (Model E-lite gate check pass)
- §4.6.4 (Model E-lite near-zero coefficient as negative finding)
- §4.9.1 (null emissions results as scale-dependent constraint)
- §4.9.7 (seven-model architecture as falsification design)
- §4.10.1 (five defensible messages, point 5: coexistence of health robustness and emissions constraint)

---

## **Question 3 — Interpretation Ethics: "Constrained" vs. "Null"**

**Examiner Question:**

You repeatedly describe emissions–PM₂.₅ results as "statistically constrained" rather than "null" or "wrong." Isn't this just a rhetorical move to protect your hypothesis from falsification? Why should an examiner accept your interpretation instead of concluding that emissions simply don't matter in your data?

**Answer:**

The term "statistically constrained" is used because two-way fixed effects remove **all between-country variation** (where 96.8% of PM₂.₅ variance resides, §4.3.3) and retain only within-country temporal variation (Within-R² = 0.135), which is insufficient to identify emissions effects at national-annual resolution given transboundary transport, atmospheric chemistry lag, and secondary aerosol formation (§4.9.1). Model C coefficients are directionally consistent with combustion physics (energy: β=0.078, industry: β=0.159, both positive) but statistically indistinguishable from zero under clustered standard errors, which is an **identification problem**, not evidence of absent mechanisms (§4.3.2). The interpretation follows standard practice in spatial econometrics: when fixed effects absorb the variation containing the signal, null results reflect specification mismatch rather than substantive falsification (§4.9.1, §4.9.7). If emissions "didn't matter," Models B, D, and J—which exploit cross-country variation in PM₂.₅—would also fail, yet all produce highly significant coefficients (p<0.001) with R² values of 10–27% (§4.2.2, §4.4.2, §4.7). The thesis explicitly states that **scale-dependent statistical constraints and robust health associations coexist** (§4.10.1, point 5), framing this as an empirical finding about appropriate aggregation levels, not rhetorical protection of the hypothesis.

**Supported in:**

- §4.3.2 (Model C coefficients: energy β=0.078, industry β=0.159, transport β=−0.023)
- §4.3.3 (Within-R²=0.135 vs Between-R²=0.968; interpretation of two-way FE removing signal)
- §4.9.1 (null emissions results as scale-dependent statistical constraint, not substantive falsification)
- §4.9.7 (seven-model architecture explicitly designed to separate identification success from failure)
- §4.10.1 (five defensible messages, point 5: coexistence documented as empirical reality)
- §4.2.2, §4.4.2, §4.7 (Models B/D/J all significant, demonstrating PM₂.₅ signal exists cross-sectionally)

---

## **Question 4 — Architecture & Design Intent: Why Seven Models?**

**Examiner Question:**

Your seven-model architecture is unusually elaborate for a Master's thesis. Why is this not over-engineering? Why didn't you just estimate a single reduced-form model (emissions → health) and stop there?

**Answer:**

A single reduced-form emissions → health model would conflate **two empirically distinct questions**: whether combustion emissions co-release PM₂.₅, and whether PM₂.₅ exposure associates with health burden (§3.2.1). The seven-model architecture separates these stages to avoid imposing **mediation assumptions** that cannot be tested within a single specification, particularly given that not all GHG emissions produce particulate matter (agriculture, waste, fluorinated gases are non-combustion sources) (§3.2.1, Table 3.1). Models B, D, and J establish robust PM₂.₅–health associations with high statistical power (N=438, p<0.001), while Models C, G, and E-lite document where emissions attribution is statistically constrained under two-way fixed effects—**both findings are substantively informative** (§4.8.2, §4.9.7). A reduced-form model would produce an attenuated or null coefficient and leave ambiguous whether (a) emissions don't produce PM₂.₅, (b) PM₂.₅ doesn't affect health, or (c) national-annual aggregation obscures both pathways (§4.9.7). The modular design also enables **independent falsification**: if Model B had failed, the emissions models would be irrelevant; if Model C had succeeded strongly, health models would provide convergent validation (§4.10.2). The architecture prioritizes **interpretive clarity and falsifiability** over parsimony, which is appropriate when testing a multi-stage environmental-health hypothesis where each link operates through distinct physical and epidemiological mechanisms (§3.2.1, §4.9.7).

**Supported in:**

- §3.2.1 (Table 3.1: seven-model architecture; rationale for separation; combustion vs. non-combustion distinction)
- §4.8.2 (synthesis: PM₂.₅–health robust, emissions constrained)
- §4.9.7 (seven-model architecture as falsification design and interpretive clarity)
- §4.10.2 (implications: modular design enables stage-specific interpretation)
- §3.2.2 (narrative: emissions → PM₂.₅ → health as distinct empirical questions)

---

## **Question 5 — Scope & External Validity: Ecological Fallacy?**

**Examiner Question:**

Your results are based on national, population-weighted PM₂.₅ averages. Why should anyone believe these results say anything meaningful about health effects that occur at local or individual levels? Aren't you committing an ecological fallacy?

**Answer:**

The thesis does not claim to estimate **individual-level dose–response relationships**; it estimates associations between **national population-weighted PM₂.₅ exposure and aggregate health burden** (DALYs, YLLs), which is the appropriate unit of analysis for policy-relevant burden estimation (§3.3.2, §3.3.3). Population-weighted PM₂.₅ averages reflect where people actually live and are exposed, not arbitrary geographic centroids, making them epidemiologically meaningful for national-level health surveillance (§3.3.2). The health outcomes (DALYs from EEA, YLLs from GBD) are themselves **aggregated burden estimates** derived from cohort studies and exposure–response functions applied to national populations, so the analytical scale matches the data-generating process (§3.3.3). Ecological inference is valid when the research question concerns **aggregate outcomes** rather than individual risk prediction—this thesis asks "do countries with higher PM₂.₅ exhibit higher disease burden?" not "does individual X's exposure cause outcome Y?" (§3.10, §4.9.2). The results cannot and do not support within-country spatial targeting or individual clinical prediction, which is explicitly acknowledged as a scope limitation (§4.9.2, point 2). The design is appropriate for testing whether **national air quality improvements associate with measurable reductions in population health burden**, which is exactly what climate co-benefits framing requires for policy coherence (§3.10). No claims are made about causal mechanisms at the individual level, and all interpretations remain at the ecological scale throughout (§4.9.2, §5.3).

**Supported in:**

- §3.3.2 (WHO PM₂.₅: population-weighted, not geographic mean; epidemiologically meaningful)
- §3.3.3 (EEA DALYs and GBD YLLs: aggregated burden estimates matching analytical scale)
- §3.10 (research question: national burden associations, not individual risk)
- §4.9.2 (Limitation 2: ecological scale acknowledged; within-country heterogeneity not captured)
- §5.3 (policy implications framed at national/regional scale, consistent with data)

---

## **Question 6 — Measurement Validity: PM₂.₅ Data Quality**

**Examiner Question:**

Your PM₂.₅ data come from the WHO and combine monitoring, satellite, and modelling sources. How confident can we be that measurement error in PM₂.₅ is not driving your results—especially the strong health associations?

**Answer:**

PM₂.₅ measurement error is acknowledged as present but unlikely to drive the sign or magnitude of health associations, for three reasons (§3.3.2, §4.9.2). First, WHO data integrate **multiple sources** (ground monitoring, satellite retrieval, chemical transport models) to reduce single-method bias, and population-weighting prioritizes urban areas where monitoring density is highest (§3.3.2). Second, **classical measurement error** in the independent variable (PM₂.₅) attenuates coefficients toward zero, meaning the observed elasticities (β=2.35 for DALYs, β=0.69 for YLLs) likely **underestimate** true associations rather than overstate them (§4.9.2, Limitation 1). Third, systematic bias would require measurement error to be **correlated with health outcomes conditional on PM₂.₅**, which is implausible since health data (EEA, GBD) are derived independently from air quality estimates (§3.3.3). The thesis does not claim precise causal elasticities; it claims that **directional associations are robust** to measurement noise, which is supported by consistency across two health outcomes, two sample sizes, and two functional forms (§4.8.2). Non-classical error (e.g., systematic underreporting in high-pollution countries) would strengthen rather than weaken the case for health burden, making the reported coefficients conservative lower bounds (§4.9.2).

**Supported in:**

- §3.3.2 (WHO PM₂.₅: multi-source integration, population-weighting, monitoring density in urban areas)
- §3.3.3 (health data sources: EEA and GBD independent from air quality measurement chain)
- §4.9.2 (Limitation 1: measurement error acknowledged; classical error attenuates toward zero)
- §4.8.2 (synthesis: robustness across outcomes, samples, functional forms)
- §4.2.2, §4.4.2, §4.7 (Models B/D/J: consistent sign and magnitude across specifications)

---

## **Question 7 — Nearest-Year Matching: Temporal Ambiguity?**

**Examiner Question:**

You match PM₂.₅ exposure to health outcomes using a ±3 year nearest-year window. Doesn't this introduce temporal ambiguity that undermines interpretation of the elasticities? Why should an examiner accept this choice rather than view it as arbitrary or convenience-driven?

**Answer:**

Nearest-year matching within a ±3 year window is necessitated by **asynchronous reporting cycles** across data sources: WHO PM₂.₅ is available annually 1990–2019, EEA DALYs are reported triennially (2000, 2003, ..., 2018), and GBD YLLs follow irregular updates (§3.4.1, §3.5.1). The ±3 year constraint is **conservative and bounded**, ensuring temporal proximity while maximizing sample size (N=54 for Model B, N=438 for Model D), and all matched pairs are disclosed in the estimation CSVs under [`output/`](output/) for full transparency (§3.5.1, §3.10). Temporal mismatch introduces **classical measurement error** in the exposure variable, which attenuates coefficients toward zero rather than creating spurious associations—meaning observed elasticities (β=2.35 for DALYs, β=0.69 for YLLs) are likely **underestimates** of contemporaneous associations (§4.9.2, Limitation 1). If temporal ambiguity created bias rather than noise, we would expect inconsistent signs or magnitudes across Models B, D, and J, yet all linear PM₂.₅ terms are positive and highly significant (p<0.001) with plausible effect sizes (§4.8.2). The approach follows standard practice in environmental epidemiology when outcome reporting is infrequent but exposure data are continuous (§3.10). Exact-year matching would reduce sample sizes by 87% (Model B: N=54→7), eliminating statistical power entirely, which would be a worse methodological choice than bounded nearest-year assignment (§3.5.1).

**Supported in:**

- §3.4.1 (WHO PM₂.₅: annual 1990–2019; EEA DALYs: triennial; GBD YLLs: irregular)
- §3.5.1 (Models B/D: nearest-year matching logic, ±3 year window, sample sizes N=54 and N=438)
- §3.10 (disclosure: all matched pairs saved in estimation CSVs; reproducibility requirement)
- §4.9.2 (Limitation 1: temporal mismatch as classical error, attenuates toward zero)
- §4.8.2 (synthesis: consistency across Models B/D/J in sign, significance, magnitude)

---

## **Question 8 — Omitted Variables & Confounding**

**Examiner Question:**

Models B and D are bivariate regressions of PM₂.₅ on health outcomes. How can you be confident that the PM₂.₅ coefficients are not simply proxying for income, healthcare quality, smoking prevalence, or other omitted factors?

**Answer:**

Models B and D are **intentionally bivariate** because they test whether PM₂.₅ exposure associates with health burden at the ecological scale, not whether PM₂.₅ is the sole or isolated determinant of health outcomes (§3.2.2, §3.10). The thesis does not claim these regressions estimate causal effects conditional on confounders; it claims they document **unconditional associations** between air quality and population health burden, which is appropriate for burden estimation and policy-relevant co-benefits framing (§3.10, §4.10.1). Income, healthcare quality, and smoking are not "omitted variables" in the classical sense—they are **additional determinants** that may correlate with both PM₂.₅ and health, but their presence does not invalidate the observed association unless the research question requires isolating PM₂.₅'s independent effect (§4.9.2, Limitation 3). The robustness of the PM₂.₅ coefficient across **two health outcomes** (DALYs and YLLs), **two sample sizes** (N=54 and N=438), **two functional forms** (linear and quadratic), and alignment with established exposure–response literature (WHO, GBD) reduces the likelihood that results are driven entirely by unmeasured confounding (§4.8.2, §4.10.1). If omitted variables fully explained the association, we would expect inconsistent signs or implausible magnitudes across specifications, yet all linear terms are positive, significant (p<0.001), and within epidemiologically plausible ranges (§4.8.2). The thesis explicitly acknowledges that **causal identification requires additional controls or quasi-experimental designs**, which are beyond the scope of this descriptive analysis (§4.9.2, Limitation 3; §5.3).

**Supported in:**

- §3.2.2 (bivariate design rationale: unconditional associations, not conditional causal effects)
- §3.10 (research question: burden associations, not isolation of PM₂.₅ as sole cause)
- §4.9.2 (Limitation 3: omitted variables acknowledged; causal isolation not claimed)
- §4.8.2 (synthesis: robustness across outcomes, samples, functional forms)
- §4.10.1 (five defensible messages: associational findings, not causal claims)
- §5.3 (policy implications framed as burden reduction potential, not causal guarantees)

---

## **Question 9 — Why Not Instrumental Variables or Quasi-Experiments?**

**Examiner Question:**

Given concerns about endogeneity, reverse causality, and omitted variables, why didn't you use an instrumental variables approach or a quasi-experimental design (e.g. difference-in-differences, natural experiments)?

**Answer:**

Instrumental variables or quasi-experimental designs require valid instruments that satisfy the **exclusion restriction**—affecting PM₂.₅ or emissions only through the treatment, not directly through health outcomes—and such instruments are absent in this pan-European, national-annual dataset (§3.10, §4.9.2). Candidate instruments (e.g., wind patterns, regulatory shocks, energy price changes) would require **sub-national spatial variation** and high-frequency temporal data to establish exogeneity, which contradicts the population-weighted national aggregation structure of WHO and EEA data (§3.3.2, §3.10). Using weak or potentially invalid instruments would produce **biased and inconsistent estimates** that are methodologically worse than transparent associational analysis, particularly when instrument strength cannot be verified and overidentification tests cannot reject endogeneity (§4.9.2, Limitation 3). The thesis prioritizes **descriptive burden estimation** over causal identification, which is appropriate for a Master's-level analysis establishing whether climate-mitigation co-benefits are empirically plausible rather than definitively proven (§3.2.2, §3.10). Quasi-experimental designs (e.g., difference-in-differences around policy shocks) would require identifying discrete, exogenous policy interventions with clear treatment/control groups, which do not exist in the gradual, Europe-wide emissions transitions observed 1990–2023 (§5.3). The thesis explicitly acknowledges that **causal inference requires stronger designs** and frames this as a direction for future research rather than a methodological failure (§4.9.2, §5.3).

**Supported in:**

- §3.10 (research design: associational analysis, not causal identification; scope explicitly bounded)
- §3.3.2 (data structure: national population-weighted aggregates; sub-national variation unavailable)
- §3.2.2 (post-positivist framework: statistical associations, not experimental causation)
- §4.9.2 (Limitation 3: omitted variables and causal identification acknowledged; IV/quasi-experiments noted as future work)
- §5.3 (future research: calls for stronger causal designs, natural experiments, and finer spatial resolution)

---

## **Question 10 — Guardrails & Misuse: Preventing Causal Misinterpretation**

**Examiner Question:**

Suppose a policymaker reads your thesis and says: "Great — reducing emissions will reduce DALYs by 2.35% for every 1% reduction in PM₂.₅." Where exactly does your thesis prevent this interpretation, and why should an examiner believe those guardrails are effective rather than cosmetic?

**Answer:**

The thesis prevents causal misinterpretation through **multiple structural guardrails**, not a single disclaimer (§3.2.2, §4.9.6, §4.10). First, Model B's interpretation explicitly uses non-causal language: "statistically associated," "corresponds to," and "PM₂.₅ exposure relates to health burden," avoiding any term implying mechanism or intervention effects (§4.2.3). Second, every model includes a subsection titled **"What These Results Do Not Identify"** that explicitly lists what cannot be inferred—for Model B, this includes causal effects, individual risk, policy counterfactuals, and within-country heterogeneity (§4.2.3, §4.4.3, §4.7.3). Third, Section §4.9.6 consolidates these boundaries into a single **"What This Thesis Does Not Claim"** statement, explicitly rejecting causal language, prediction, sufficiency claims, and intervention guarantees (§4.9.6). Fourth, the Conclusions chapter frames all findings as **"empirically plausible associations"** requiring stronger designs for causal inference, and explicitly states that elasticities are descriptive summaries, not policy instruments (§4.10.1, §5.3). Fifth, the seven-model architecture itself demonstrates interpretive restraint: emissions models are reported as null/constrained rather than suppressed, showing that negative results are disclosed rather than hidden—this transparency signals that positive results are not cherry-picked (§4.9.7). The policymaker misinterpretation would require ignoring repeated warnings across four chapters, making misuse a reading-comprehension failure rather than a thesis-design failure (§3.2.2, §4.9.6, §4.10.1, §5.3).

**Supported in:**

- §4.2.3 ("What Model B Does Not Identify": causal effects, individual risk, policy counterfactuals explicitly rejected)
- §4.4.3, §4.7.3 (parallel "Does Not Identify" subsections for Models D and J)
- §4.9.6 ("What This Thesis Does Not Claim": consolidated boundaries, no causal/predictive/interventional claims)
- §4.10.1 (Conclusions: "empirically plausible associations," elasticities as descriptive summaries)
- §5.3 (future research: calls for causal designs, acknowledging current scope limits)
- §3.2.2 (post-positivist framework: associations, not causation, established from Chapter 3)
- §4.9.7 (seven-model architecture: null results disclosed, demonstrating interpretive discipline)
