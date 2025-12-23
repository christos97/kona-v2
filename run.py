"""
run.py – Extended Environmental–Health Regression Pipeline (Final Panel-Friendly + Nearest-Year Merge)
======================================================================================================

Performs integrated regressions across environmental and health datasets (EEA, WHO, UNFCCC, GBD):

  A. EEA Emissions → PM2.5
  B. PM2.5 → DALY (EEA) — nearest-year merge ±3 years
  C. UNFCCC Emissions → PM2.5
  D. PM2.5 → YLL (GBD)
  E. Two-Way Fixed Effects (country + year)
  F. Greece-specific subset

All outputs (CSV summaries, residual plots, diagnostics) saved in /output.
"""

from __future__ import annotations
import sys, re, numpy as np, pandas as pd
from pathlib import Path
import statsmodels.api as sm
import matplotlib.pyplot as plt, seaborn as sns, pycountry
from datetime import datetime
from linearmodels.panel import PanelOLS

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
OUT, DATA = Path("output"), Path("data")
OUT.mkdir(exist_ok=True)
log_path = OUT / f"run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_file = open(log_path, "w", encoding="utf-8")
sys_stdout = sys.stdout
sys.stdout = log_file
print(f"🚀 Starting Extended Environmental–Health Pipeline (log: {log_path})")


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def normalize_country(name: str) -> str | float:
    """Return ISO3 code if possible, else clean string."""
    if not isinstance(name, str) or not name.strip():
        return np.nan
    try:
        return pycountry.countries.lookup(name).alpha_3
    except Exception:
        return name.strip()


def leading_number(x):
    """Extract first numeric token from mixed strings."""
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.number)):
        return float(x)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(x).replace(",", ""))
    return float(m.group(0)) if m else np.nan


def save_summary(model, name, results_dict):
    """Save regression summary, coefficients, residuals plots."""
    with open(OUT / f"{name}_summary.txt", "w", encoding="utf-8") as f:
        f.write(model.summary().as_text())

    coef = pd.DataFrame(
        {
            "Coefficient": model.params,
            "Std_Error": model.bse,
            "t_Stat": model.tvalues,
            "P_value": model.pvalues,
            "Lower_95%": model.conf_int()[0],
            "Upper_95%": model.conf_int()[1],
        }
    )
    coef.to_csv(OUT / f"{name}_coefficients.csv")

    stats = {
        "Model": name,
        "R2": float(getattr(model, "rsquared", np.nan)),
        "Adj_R2": float(getattr(model, "rsquared_adj", np.nan))
        if hasattr(model, "rsquared_adj")
        else np.nan,
        "N": int(getattr(model, "nobs", np.nan)),
    }
    if "const" in model.params:
        stats["Intercept"] = model.params["const"]
    for p in model.params.index:
        if p != "const":
            stats[f"Coef_{p}"] = model.params[p]
            stats[f"P_{p}"] = model.pvalues[p]
    results_dict.append(stats)

    # residual diagnostics
    resid, fitted = model.resid, model.fittedvalues
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=fitted, y=resid, s=45, edgecolor="white")
    plt.axhline(0, color="red", ls="--", lw=1.2)
    plt.title(f"{name} – Residuals vs Fitted")
    plt.xlabel("Fitted Values")
    plt.ylabel("Residuals")
    plt.tight_layout()
    plt.savefig(OUT / f"{name}_residuals.png", dpi=200)
    plt.close()

    sm.qqplot(resid, line="45", fit=True)
    plt.title(f"{name} – Normal Probability Plot")
    plt.tight_layout()
    plt.savefig(OUT / f"{name}_qqplot.png", dpi=200)
    plt.close()


def fit_ols(y, X, name, results_dict):
    Xc = sm.add_constant(X)
    model = sm.OLS(y, Xc, missing="drop").fit()
    print(model.summary())
    save_summary(model, name, results_dict)
    return model


def save_intermediate(df, name):
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"💾 Saved {name} → {len(df)} rows")


def merge_nearest_years(df_left, df_right, on_key, left_year, right_year, tolerance=3):
    """Nearest-year join with ±tolerance window."""
    merged = []
    for _, row in df_left.iterrows():
        subset = df_right[df_right[on_key] == row[on_key]]
        if subset.empty:
            continue
        subset = subset.assign(diff=(subset[right_year] - row[left_year]).abs())
        subset = subset[subset["diff"] <= tolerance]
        if len(subset):
            merged.append({**row.to_dict(), **subset.sort_values("diff").iloc[0].to_dict()})
    return pd.DataFrame(merged)


