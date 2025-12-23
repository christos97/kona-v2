"""
models.py – Regression Model Definitions
=========================================

Contains model specifications for the environmental-health analysis:
- Model B: PM2.5 → DALY (health burden)
- Model C: Sectoral Emissions → PM2.5 (multivariate panel)
- Model D: PM2.5 → YLL (mortality burden)
- Model G: Total Emissions → PM2.5 (aggregated panel FE)
- Model E-lite: Lagged Total Emissions → PM2.5 (panel FE, gated)
- Model J: Quadratic PM2.5 → Health (nonlinear OLS)
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Any
from datetime import datetime

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from scipy.special import logsumexp

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def _log_panel_save(message: str):
    """Log panel materialization to dedicated log file."""
    log_path = OUTPUT_DIR / "panel_materialization_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


# =============================================================================
# Utilities
# =============================================================================


def _ensure_series(y: pd.Series | pd.DataFrame) -> pd.Series:
    """Ensure y is a 1-D pandas Series."""
    if isinstance(y, pd.DataFrame):
        if y.shape[1] != 1:
            raise ValueError("Dependent variable must be 1-dimensional")
        return y.iloc[:, 0]
    if not isinstance(y, pd.Series):
        # last resort: convert array-like to Series (keeps index if possible)
        return pd.Series(y)
    return y


def _ensure_dataframe(X: pd.Series | pd.DataFrame) -> pd.DataFrame:
    """Ensure X is a DataFrame."""
    if isinstance(X, pd.Series):
        return X.to_frame()
    if not isinstance(X, pd.DataFrame):
        return pd.DataFrame(X)
    return X


def _as_1d_array(x: Any) -> np.ndarray:
    """
    Convert Series / DataFrame / array-like to a strict 1-D numpy array.
    Works for:
      - pd.Series
      - pd.DataFrame with 1 column
      - numpy arrays (n,) or (n,1)
    """
    if isinstance(x, pd.DataFrame):
        if x.shape[1] != 1:
            raise ValueError(f"Expected 1 column, got {x.shape[1]}")
        x = x.iloc[:, 0]
    if isinstance(x, pd.Series):
        return x.to_numpy()
    arr = np.asarray(x)
    arr = np.squeeze(arr)
    if arr.ndim != 1:
        raise ValueError(f"Expected 1-D array, got shape {arr.shape}")
    return arr


def _safe_getattr(obj: Any, name: str, default: Any = np.nan) -> Any:
    v = getattr(obj, name, default)
    try:
        # Some attrs are callables in certain libs/versions
        return v() if callable(v) else v
    except Exception:
        return default


# =============================================================================
# Output & Diagnostics
# =============================================================================


def save_model_outputs(
    model,
    name: str,
    results_list: list[dict],
    is_panel: bool = False,
) -> None:
    """
    Save regression outputs: summary, coefficients, diagnostics.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    OUTPUT_DIR.mkdir(exist_ok=True)

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    summary_text = str(model.summary) if is_panel else model.summary().as_text()
    (OUTPUT_DIR / f"{name}_summary.txt").write_text(summary_text, encoding="utf-8")

    # -------------------------------------------------------------------------
    # Coefficients table
    # -------------------------------------------------------------------------
    if is_panel:
        # linearmodels PanelResults: params is Series
        params = pd.Series(model.params)
        pvalues = pd.Series(model.pvalues, index=params.index)

        std_err = pd.Series(_safe_getattr(model, "std_errors", np.nan), index=params.index)
        tstats = pd.Series(_safe_getattr(model, "tstats", np.nan), index=params.index)

        coef = pd.DataFrame(
            {
                "Coefficient": params,
                "Std_Error": std_err,
                "t_Stat": tstats,
                "P_value": pvalues,
            }
        )
    else:
        ci = model.conf_int()
        coef = pd.DataFrame(
            {
                "Coefficient": model.params,
                "Std_Error": model.bse,
                "t_Stat": model.tvalues,
                "P_value": model.pvalues,
                "Lower_95%": ci[0],
                "Upper_95%": ci[1],
            }
        )

    coef.to_csv(OUTPUT_DIR / f"{name}_coefficients.csv", index=True)

    # -------------------------------------------------------------------------
    # Summary stats row
    # -------------------------------------------------------------------------
    if is_panel:
        stats = {
            "Model": name,
            "R2_within": float(_safe_getattr(model, "rsquared_within", np.nan)),
            "R2_between": float(_safe_getattr(model, "rsquared_between", np.nan)),
            "R2_overall": float(_safe_getattr(model, "rsquared_overall", np.nan)),
            "N": int(_safe_getattr(model, "nobs", np.nan)),
        }
        params = pd.Series(model.params)
        pvals = pd.Series(model.pvalues, index=params.index)
    else:
        stats = {
            "Model": name,
            "R2": float(_safe_getattr(model, "rsquared", np.nan)),
            "Adj_R2": float(_safe_getattr(model, "rsquared_adj", np.nan)),
            "N": int(_safe_getattr(model, "nobs", np.nan)),
        }
        params = pd.Series(model.params)
        pvals = pd.Series(model.pvalues, index=params.index)

    for p in params.index:
        if str(p) != "const":
            stats[f"Coef_{p}"] = float(params[p])
            stats[f"P_{p}"] = float(pvals[p])

    results_list.append(stats)

    # -------------------------------------------------------------------------
    # Diagnostics (always 1-D arrays for plotting)
    # -------------------------------------------------------------------------
    if is_panel:
        resid = _as_1d_array(model.resids)
        fitted = _as_1d_array(model.fitted_values)
    else:
        resid = _as_1d_array(model.resid)
        fitted = _as_1d_array(model.fittedvalues)

    # Residuals vs Fitted
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=fitted, y=resid, s=45, alpha=0.7)
    plt.axhline(0, color="red", linestyle="--", linewidth=1)
    plt.title(f"{name} – Residuals vs Fitted")
    plt.xlabel("Fitted Values")
    plt.ylabel("Residuals")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"{name}_residuals.png", dpi=200)
    plt.close()

    # Q-Q plot
    sm.qqplot(resid, line="45", fit=True)
    plt.title(f"{name} – Normal Q-Q Plot")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"{name}_qqplot.png", dpi=200)
    plt.close()


