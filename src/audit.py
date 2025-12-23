"""
audit.py – Panel Balance Diagnostics for Thesis Reproducibility
================================================================

Reads actual pipeline outputs and generates audit-ready reports.
Implements gate criteria for Model E-lite (lagged specifications).

All diagnostics are saved to file for thesis transparency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def audit_panel_balance(
    print_fn: Callable = print,
    save_to_file: bool = True,
) -> dict:
    """
    Audit panel structure from actual pipeline outputs.

    Reports:
    - Observations per country (median, min, max)
    - Year coverage
    - Panel viability for FE/lagged models

    Returns:
        dict with panel diagnostics for each model
    """
    diagnostics = {}

    header = [
        "=" * 60,
        "PANEL VERIFICATION (from saved outputs)",
        "=" * 60,
    ]
    for line in header:
        print_fn(line)

    # -------------------------------------------------------------------------
    # Model C: Emissions → PM₂.₅ (exact-year panel)
    # -------------------------------------------------------------------------
    panel_c_path = OUTPUT_DIR / "panel_c_sectoral.csv"
    if panel_c_path.exists():
        panel_c = pd.read_csv(panel_c_path)
        obs_per_country = panel_c.groupby("iso3").size()

        diagnostics["model_c"] = {
            "n_obs": len(panel_c),
            "n_countries": panel_c["iso3"].nunique(),
            "n_years": panel_c["year"].nunique(),
            "year_min": int(panel_c["year"].min()),
            "year_max": int(panel_c["year"].max()),
            "median_obs_per_country": float(obs_per_country.median()),
            "min_obs_per_country": int(obs_per_country.min()),
            "max_obs_per_country": int(obs_per_country.max()),
        }

        print_fn("\n📊 Model C (Sectoral Emissions → PM₂.₅)")
        print_fn(f"   Total observations: {diagnostics['model_c']['n_obs']}")
        print_fn(f"   Countries: {diagnostics['model_c']['n_countries']}")
        print_fn(
            f"   Years: {diagnostics['model_c']['year_min']} - {diagnostics['model_c']['year_max']}"
        )
        print_fn(
            f"   Obs per country: median={diagnostics['model_c']['median_obs_per_country']:.0f}, "
            f"min={diagnostics['model_c']['min_obs_per_country']}, "
            f"max={diagnostics['model_c']['max_obs_per_country']}"
        )
    else:
        print_fn("\n⚠️  Model C panel not found (run pipeline first)")
        diagnostics["model_c"] = None

    # -------------------------------------------------------------------------
    # Model B: PM₂.₅ → DALY (cross-sectional)
    # -------------------------------------------------------------------------
    panel_b_path = OUTPUT_DIR / "panel_b_health.csv"
    if panel_b_path.exists():
        panel_b = pd.read_csv(panel_b_path)
        diagnostics["model_b"] = {
            "n_obs": len(panel_b),
            "n_countries": panel_b["country"].nunique() if "country" in panel_b.columns else "N/A",
            "structure": "Cross-sectional (nearest-year merge ±3)",
        }
        print_fn(f"\n📊 Model B (PM₂.₅ → DALY)")
        print_fn(f"   Observations: {diagnostics['model_b']['n_obs']}")
        print_fn(f"   Structure: {diagnostics['model_b']['structure']}")
    else:
        diagnostics["model_b"] = None

    # -------------------------------------------------------------------------
    # Model D: PM₂.₅ → YLL (cross-sectional)
    # -------------------------------------------------------------------------
    panel_d_path = OUTPUT_DIR / "panel_d_mortality.csv"
    if panel_d_path.exists():
        panel_d = pd.read_csv(panel_d_path)
        diagnostics["model_d"] = {
            "n_obs": len(panel_d),
            "n_countries": panel_d["country"].nunique() if "country" in panel_d.columns else "N/A",
            "structure": "Cross-sectional (nearest-year merge ±3)",
        }
        print_fn(f"\n📊 Model D (PM₂.₅ → YLL)")
        print_fn(f"   Observations: {diagnostics['model_d']['n_obs']}")
        print_fn(f"   Structure: {diagnostics['model_d']['structure']}")
    else:
        diagnostics["model_d"] = None

    print_fn("\n" + "=" * 60)

    return diagnostics


def check_model_e_gate(
    panel_df: pd.DataFrame,
    max_sample_loss: float = 0.30,
    min_country_retention: float = 0.67,
    print_fn: Callable = print,
    save_to_file: bool = True,
) -> tuple[bool, dict]:
    """
    Check gate criteria for Model E-lite (lagged specification).

    Gate criteria (all must pass):
    1. Median observations per country ≥ 3
    2. Sample loss after lagging ≤ max_sample_loss (default 30%)
    3. Countries retained ≥ min_country_retention of baseline (default 67%)

    Args:
        panel_df: Panel data with iso3, year, and emissions columns
        max_sample_loss: Maximum acceptable sample loss fraction
        min_country_retention: Minimum acceptable country retention fraction
        print_fn: Print function for logging
        save_to_file: Whether to save gate diagnostics to file

    Returns:
        tuple: (gate_passed: bool, diagnostics: dict)
    """
    df = panel_df.copy()

    # Ensure we have the right structure
    if "iso3" not in df.columns or "year" not in df.columns:
        # Try to extract from index
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()

    # -------------------------------------------------------------------------
    # Baseline panel statistics
    # -------------------------------------------------------------------------
    n_baseline = len(df)
    countries_baseline = df["iso3"].nunique()
    obs_per_country = df.groupby("iso3").size()
    median_obs_baseline = float(obs_per_country.median())

    # -------------------------------------------------------------------------
    # Simulate lagging (drop first observation per country)
    # -------------------------------------------------------------------------
    df = df.sort_values(["iso3", "year"])
    df["_lag_valid"] = df.groupby("iso3").cumcount() > 0  # First obs per country = False

    df_after_lag = df[df["_lag_valid"]].copy()
    n_after_lag = len(df_after_lag)
    countries_after_lag = df_after_lag["iso3"].nunique()
    obs_per_country_after = df_after_lag.groupby("iso3").size()
    median_obs_after = (
        float(obs_per_country_after.median()) if len(obs_per_country_after) > 0 else 0
    )

    # -------------------------------------------------------------------------
    # Compute gate metrics
    # -------------------------------------------------------------------------
    sample_loss = (n_baseline - n_after_lag) / n_baseline if n_baseline > 0 else 1.0
    country_retention = countries_after_lag / countries_baseline if countries_baseline > 0 else 0.0

    # -------------------------------------------------------------------------
    # Evaluate gate criteria
    # -------------------------------------------------------------------------
    gate_1_pass = median_obs_baseline >= 3
    gate_2_pass = sample_loss <= max_sample_loss
    gate_3_pass = country_retention >= min_country_retention

    gate_passed = gate_1_pass and gate_2_pass and gate_3_pass

    diagnostics = {
        "baseline": {
            "n_obs": n_baseline,
            "n_countries": countries_baseline,
            "median_obs_per_country": median_obs_baseline,
        },
        "after_lagging": {
            "n_obs": n_after_lag,
            "n_countries": countries_after_lag,
            "median_obs_per_country": median_obs_after,
            "sample_loss": sample_loss,
            "country_retention": country_retention,
        },
        "gate_criteria": {
            "median_obs_ge_3": {
                "passed": gate_1_pass,
                "value": median_obs_baseline,
                "threshold": 3,
            },
            "sample_loss_le_30pct": {
                "passed": gate_2_pass,
                "value": sample_loss,
                "threshold": max_sample_loss,
            },
            "country_retention_ge_67pct": {
                "passed": gate_3_pass,
                "value": country_retention,
                "threshold": min_country_retention,
            },
        },
        "decision": "ESTIMATED" if gate_passed else "SKIPPED",
        "reason": None
        if gate_passed
        else _get_failure_reason(gate_1_pass, gate_2_pass, gate_3_pass),
    }

    # -------------------------------------------------------------------------
    # Log results
    # -------------------------------------------------------------------------
    print_fn("\n" + "=" * 60)
    print_fn("MODEL E-LITE GATE CHECK")
    print_fn("=" * 60)
    print_fn(f"\nBaseline panel:")
    print_fn(f"  Observations: N = {n_baseline}")
    print_fn(f"  Countries: {countries_baseline}")
    print_fn(f"  Median obs per country: {median_obs_baseline:.0f}")
    print_fn(f"\nAfter lagging (t-1):")
    print_fn(f"  Observations retained: {n_after_lag}")
    print_fn(f"  Countries retained: {countries_after_lag}")
    print_fn(f"  Median obs per country: {median_obs_after:.0f}")
    print_fn(f"  Sample loss: {sample_loss:.1%}")
    print_fn(f"\nGate criteria:")
    print_fn(f"  Median obs ≥ 3: {'PASS' if gate_1_pass else 'FAIL'}")
    print_fn(f"  Sample loss ≤ {max_sample_loss:.0%}: {'PASS' if gate_2_pass else 'FAIL'}")
    print_fn(
        f"  Countries retained ≥ {min_country_retention:.0%}: {'PASS' if gate_3_pass else 'FAIL'}"
    )
    print_fn(f"\nDecision:")
    if gate_passed:
        print_fn(f"→ Model E-lite ESTIMATED")
    else:
        print_fn(f"→ Model E-lite SKIPPED ({diagnostics['reason']})")
    print_fn("=" * 60)

    # -------------------------------------------------------------------------
    # Save to file (ALWAYS, even if skipped)
    # -------------------------------------------------------------------------
    if save_to_file:
        _save_gate_diagnostics(diagnostics, print_fn)

    return gate_passed, diagnostics


def _get_failure_reason(gate_1: bool, gate_2: bool, gate_3: bool) -> str:
    """Generate human-readable failure reason."""
    reasons = []
    if not gate_1:
        reasons.append("median observations per country < 3")
    if not gate_2:
        reasons.append("sample loss exceeds threshold")
    if not gate_3:
        reasons.append("too many countries dropped")
    return "; ".join(reasons)


def _save_gate_diagnostics(diagnostics: dict, print_fn: Callable = print) -> None:
    """
    Save gate diagnostics to file for thesis reproducibility.

    Always saves, regardless of whether model was estimated or skipped.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    gate_file = OUTPUT_DIR / "ModelE_gate_check.txt"

    lines = [
        "Model E-lite Gate Diagnostics",
        "=" * 40,
        "",
        "Source panel: output/panel_c_sectoral.csv",
        "",
        "Baseline panel:",
        f"- Observations: N = {diagnostics['baseline']['n_obs']}",
        f"- Countries: {diagnostics['baseline']['n_countries']}",
        f"- Median obs per country: {diagnostics['baseline']['median_obs_per_country']:.0f}",
        "",
        "After lagging (t-1):",
        f"- Observations retained: {diagnostics['after_lagging']['n_obs']}",
        f"- Countries retained: {diagnostics['after_lagging']['n_countries']}",
        f"- Median obs per country: {diagnostics['after_lagging']['median_obs_per_country']:.0f}",
        f"- Sample loss: {diagnostics['after_lagging']['sample_loss']:.1%}",
        "",
        "Gate criteria:",
        f"- Median obs ≥ 3: {'PASS' if diagnostics['gate_criteria']['median_obs_ge_3']['passed'] else 'FAIL'}",
        f"- Sample loss ≤ 30%: {'PASS' if diagnostics['gate_criteria']['sample_loss_le_30pct']['passed'] else 'FAIL'}",
        f"- Countries retained ≥ 2/3 baseline: {'PASS' if diagnostics['gate_criteria']['country_retention_ge_67pct']['passed'] else 'FAIL'}",
        "",
        "Decision:",
    ]

    if diagnostics["decision"] == "ESTIMATED":
        lines.append("→ Model E-lite ESTIMATED")
    else:
        lines.append(f"→ Model E-lite SKIPPED ({diagnostics['reason']})")

    gate_file.write_text("\n".join(lines), encoding="utf-8")
    print_fn(f"💾 Saved gate diagnostics to {gate_file}")


if __name__ == "__main__":
    audit_panel_balance()