# -----------------------------------------------------------------------------
# Load and prepare datasets
# -----------------------------------------------------------------------------
print("\n📊 Loading input datasets...")

# WHO Air Quality
who = pd.read_csv(DATA / "who_air_quality.csv").rename(
    columns={"WHO Country Name": "country", "Measurement Year": "year", "PM2.5 (μg/m3)": "pm25"}
)
who_cty = who.groupby(["country", "year"], as_index=False)["pm25"].mean()
who_cty["iso3"] = who_cty["country"].apply(normalize_country)

# EEA Emissions
eea = pd.read_csv(DATA / "eea_emissions.csv").rename(columns={"Party": "country"})
value_cols = [c for c in eea.columns if str(c).isdigit()]
eea_long = eea.melt(
    id_vars=["country"], value_vars=value_cols, var_name="year", value_name="total_emissions_kt"
)
eea_long["year"] = pd.to_numeric(eea_long["year"], errors="coerce")
eea_long["total_emissions_kt"] = pd.to_numeric(
    eea_long["total_emissions_kt"].astype(str).str.replace(",", ""), errors="coerce"
)
eea_long["iso3"] = eea_long["country"].apply(normalize_country)

# EEA Burden (DALY)
burden = pd.read_csv(DATA / "eea_burden_disease.csv")
burden = burden[
    (burden["Degree Of Urbanisation"] == "All Areas (incl.unclassified)")
    & (burden["Air Pollutant"] == "PM2.5")
    & (burden["Health Indicator"] == "Disability-Adjusted Life Years (DALY)")
]
burden_cty = (
    burden.groupby(["Country Or Territory", "Year"], as_index=False)["Value"]
    .sum()
    .rename(columns={"Country Or Territory": "country", "Year": "year", "Value": "daly"})
)
burden_cty["iso3"] = burden_cty["country"].apply(normalize_country)

# UNFCCC totals
unfccc = pd.read_csv(DATA / "unfccc_totals.csv")
unfccc_cty = (
    unfccc.groupby(["Country", "Year"], as_index=False)["emissions"]
    .sum()
    .rename(
        columns={"Country": "country", "Year": "year", "emissions": "total_emissions_kt_unfccc"}
    )
)
unfccc_cty["iso3"] = unfccc_cty["country"].apply(normalize_country)

# GBD YLL
gbd = pd.read_csv(DATA / "health_gbd2021_yll_bothsex_asmr.csv").rename(
    columns={"location_name": "country"}
)
year_cols = [c for c in gbd.columns if re.match(r"^\\d{4}", c)]
gbd_long = gbd.melt(
    id_vars=["country"], value_vars=year_cols, var_name="year_raw", value_name="yll_asmr"
)
gbd_long["year"] = gbd_long["year_raw"].str.extract(r"(\\d{4})").astype(float)
gbd_long["yll_asmr"] = gbd_long["yll_asmr"].apply(leading_number)
gbd_long["iso3"] = gbd_long["country"].apply(normalize_country)

results: list[dict] = []

# -----------------------------------------------------------------------------
# Model A: EEA Emissions → PM2.5
# -----------------------------------------------------------------------------
print("\n===================================================")
print("MODEL A: EEA Emissions → PM2.5")
print("===================================================")
panel_a = who_cty.merge(eea_long, on=["iso3", "country", "year"], how="inner")
panel_a["ln_pm25"] = np.log(panel_a["pm25"])
panel_a["ln_total_emissions_kt"] = np.log(panel_a["total_emissions_kt"])
panel_a = panel_a.replace([np.inf, -np.inf], np.nan).dropna(
    subset=["ln_pm25", "ln_total_emissions_kt"]
)
save_intermediate(panel_a, "panel_a")
if len(panel_a) >= 10:
    fit_ols(
        panel_a["ln_pm25"], panel_a[["ln_total_emissions_kt"]], "ModelA_Emissions_PM25", results
    )