# =============================================================================
# Model Fitting
# =============================================================================


def fit_ols(
    y: pd.Series | pd.DataFrame,
    X: pd.DataFrame | pd.Series,
    name: str,
    results_list: list[dict],
    print_fn: Callable = print,
):
    """
    Fit standard OLS regression.
    """
    y = _ensure_series(y)
    X = _ensure_dataframe(X)

    Xc = sm.add_constant(X)
    model = sm.OLS(y, Xc, missing="drop").fit()

    print_fn(model.summary())
    save_model_outputs(model, name, results_list, is_panel=False)
    return model


def fit_panel_fe(
    y: pd.Series | pd.DataFrame,
    X: pd.DataFrame | pd.Series,
    name: str,
    results_list: list[dict],
    entity_effects: bool = True,
    time_effects: bool = True,
    print_fn: Callable = print,
):
    """
    Fit fixed-effects Panel OLS.
    """
    y = _ensure_series(y)
    X = _ensure_dataframe(X)

    # NOTE: Do NOT add constant in FE models (absorbed by FE)
    model = PanelOLS(
        y,
        X,
        entity_effects=entity_effects,
        time_effects=time_effects,
    )

    result = model.fit(
        cov_type="clustered",
        cluster_entity=True,
    )

    print_fn(result.summary)
    save_model_outputs(result, name, results_list, is_panel=True)
    return result


# =============================================================================
# NEW MODELS: J, G, E-lite
# =============================================================================


