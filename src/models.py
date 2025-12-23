"""
models.py – Regression Model Definitions
=========================================

Contains model specifications for the environmental-health analysis:
- Model B: PM2.5 → DALY (health burden)
- Model C: Sectoral Emissions → PM2.5 (multivariate panel)
- Model D: PM2.5 → YLL (mortality burden)
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

OUTPUT_DIR = Path(__file__).parent.parent / "output"


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
