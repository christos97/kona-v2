"""
run.py – Extended Environmental–Health Regression Pipeline (Final Stable)
=====================================================================
Includes:
  A. EEA Emissions → PM2.5
  B. PM2.5 → DALY (EEA)
  C. UNFCCC Emissions → PM2.5
  D. PM2.5 → YLL (GBD)
  E. Two-Way Fixed Effects (country + year)
  F. Greece-specific regression
  G. Combined summary CSV + log file

All results saved in /output.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry
from datetime import datetime
from linearmodels.panel import PanelOLS

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
OUT = Path("output")
OUT.mkdir(exist_ok=True)
log_path = OUT / f"run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_file = open(log_path, "w", encoding="utf-8")
sys.stdout = log_file
print("🚀 Running Extended Environmental–Health Analysis Pipeline...")
print(f"Log file: {log_path.resolve()}")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def normalize_country(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        return np.nan
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return name.strip()


def leading_number(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).replace(",", "").strip()
    for token in s.replace("(", " ").split():
        try:
            return float(token)
        except ValueError:
            continue
    return np.nan


def save_summary(model, name: str, results_dict: list):
    summary_txt = model.summary().as_text()
    with open(OUT / f"{name}_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary_txt)

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

    # Residual plots
    resid = model.resid
    fitted = model.fittedvalues
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=fitted, y=resid, s=50, edgecolor="white")
    plt.axhline(0, color="red", ls="--", lw=1.5)
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


def fit_ols(y, X, name: str, results_dict):
    Xc = sm.add_constant(X)
    model = sm.OLS(y, Xc, missing="drop").fit()
    print(model.summary())
    save_summary(model, name, results_dict)
    return model


# ---------------------------------------------------------------------
# Load datasets
# ---------------------------------------------------------------------
DATA = Path("data")

# WHO Air Quality
who = pd.read_csv(DATA / "who_air_quality.csv")
who = who.rename(
    columns={"WHO Country Name": "country", "Measurement Year": "year", "PM2.5 (μg/m3)": "pm25"}
)
who["year"] = pd.to_numeric(who["year"], errors="coerce")
who["pm25"] = pd.to_numeric(who["pm25"], errors="coerce")
who_cty = who.groupby(["country", "year"], as_index=False)["pm25"].mean()
who_cty["iso3"] = who_cty["country"].apply(normalize_country)

# EEA Emissions
eea = pd.read_csv(DATA / "eea_emissions.csv")
eea = eea.rename(columns={"Party": "country"})
value_cols = [c for c in eea.columns if str(c).isdigit()]
eea_long = eea.melt(
    id_vars=["country"], value_vars=value_cols, var_name="year", value_name="total_emissions_kt"
)
eea_long["year"] = eea_long["year"].astype(int)
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
burden_agg = burden.groupby(["Country Or Territory", "Year"], as_index=False)["Value"].sum()
burden_agg = burden_agg.rename(
    columns={"Country Or Territory": "country", "Year": "year", "Value": "daly"}
)
burden_agg["year"] = pd.to_numeric(burden_agg["year"], errors="coerce")
burden_agg["daly"] = pd.to_numeric(burden_agg["daly"], errors="coerce")
burden_agg["iso3"] = burden_agg["country"].apply(normalize_country)

# UNFCCC
unfccc = pd.read_csv(DATA / "unfccc_totals.csv")
unfccc["emissions"] = pd.to_numeric(unfccc["emissions"], errors="coerce")
unfccc["Year"] = pd.to_numeric(unfccc["Year"], errors="coerce")
unfccc_cty = unfccc.groupby(["Country", "Year"], as_index=False)["emissions"].sum()
unfccc_cty = unfccc_cty.rename(
    columns={"Country": "country", "Year": "year", "emissions": "total_emissions_kt_unfccc"}
)
unfccc_cty["iso3"] = unfccc_cty["country"].apply(normalize_country)

# GBD YLL
gbd = pd.read_csv(DATA / "health_gbd2021_yll_bothsex_asmr.csv")
gbd = gbd.rename(columns={"location_name": "country"})
gbd["ASMR_2021"] = gbd["2021 (Age-Standardised Rate - YLLs)"].apply(leading_number)
gbd["ASMR_2019"] = gbd["2019 (Age-Standardised Rate - YLLs)"].apply(leading_number)
gbd_latest = (
    gbd.assign(asmr_latest=lambda d: d["ASMR_2021"].fillna(d["ASMR_2019"]))
    .groupby("country", as_index=False)["asmr_latest"]
    .mean()
)
gbd_latest["iso3"] = gbd_latest["country"].apply(normalize_country)

results = []

# ---------------------------------------------------------------------
# Models A–D
# ---------------------------------------------------------------------
print("\n===================================================")
print("MODEL A: EEA Emissions → PM2.5")
print("===================================================")
panel_a = who_cty.merge(eea_long, on=["iso3", "country", "year"], how="inner")
panel_a["ln_pm25"] = np.log(panel_a["pm25"])
panel_a["ln_total_emissions_kt"] = np.log(panel_a["total_emissions_kt"])
panel_a = panel_a.replace([np.inf, -np.inf], np.nan).dropna(
    subset=["ln_pm25", "ln_total_emissions_kt"]
)
fit_ols(panel_a["ln_pm25"], panel_a[["ln_total_emissions_kt"]], "ModelA_Emissions_PM25", results)

print("\n===================================================")
print("MODEL B: PM2.5 → DALY (EEA)")
print("===================================================")
who_latest = who_cty.sort_values("year").groupby(["iso3", "country"]).tail(1)
burden_latest = burden_agg.sort_values("year").groupby(["iso3", "country"]).tail(1)
health_b = who_latest.merge(burden_latest, on=["iso3", "country"])
health_b["ln_pm25"] = np.log(health_b["pm25"])
health_b["ln_daly"] = np.log(health_b["daly"])
health_b = health_b.replace([np.inf, -np.inf], np.nan).dropna(subset=["ln_pm25", "ln_daly"])
if len(health_b) >= 4:
    fit_ols(health_b["ln_daly"], health_b[["ln_pm25"]], "ModelB_PM25_DALY", results)

print("\n===================================================")
print("MODEL C: UNFCCC Emissions → PM2.5")
print("===================================================")
panel_c = who_cty.merge(unfccc_cty, on=["iso3", "country", "year"], how="inner")
panel_c["ln_pm25"] = np.log(panel_c["pm25"])
panel_c["ln_total_unfccc"] = np.log(panel_c["total_emissions_kt_unfccc"])
panel_c = panel_c.replace([np.inf, -np.inf], np.nan).dropna(subset=["ln_pm25", "ln_total_unfccc"])
if len(panel_c) >= 10:
    fit_ols(panel_c["ln_pm25"], panel_c[["ln_total_unfccc"]], "ModelC_UNFCCC_PM25", results)

print("\n===================================================")
print("MODEL D: PM2.5 → YLL (GBD)")
print("===================================================")
who_latest_d = who_latest[["iso3", "country", "pm25"]].rename(columns={"pm25": "pm25_latest"})
yll_merge = who_latest_d.merge(gbd_latest[["iso3", "asmr_latest"]], on="iso3", how="inner")
yll_merge["ln_pm25"] = np.log(yll_merge["pm25_latest"])
yll_merge["ln_yll_asmr"] = np.log(yll_merge["asmr_latest"])
yll_merge = yll_merge.replace([np.inf, -np.inf], np.nan).dropna(subset=["ln_pm25", "ln_yll_asmr"])
if len(yll_merge) >= 4:
    fit_ols(yll_merge["ln_yll_asmr"], yll_merge[["ln_pm25"]], "ModelD_PM25_YLL", results)

# ---------------------------------------------------------------------
# Model E: Two-Way Fixed Effects
# ---------------------------------------------------------------------
print("\n===================================================")
print("MODEL E: Two-Way Fixed Effects – UNFCCC → PM2.5")
print("===================================================")
if len(panel_c) > 30:
    df_panel = panel_c.set_index(["iso3", "year"])
    model_e = PanelOLS(
        df_panel["ln_pm25"],
        sm.add_constant(df_panel["ln_total_unfccc"]),
        entity_effects=True,
        time_effects=True,
    )
    res_e = model_e.fit(cov_type="clustered", cluster_entity=True)
    print(res_e.summary)
    with open(OUT / "ModelE_TwoWayFE_summary.txt", "w", encoding="utf-8") as f:
        f.write(str(res_e.summary))

    # Handle rsquared (float or dict)
    if isinstance(res_e.rsquared, dict):
        r2_within = res_e.rsquared.get("within", np.nan)
        r2_overall = res_e.rsquared.get("overall", np.nan)
    else:
        r2_within = float(res_e.rsquared)
        r2_overall = np.nan

    # ✅ Flatten all coefficient arrays safely
    coef_df = pd.DataFrame(
        {
            "Coefficient": np.ravel(res_e.params),
            "Std_Error": np.ravel(res_e.std_errors),
            "t_Stat": np.ravel(res_e.tstats),
            "P_value": np.ravel(res_e.pvalues),
            "Lower_95%": np.ravel(res_e.conf_int().iloc[:, 0]),
            "Upper_95%": np.ravel(res_e.conf_int().iloc[:, 1]),
        },
        index=res_e.params.index,
    )
    coef_df.to_csv(OUT / "ModelE_TwoWayFE_coefficients.csv")

    # ✅ Residuals & fitted plots
    resid = res_e.resids.squeeze()
    fitted = res_e.fitted_values.squeeze()
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=fitted, y=resid, s=50, edgecolor="white")
    plt.axhline(0, color="red", ls="--", lw=1.5)
    plt.title("ModelE_TwoWayFE – Residuals vs Fitted")
    plt.xlabel("Fitted Values")
    plt.ylabel("Residuals")
    plt.tight_layout()
    plt.savefig(OUT / "ModelE_TwoWayFE_residuals.png", dpi=200)
    plt.close()

    sm.qqplot(resid, line="45", fit=True)
    plt.title("ModelE_TwoWayFE – Normal Probability Plot")
    plt.tight_layout()
    plt.savefig(OUT / "ModelE_TwoWayFE_qqplot.png", dpi=200)
    plt.close()

    # ✅ Add summary row
    results.append(
        {
            "Model": "ModelE_TwoWayFE",
            "R2_within": r2_within,
            "R2_overall": r2_overall,
            "N": int(res_e.nobs),
            "Coef_ln_total_unfccc": float(res_e.params.squeeze().iloc[0])
            if "ln_total_unfccc" in res_e.params.index
            else np.nan,
            "P_ln_total_unfccc": float(res_e.pvalues.squeeze().iloc[0])
            if "ln_total_unfccc" in res_e.pvalues.index
            else np.nan,
        }
    )

# ---------------------------------------------------------------------
# Model F: Greece Subset
# ---------------------------------------------------------------------
print("\n===================================================")
print("MODEL F: Greece Subset (UNFCCC Emissions → PM2.5)")
print("===================================================")
greece = panel_c[panel_c["country"].str.contains("Greece", case=False, na=False)]
if len(greece) >= 3:
    fit_ols(greece["ln_pm25"], greece[["ln_total_unfccc"]], "ModelF_Greece_UNFCCC_PM25", results)

# ---------------------------------------------------------------------
# Combined Summary
# ---------------------------------------------------------------------
pd.DataFrame(results).to_csv(OUT / "summary_all_models.csv", index=False)
print("\n✅ Analysis complete.")
print(f"Saved outputs and log → {OUT.resolve()}")

sys.stdout = sys.__stdout__
log_file.close()
print(f"✅ Extended pipeline complete. Log saved at: {log_path.resolve()}")