def fit_model_j_quadratic(
    df: pd.DataFrame,
    outcome: str,
    name: str,
    results_list: list[dict],
    print_fn: Callable = print,
):
    """
    Model J: Quadratic PM₂.₅ → Health (OLS, centered specification).

    Tests nonlinear dose-response relationship (convex vs. concave).

    Specification:
        ln(Health_i) = β₀ + β₁·z_i + β₂·z_i² + ε_i
        where z_i = ln(PM₂.₅_i) - mean(ln(PM₂.₅))

    Args:
        df: Cross-sectional data with ln_pm25 and outcome columns
        outcome: Column name for outcome variable ('ln_daly' or 'ln_yll')
        name: Model name for output files
        results_list: List to append summary statistics
        print_fn: Print function for logging

    Returns:
        tuple: (model, diagnostics_dict)

    Notes:
        - Centers ln(PM₂.₅) to reduce multicollinearity with squared term
        - Interprets β₂ sign: positive = accelerating harm, negative = diminishing returns
        - Turning point only meaningful if concave (β₂ < 0)
        - Turning point is DESCRIPTIVE only, no confidence interval computed
    """
    # CRITICAL: Do not mutate input dataframe
    df = df.copy()

    # Drop missing values first
    vars_needed = ["ln_pm25", outcome]
    df = df.dropna(subset=vars_needed)

    if len(df) < 10:
        print_fn(f"[WARN] Insufficient data for Model J: {len(df)} observations")
        return None, {"error": "insufficient_data", "n_obs": len(df)}

    # Center ln(PM₂.₅) to reduce collinearity with squared term
    pm_mean = df["ln_pm25"].mean()
    df["z"] = df["ln_pm25"] - pm_mean
    df["z_sq"] = df["z"] ** 2

    # Specification: outcome = β₀ + β₁·z + β₂·z² + ε
    X = df[["z", "z_sq"]]
    y = df[outcome]

    # Save estimation panel for Excel replication
    estimation_panel = df[["iso3", "country", outcome, "ln_pm25", "z", "z_sq"]].copy()
    estimation_panel = estimation_panel.reset_index(drop=True)
    panel_name = f"panel_model_j_{outcome.replace('ln_', '')}_estimation.csv"
    estimation_panel.to_csv(OUTPUT_DIR / panel_name, index=False)
    print_fn(f"💾 Saved {panel_name} (N={len(estimation_panel)})")
    _log_panel_save(f"Model J ({outcome}): {panel_name} (N={len(estimation_panel)}, countries={df['country'].nunique()})")

    Xc = sm.add_constant(X)
    model = sm.OLS(y, Xc, missing="drop").fit()

    # Extract coefficients
    beta1 = model.params["z"]
    beta2 = model.params["z_sq"]

    # Interpret curvature
    if beta2 > 0:
        curvature = "convex (accelerating harm)"
    elif beta2 < 0:
        curvature = "concave (diminishing marginal harm)"
    else:
        curvature = "linear (β₂ ≈ 0)"

    # Compute turning point if concave (β₂ < 0)
    # Turning point in centered space: z* = -β₁ / (2β₂)
    # Back-transform to PM₂.₅ units: PM* = exp(z* + mean(ln_pm25))
    turning_point_pm25 = None
    turning_point_note = None

    if beta2 < 0 and abs(beta2) > 1e-6:
        z_star = -beta1 / (2 * beta2)
        ln_pm_star = z_star + pm_mean
        turning_point_pm25 = np.exp(ln_pm_star)
        turning_point_note = "Implied turning point (descriptive, point estimate only)"

    diagnostics = {
        "n_obs": len(df),
        "pm25_mean_ln": pm_mean,
        "pm25_mean_raw": np.exp(pm_mean),
        "beta1_z": beta1,
        "beta2_z_sq": beta2,
        "curvature": curvature,
        "turning_point_pm25": turning_point_pm25,
        "turning_point_note": turning_point_note,
    }

    # Print summary
    print_fn(f"\n{'=' * 60}")
    print_fn(f"MODEL J: Quadratic PM₂.₅ → {outcome.replace('ln_', '').upper()}")
    print_fn(f"{'=' * 60}")
    print_fn(f"Specification: {outcome} = β₀ + β₁·z + β₂·z² + ε")
    print_fn(f"where z = ln(PM₂.₅) - {pm_mean:.4f}")
    print_fn(f"\nObservations: N = {len(df)}")
    print_fn(f"Centering mean (ln PM₂.₅): {pm_mean:.4f} ({np.exp(pm_mean):.2f} μg/m³)")
    print_fn(model.summary())
    print_fn(f"\nCurvature interpretation: {curvature}")
    if turning_point_pm25 is not None:
        print_fn(f"Implied turning point: {turning_point_pm25:.1f} μg/m³ (descriptive)")
        print_fn("NOTE: Turning point is a descriptive quantity derived from point estimates")
        print_fn("      and should not be interpreted as a precisely identified threshold.")

    # Save outputs using standard function
    save_model_outputs(model, name, results_list, is_panel=False)

    # Save additional diagnostics specific to Model J
    _save_model_j_diagnostics(name, diagnostics)

    return model, diagnostics