# -----------------------------------------------------------------------------
# Model B: PM2.5 → DALY (nearest-year merge ±3)
# -----------------------------------------------------------------------------
print("\n===================================================")
print("MODEL B: PM2.5 → DALY (EEA) – nearest-year ±3")
print("===================================================")
health_b = merge_nearest_years(who_cty, burden_cty, "iso3", "year", "year", tolerance=3)
if not health_b.empty:
    health_b["ln_pm25"] = np.log(health_b["pm25"])
    health_b["ln_daly"] = np.log(health_b["daly"])
    save_intermediate(health_b, "health_b")
    fit_ols(health_b["ln_daly"], health_b[["ln_pm25"]], "ModelB_PM25_DALY", results)
else:
    print("[WARN] No overlapping country-years even with ±3-year tolerance.")

# -----------------------------------------------------------------------------
# Model C: UNFCCC Emissions → PM2.5
# -----------------------------------------------------------------------------
print("\n===================================================")
print("MODEL C: UNFCCC Emissions → PM2.5")
print("===================================================")
panel_c = who_cty.merge(unfccc_cty, on=["iso3", "country", "year"], how="inner")
panel_c["ln_pm25"] = np.log(panel_c["pm25"])
panel_c["ln_total_unfccc"] = np.log(panel_c["total_emissions_kt_unfccc"])
panel_c = panel_c.replace([np.inf, -np.inf], np.nan).dropna(subset=["ln_pm25", "ln_total_unfccc"])
save_intermediate(panel_c, "panel_c")
if len(panel_c) >= 10:
    fit_ols(panel_c["ln_pm25"], panel_c[["ln_total_unfccc"]], "ModelC_UNFCCC_PM25", results)

# -----------------------------------------------------------------------------
# Model D: PM2.5 → YLL (GBD)
# -----------------------------------------------------------------------------
print("\n===================================================")
print("MODEL D: PM2.5 → YLL (GBD)")
print("===================================================")
health_d = who_cty.merge(gbd_long, on=["iso3", "country", "year"], how="inner")
health_d["ln_pm25"] = np.log(health_d["pm25"])
health_d["ln_yll_asmr"] = np.log(health_d["yll_asmr"])
health_d = health_d.replace([np.inf, -np.inf], np.nan).dropna(subset=["ln_pm25", "ln_yll_asmr"])
save_intermediate(health_d, "health_d_yll_merge")
if len(health_d) >= 10:
    fit_ols(health_d["ln_yll_asmr"], health_d[["ln_pm25"]], "ModelD_PM25_YLL", results)

# -----------------------------------------------------------------------------
# Model E: Two-Way Fixed Effects
# -----------------------------------------------------------------------------
print("\n===================================================")
print("MODEL E: Two-Way Fixed Effects – UNFCCC → PM2.5")
print("===================================================")
if len(panel_c) > 30:
    df_panel = panel_c.set_index(["iso3", "year"]).sort_index()
    save_intermediate(df_panel.reset_index(), "panel_e_fe")
    model_e = PanelOLS(
        df_panel["ln_pm25"],
        sm.add_constant(df_panel[["ln_total_unfccc"]]),
        entity_effects=True,
        time_effects=True,
    )
    res_e = model_e.fit(cov_type="clustered", cluster_entity=True)
    with open(OUT / "ModelE_TwoWayFE_summary.txt", "w", encoding="utf-8") as f:
        f.write(str(res_e.summary))
    print(res_e.summary)

# -----------------------------------------------------------------------------
# Model F: Greece subset
# -----------------------------------------------------------------------------
print("\n===================================================")
print("MODEL F: Greece subset (UNFCCC → PM2.5)")
print("===================================================")
greece = panel_c[panel_c["country"].str.contains("Greece", case=False, na=False)]
save_intermediate(greece, "panel_f_greece")
if len(greece) >= 3:
    fit_ols(greece["ln_pm25"], greece[["ln_total_unfccc"]], "ModelF_Greece_UNFCCC_PM25", results)

# -----------------------------------------------------------------------------
# Combined summary
# -----------------------------------------------------------------------------
pd.DataFrame(results).to_csv(OUT / "summary_all_models.csv", index=False)
print("\n✅ Analysis complete.")
sys.stdout = sys_stdout
log_file.close()
print(f"✅ Pipeline finished. Log saved at: {log_path}")