def _save_model_j_diagnostics(name: str, diagnostics: dict) -> None:
    """Save Model J-specific diagnostics (turning point, curvature)."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    diag_lines = [
        f"Model J Diagnostics: {name}",
        "=" * 40,
        "",
        f"Sample size: N = {diagnostics['n_obs']}",
        f"Centering mean (ln PM₂.₅): {diagnostics['pm25_mean_ln']:.4f}",
        f"Centering mean (PM₂.₅): {diagnostics['pm25_mean_raw']:.2f} μg/m³",
        "",
        f"Coefficient on z (linear): {diagnostics['beta1_z']:.6f}",
        f"Coefficient on z² (quadratic): {diagnostics['beta2_z_sq']:.6f}",
        "",
        f"Curvature: {diagnostics['curvature']}",
        "",
    ]

    if diagnostics["turning_point_pm25"] is not None:
        diag_lines.extend(
            [
                f"Implied turning point: {diagnostics['turning_point_pm25']:.1f} μg/m³",
                "",
                "NOTE: The implied turning point is reported as a descriptive quantity",
                "derived from point estimates and should not be interpreted as a",
                "precisely identified threshold. No confidence interval is computed.",
            ]
        )
    else:
        diag_lines.append("Turning point: Not applicable (curvature is not concave)")

    (OUTPUT_DIR / f"{name}_diagnostics.txt").write_text("\n".join(diag_lines), encoding="utf-8")


def fit_model_g_total_emissions(
    panel_df: pd.DataFrame,
    name: str,
    results_list: list[dict],
    print_fn: Callable = print,
):
    """
    Model G: Total Emissions → PM₂.₅ (Panel FE).

    Addresses multicollinearity in sectoral regressors by aggregating to total emissions.
    Uses exact-year WHO-UNFCCC panel (same sample as Model C).

    Specification:
        ln(PM₂.₅)_it = β·ln(TotalEmissions)_it + α_i + γ_t + ε_it
        where TotalEmissions = Energy + Industry + Transport

    Args:
        panel_df: Panel data with emissions columns (raw or log-transformed)
        name: Model name for output files
        results_list: List to append summary statistics
        print_fn: Print function for logging

    Returns:
        PanelOLS result object

    Notes:
        - Constructs total emissions from raw values when available (preferred)
        - Falls back to numerically stable logsumexp if only logs exist
        - Two-way fixed effects (entity + time)
        - Clustered SE at country level
        - NO constant added (absorbed by FE)
    """
    df = panel_df.copy()

    # -------------------------------------------------------------------------
    # Construct total emissions (prefer raw values for numerical stability)
    # -------------------------------------------------------------------------
    raw_cols = ["energy_emissions", "industry_emissions", "transport_emissions"]
    log_cols = ["ln_energy", "ln_industry", "ln_transport"]

    if all(col in df.columns for col in raw_cols):
        # Best: sum raw emissions, then log
        df["total_emissions"] = (
            df["energy_emissions"] + df["industry_emissions"] + df["transport_emissions"]
        )
        df["ln_total_emissions"] = np.log(df["total_emissions"])
        construction_method = "raw emissions summation"
    elif all(col in df.columns for col in log_cols):
        # Fallback: numerically stable logsumexp
        df["ln_total_emissions"] = logsumexp(df[log_cols].values, axis=1)
        construction_method = "logsumexp from log-transformed sectors"
    else:
        raise ValueError(
            "Cannot construct total emissions: missing sector columns. "
            f"Need {raw_cols} or {log_cols}"
        )

    # -------------------------------------------------------------------------
    # Prepare panel and drop missing
    # -------------------------------------------------------------------------
    df = df.dropna(subset=["ln_total_emissions", "ln_pm25"])

    if len(df) < 20:
        print_fn(f"[WARN] Insufficient data for Model G: {len(df)} observations")
        return None

    # Ensure MultiIndex for panel
    if not isinstance(df.index, pd.MultiIndex):
        if "iso3" in df.columns and "year" in df.columns:
            df = df.set_index(["iso3", "year"]).sort_index()
        else:
            raise ValueError("Panel must have iso3 and year columns or MultiIndex")

    n_countries = df.index.get_level_values("iso3").nunique()
    n_years = df.index.get_level_values("year").nunique()

    # -------------------------------------------------------------------------
    # Estimate: ln(PM₂.₅) ~ ln(TotalEmissions) + FE_i + FE_t
    # -------------------------------------------------------------------------
    y = df["ln_pm25"]
    X = df[["ln_total_emissions"]]

    # Save estimation panel for Excel replication
    estimation_panel = df.reset_index()[["iso3", "country", "year", "ln_pm25", "ln_total_emissions"]]
    estimation_panel.to_csv(OUTPUT_DIR / "panel_model_g_estimation.csv", index=False)
    print_fn(f"💾 Saved panel_model_g_estimation.csv (N={len(estimation_panel)}, countries={n_countries}, years={n_years})")
    _log_panel_save(f"Model G: panel_model_g_estimation.csv (N={len(estimation_panel)}, countries={n_countries}, years={n_years})")

    # NOTE: Do NOT add constant (absorbed by fixed effects)
    model = PanelOLS(
        y,
        X,
        entity_effects=True,
        time_effects=True,
    )

    result = model.fit(cov_type="clustered", cluster_entity=True)

    # -------------------------------------------------------------------------
    # Print summary
    # -------------------------------------------------------------------------
    print_fn(f"\n{'=' * 60}")
    print_fn("MODEL G: Total Emissions → PM₂.₅ (Panel FE)")
    print_fn(f"{'=' * 60}")
    print_fn("Specification: ln(PM₂.₅)_it = β·ln(TotalEmissions)_it + α_i + γ_t + ε_it")
    print_fn(f"Construction: {construction_method}")
    print_fn(f"\nSample: N = {len(df)} observations")
    print_fn(f"        {n_countries} countries, {n_years} years")
    print_fn(result.summary)

    # Save outputs
    save_model_outputs(result, name, results_list, is_panel=True)

    return result


def fit_model_e_lagged(
    panel_df: pd.DataFrame,
    name: str,
    results_list: list[dict],
    print_fn: Callable = print,
):
    """
    Model E-lite: Lagged Total Emissions → PM₂.₅ (Panel FE).

    Tests temporal precedence; reduces simultaneity concerns.
    ONLY called after gate check passes (see src/audit.py).

    Specification:
        ln(PM₂.₅)_it = β·ln(TotalEmissions)_{i,t-1} + α_i + γ_t + ε_it

    Args:
        panel_df: Panel data with total emissions column (or sector columns to construct it)
        name: Model name for output files
        results_list: List to append summary statistics
        print_fn: Print function for logging

    Returns:
        tuple: (PanelOLS result, sample_diagnostics_dict)

    Notes:
        - Lags total emissions by 1 year within each country
        - Two-way FE (entity + time)
        - Clustered SE at country level
        - NO constant added (absorbed by FE)
        - Caller is responsible for gate check before calling this function
    """
    df = panel_df.copy()

    # -------------------------------------------------------------------------
    # Ensure we have total emissions
    # -------------------------------------------------------------------------
    raw_cols = ["energy_emissions", "industry_emissions", "transport_emissions"]
    log_cols = ["ln_energy", "ln_industry", "ln_transport"]

    if "ln_total_emissions" not in df.columns:
        if all(col in df.columns for col in raw_cols):
            df["total_emissions"] = (
                df["energy_emissions"] + df["industry_emissions"] + df["transport_emissions"]
            )
            df["ln_total_emissions"] = np.log(df["total_emissions"])
        elif all(col in df.columns for col in log_cols):
            df["ln_total_emissions"] = logsumexp(df[log_cols].values, axis=1)
        else:
            raise ValueError("Cannot construct total emissions")

    # -------------------------------------------------------------------------
    # Reset index if needed for groupby operations
    # -------------------------------------------------------------------------
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index()

    # -------------------------------------------------------------------------
    # Create lag within each country
    # -------------------------------------------------------------------------
    n_before = len(df)
    countries_before = df["iso3"].nunique()

    df = df.sort_values(["iso3", "year"])
    df["ln_total_emissions_lag1"] = df.groupby("iso3")["ln_total_emissions"].shift(1)

    # Drop rows with missing lag
    df = df.dropna(subset=["ln_total_emissions_lag1", "ln_pm25"])

    n_after = len(df)
    countries_after = df["iso3"].nunique()

    sample_loss = (n_before - n_after) / n_before
    country_retention = countries_after / countries_before

    sample_diagnostics = {
        "n_before": n_before,
        "n_after": n_after,
        "sample_loss": sample_loss,
        "countries_before": countries_before,
        "countries_after": countries_after,
        "country_retention": country_retention,
    }

    if len(df) < 20:
        print_fn(f"[WARN] Insufficient data after lagging: {len(df)} observations")
        return None, sample_diagnostics

    # -------------------------------------------------------------------------
    # Set panel index and estimate
    # -------------------------------------------------------------------------
    df = df.set_index(["iso3", "year"]).sort_index()

    n_countries = df.index.get_level_values("iso3").nunique()
    n_years = df.index.get_level_values("year").nunique()

    # Save estimation panel for Excel replication
    estimation_panel = df.reset_index()[["iso3", "country", "year", "ln_pm25", "ln_total_emissions_lag1"]]
    estimation_panel.to_csv(OUTPUT_DIR / "panel_model_e_estimation.csv", index=False)
    print_fn(f"💾 Saved panel_model_e_estimation.csv (N={len(estimation_panel)}, countries={n_countries}, years={n_years})")
    _log_panel_save(f"Model E: panel_model_e_estimation.csv (N={len(estimation_panel)}, countries={n_countries}, years={n_years})")

    y = df["ln_pm25"]
    X = df[["ln_total_emissions_lag1"]]

    # NOTE: Do NOT add constant (absorbed by fixed effects)
    model = PanelOLS(
        y,
        X,
        entity_effects=True,
        time_effects=True,
    )

    result = model.fit(cov_type="clustered", cluster_entity=True)

    # -------------------------------------------------------------------------
    # Print summary
    # -------------------------------------------------------------------------
    print_fn(f"\n{'=' * 60}")
    print_fn("MODEL E-LITE: Lagged Total Emissions → PM₂.₅ (Panel FE)")
    print_fn(f"{'=' * 60}")
    print_fn("Specification: ln(PM₂.₅)_it = β·ln(TotalEmissions)_{i,t-1} + α_i + γ_t + ε_it")
    print_fn(f"\nSample retention:")
    print_fn(f"  Before lagging: {n_before} obs, {countries_before} countries")
    print_fn(f"  After lagging:  {n_after} obs, {countries_after} countries")
    print_fn(f"  Sample loss: {sample_loss:.1%}")
    print_fn(f"\nFinal sample: N = {len(df)} observations")
    print_fn(f"              {n_countries} countries, {n_years} years")
    print_fn(result.summary)

    # Save outputs
    save_model_outputs(result, name, results_list, is_panel=True)

    # Save sample retention info
    _save_model_e_sample_info(name, sample_diagnostics)

    return result, sample_diagnostics


def _save_model_e_sample_info(name: str, diagnostics: dict) -> None:
    """Save Model E sample retention information."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    lines = [
        f"Model E-lite Sample Retention: {name}",
        "=" * 40,
        "",
        "Lagging drops the first observation per country.",
        "",
        f"Before lagging: {diagnostics['n_before']} observations, {diagnostics['countries_before']} countries",
        f"After lagging:  {diagnostics['n_after']} observations, {diagnostics['countries_after']} countries",
        "",
        f"Sample loss: {diagnostics['sample_loss']:.1%}",
        f"Country retention: {diagnostics['country_retention']:.1%}",
    ]

    (OUTPUT_DIR / f"{name}_sample_retention.txt").write_text("\n".join(lines), encoding="utf-8")
