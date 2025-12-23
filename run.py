"""
run.py – Streamlined Environmental-Health Regression Pipeline
=============================================================

Focused analysis with core models:
  B. PM2.5 → DALY (EEA health burden, nearest-year merge ±3)
  C. Sectoral Emissions → PM2.5 (multivariate panel with fixed effects)
  D. PM2.5 → YLL (GBD mortality burden, nearest-year merge ±3)
  G. Total Emissions → PM2.5 (aggregated panel FE)
  E. Lagged Total Emissions → PM2.5 (panel FE, GATED)
  J. Quadratic PM2.5 → Health (nonlinear OLS, DALY and YLL)

Usage:
  poetry run python run.py [--model B|C|D|G|E|J|all]  (default: run all)

Examples:
  poetry run python run.py              # Run all models
  poetry run python run.py --model B    # Run only Model B
  poetry run python run.py --model J    # Run only Model J (quadratic)
  poetry run python run.py --model G    # Run only Model G (total emissions)
"""

from __future__ import annotations
import sys
import argparse
import re
import numpy as np
import pandas as pd
from pathlib import Path
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from linearmodels.panel import PanelOLS

# Import custom modules
from src.data_loader import (
    load_who_pm25,
    load_unfccc_sectoral,
    load_eea_burden,
    load_gbd_yll,
    merge_nearest_years,
)
from src.models import (
    fit_ols,
    fit_panel_fe,
    save_model_outputs,
    fit_model_j_quadratic,
    fit_model_g_total_emissions,
    fit_model_e_lagged,
)
from src.audit import audit_panel_balance, check_model_e_gate

# Setup
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

log_path = OUTPUT_DIR / f"run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_file = open(log_path, "w", encoding="utf-8")
sys_stdout = sys.stdout

# Panel materialization log
panel_log_path = OUTPUT_DIR / "panel_materialization_log.txt"
panel_log = open(panel_log_path, "w", encoding="utf-8")


def log_print(*args, **kwargs):
    """Print to both console and log file."""
    print(*args, **kwargs)
    print(*args, file=log_file, **kwargs)


def log_panel_save(message: str):
    """Log panel materialization to dedicated log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    panel_log.write(f"[{timestamp}] {message}\n")
    panel_log.flush()


# =====================================================================
# Main Pipeline
# =====================================================================
def main(models_to_run: list[str]):
    """
    Execute selected models.

    Args:
        models_to_run: List of model identifiers: ['B'], ['C'], ['D'], ['G'], ['E'], ['J'], or ['all']
    """
    log_print(f"🚀 Starting Environmental-Health Pipeline")
    log_print(f"📋 Models to run: {', '.join(models_to_run)}")
    log_print(f"📊 Log file: {log_path}")
    log_print("=" * 70)

    results_summary = []

    # Load datasets once
    log_print("\n📂 Loading datasets...")
    who_pm25 = load_who_pm25()
    log_print(f"  ✓ WHO PM2.5: {len(who_pm25)} country-year records")

    eea_burden = load_eea_burden()
    log_print(f"  ✓ EEA Burden (DALY): {len(eea_burden)} country-year records")

    gbd_yll = load_gbd_yll()
    log_print(f"  ✓ GBD YLL: {len(gbd_yll)} country-year records")

    unfccc_sectoral = load_unfccc_sectoral()
    log_print(f"  ✓ UNFCCC Sectoral: {len(unfccc_sectoral)} country-year records")

    # Shared panel construction for Models C, G, E
    panel_c = None  # Will be built if needed

    # =====================================================================
    # Model B: PM2.5 → DALY (EEA health burden)
    # =====================================================================
    panel_b = None
    if "B" in models_to_run or "J" in models_to_run:
        log_print("\n" + "=" * 70)
        log_print("MODEL B: PM₂.₅ → DALY (EEA Health Burden)")
        log_print("=" * 70)
        log_print("Nearest-year merge (±3 years) between WHO PM2.5 and EEA DALY data")

        try:
            panel_b = merge_nearest_years(who_pm25, eea_burden, "iso3", "year", "year", tolerance=3)

            if len(panel_b) < 10:
                log_print(f"[WARN] Insufficient data: {len(panel_b)} observations. Skipping.")
            else:
                # Log transform
                panel_b["ln_pm25"] = np.log(panel_b["pm25"])
                panel_b["ln_daly"] = np.log(panel_b["daly"])

                # Remove infinities
                panel_b = panel_b.replace([np.inf, -np.inf], np.nan).dropna(
                    subset=["ln_pm25", "ln_daly"]
                )

                log_print(
                    f"✓ Panel B: {len(panel_b)} observations from {panel_b['country'].nunique()} countries"
                )

                # Save intermediate panel
                panel_b.to_csv(OUTPUT_DIR / "panel_b_health.csv", index=False)
                log_print(f"💾 Saved panel_b_health.csv")

                # Fit regression: ln(DALY) ~ ln(PM2.5)
                if "B" in models_to_run:
                    # Ensure clean data before saving estimation panel
                    clean_panel_b = panel_b[["iso3", "country", "ln_daly", "ln_pm25"]].copy()
                    clean_panel_b = clean_panel_b.dropna(subset=["ln_daly", "ln_pm25"])
                    
                    # Save estimation panel with exact naming convention
                    clean_panel_b.to_csv(OUTPUT_DIR / "panel_model_b_estimation.csv", index=False)
                    log_print(f"💾 Saved panel_model_b_estimation.csv (N={len(clean_panel_b)})")
                    log_panel_save(f"Model B: panel_model_b_estimation.csv (N={len(clean_panel_b)}, countries={clean_panel_b['country'].nunique()})")
                    
                    fit_ols(
                        panel_b["ln_daly"],
                        panel_b[["ln_pm25"]],
                        "ModelB_PM25_DALY",
                        results_summary,
                        log_print,
                    )
                    log_print("✓ Model B complete")

        except Exception as e:
            log_print(f"❌ Model B failed: {e}")

    # =====================================================================
    # Model C: Sectoral Emissions → PM2.5 (Panel with Fixed Effects)
    # =====================================================================
    if "C" in models_to_run or "G" in models_to_run or "E" in models_to_run:
        log_print("\n" + "=" * 70)
        log_print("MODEL C: Sectoral Emissions → PM₂.₅ (Multivariate Panel FE)")
        log_print("=" * 70)
        log_print("Panel regression with country & year fixed effects")
        log_print("Sectors: Energy, Manufacturing, Transport")

        try:
            # Merge WHO PM2.5 with UNFCCC sectoral data
            panel_c = who_pm25.merge(unfccc_sectoral, on=["iso3", "country", "year"], how="inner")

            if len(panel_c) < 20:
                log_print(f"[WARN] Insufficient data: {len(panel_c)} observations. Skipping.")
            else:
                # Log transform
                panel_c["ln_pm25"] = np.log(panel_c["pm25"])
                panel_c["ln_energy"] = np.log(panel_c["energy_emissions"])
                panel_c["ln_industry"] = np.log(panel_c["industry_emissions"])
                panel_c["ln_transport"] = np.log(panel_c["transport_emissions"])

                # Remove infinities and missing
                panel_c = panel_c.replace([np.inf, -np.inf], np.nan).dropna(
                    subset=["ln_pm25", "ln_energy", "ln_industry", "ln_transport"]
                )

                log_print(
                    f"✓ Panel C: {len(panel_c)} observations from {panel_c['country'].nunique()} countries, {panel_c['year'].nunique()} years"
                )

                # Save intermediate panel
                panel_c.to_csv(OUTPUT_DIR / "panel_c_sectoral.csv", index=False)
                log_print(f"💾 Saved panel_c_sectoral.csv")

                # Fit Model C if requested
                if "C" in models_to_run:
                    # Ensure clean data before saving
                    clean_panel_c = panel_c[["iso3", "country", "year", "ln_pm25", "ln_energy", "ln_industry", "ln_transport"]].copy()
                    clean_panel_c = clean_panel_c.dropna(subset=["ln_pm25", "ln_energy", "ln_industry", "ln_transport"])
                    
                    # Save estimation panel with exact naming convention
                    clean_panel_c.to_csv(OUTPUT_DIR / "panel_model_c_estimation.csv", index=False)
                    log_print(f"💾 Saved panel_model_c_estimation.csv (N={len(clean_panel_c)}, countries={clean_panel_c['country'].nunique()}, years={clean_panel_c['year'].nunique()})")
                    log_panel_save(f"Model C: panel_model_c_estimation.csv (N={len(clean_panel_c)}, countries={clean_panel_c['country'].nunique()}, years={clean_panel_c['year'].nunique()})")
                    
                    # Prepare for panel regression (set MultiIndex)
                    df_panel = clean_panel_c.set_index(["iso3", "year"]).sort_index()

                    # Variables for the model
                    y = df_panel["ln_pm25"]
                    X = df_panel[["ln_energy", "ln_industry", "ln_transport"]]

                    # FIXED: Use fit_panel_fe() for consistency
                    # NOTE: No constant added - absorbed by fixed effects
                    fit_panel_fe(
                        y,
                        X,
                        "ModelC_Sectoral_PM25",
                        results_summary,
                        entity_effects=True,
                        time_effects=True,
                        print_fn=log_print,
                    )
                    log_print("✓ Model C complete")

        except Exception as e:
            log_print(f"❌ Model C failed: {e}")

    # =====================================================================
    # Model D: PM2.5 → YLL (GBD mortality)
    # =====================================================================
    panel_d = None
    if "D" in models_to_run or "J" in models_to_run:
        log_print("\n" + "=" * 70)
        log_print("MODEL D: PM₂.₅ → YLL (GBD Mortality Burden)")
        log_print("=" * 70)
        log_print("Nearest-year merge (±3 years) between WHO PM2.5 and GBD YLL data")

        try:
            panel_d = merge_nearest_years(who_pm25, gbd_yll, "iso3", "year", "year", tolerance=3)

            if len(panel_d) < 10:
                log_print(f"[WARN] Insufficient data: {len(panel_d)} observations. Skipping.")
            else:
                # Log transform
                panel_d["ln_pm25"] = np.log(panel_d["pm25"])
                panel_d["ln_yll"] = np.log(panel_d["yll_asmr"])

                # Remove infinities
                panel_d = panel_d.replace([np.inf, -np.inf], np.nan).dropna(
                    subset=["ln_pm25", "ln_yll"]
                )

                log_print(
                    f"✓ Panel D: {len(panel_d)} observations from {panel_d['country'].nunique()} countries"
                )

                # Save intermediate panel
                panel_d.to_csv(OUTPUT_DIR / "panel_d_mortality.csv", index=False)
                log_print(f"💾 Saved panel_d_mortality.csv")

                # Fit regression: ln(YLL) ~ ln(PM2.5)
                if "D" in models_to_run:
                    # Save estimation panel with exact naming convention
                    estimation_panel_d = panel_d[["iso3", "country", "ln_yll", "ln_pm25"]].copy()
                    estimation_panel_d.to_csv(OUTPUT_DIR / "panel_model_d_estimation.csv", index=False)
                    log_print(f"💾 Saved panel_model_d_estimation.csv (N={len(estimation_panel_d)})")
                    log_panel_save(f"Model D: panel_model_d_estimation.csv (N={len(estimation_panel_d)}, countries={panel_d['country'].nunique()})")
                    
                    fit_ols(
                        panel_d["ln_yll"],
                        panel_d[["ln_pm25"]],
                        "ModelD_PM25_YLL",
                        results_summary,
                        log_print,
                    )
                    log_print("✓ Model D complete")

        except Exception as e:
            log_print(f"❌ Model D failed: {e}")

    # =====================================================================
    # Model G: Total Emissions → PM2.5 (Panel FE)
    # =====================================================================
    if "G" in models_to_run:
        log_print("\n" + "=" * 70)
        log_print("MODEL G: Total Emissions → PM₂.₅ (Panel FE)")
        log_print("=" * 70)
        log_print("Aggregated emissions to address sectoral multicollinearity")

        try:
            if panel_c is not None and len(panel_c) >= 20:
                fit_model_g_total_emissions(
                    panel_c,
                    "ModelG_TotalEmissions_PM25",
                    results_summary,
                    log_print,
                )
                log_print("✓ Model G complete")
            else:
                log_print("[WARN] Panel C not available. Skipping Model G.")

        except Exception as e:
            log_print(f"❌ Model G failed: {e}")

    # =====================================================================
    # Model E-lite: Lagged Total Emissions → PM2.5 (Panel FE, GATED)
    # =====================================================================
    if "E" in models_to_run:
        log_print("\n" + "=" * 70)
        log_print("MODEL E-LITE: Lagged Total Emissions → PM₂.₅ (Panel FE)")
        log_print("=" * 70)
        log_print("Tests temporal precedence with 1-year lag")
        log_print("GATED: Only runs if panel quality criteria are met")

        try:
            if panel_c is not None and len(panel_c) >= 20:
                # Check gate criteria BEFORE running model
                gate_passed, gate_diagnostics = check_model_e_gate(
                    panel_c,
                    max_sample_loss=0.30,
                    min_country_retention=0.67,
                    print_fn=log_print,
                    save_to_file=True,
                )

                if gate_passed:
                    fit_model_e_lagged(
                        panel_c,
                        "ModelE_LaggedTotalEmissions_PM25",
                        results_summary,
                        log_print,
                    )
                    log_print("✓ Model E-lite complete")
                else:
                    log_print(f"⚠️ Model E-lite SKIPPED: {gate_diagnostics['reason']}")
            else:
                log_print("[WARN] Panel C not available. Skipping Model E.")

        except Exception as e:
            log_print(f"❌ Model E-lite failed: {e}")

    # =====================================================================
    # Model J: Quadratic PM2.5 → Health (OLS)
    # =====================================================================
    if "J" in models_to_run:
        log_print("\n" + "=" * 70)
        log_print("MODEL J: Quadratic PM₂.₅ → Health (OLS)")
        log_print("=" * 70)
        log_print("Tests nonlinear dose-response relationship")
        log_print("Centered specification: z = ln(PM₂.₅) - mean(ln(PM₂.₅))")

        # Model J for DALY (uses panel_b)
        if panel_b is not None and len(panel_b) >= 10:
            try:
                log_print("\n--- Model J: PM₂.₅ → DALY (Quadratic) ---")
                fit_model_j_quadratic(
                    panel_b,
                    "ln_daly",
                    "ModelJ_PM25_DALY",
                    results_summary,
                    log_print,
                )
                log_print("✓ Model J (DALY) complete")
            except Exception as e:
                log_print(f"❌ Model J (DALY) failed: {e}")
        else:
            log_print("[WARN] Panel B not available. Skipping Model J (DALY).")

        # Model J for YLL (uses panel_d)
        if panel_d is not None and len(panel_d) >= 10:
            try:
                log_print("\n--- Model J: PM₂.₅ → YLL (Quadratic) ---")
                fit_model_j_quadratic(
                    panel_d,
                    "ln_yll",
                    "ModelJ_PM25_YLL",
                    results_summary,
                    log_print,
                )
                log_print("✓ Model J (YLL) complete")
            except Exception as e:
                log_print(f"❌ Model J (YLL) failed: {e}")
        else:
            log_print("[WARN] Panel D not available. Skipping Model J (YLL).")

    # =====================================================================
    # Summary
    # =====================================================================
    log_print("\n" + "=" * 70)
    log_print("SUMMARY")
    log_print("=" * 70)

    if results_summary:
        summary_df = pd.DataFrame(results_summary)
        summary_df.to_csv(OUTPUT_DIR / "summary_all_models.csv", index=False)
        log_print(f"\n✅ Results saved to: output/summary_all_models.csv")
        log_print(f"\n{summary_df.to_string()}")
    else:
        log_print("\n[WARN] No models were successfully fitted.")

    log_print(f"\n📊 All outputs saved to: {OUTPUT_DIR}")
    log_print(f"📝 Log saved to: {log_path}")
    log_print(f"💾 Panel materialization log: {panel_log_path}")
    log_print("=" * 70)

    # Run post-execution audit to verify what was created
    log_print("\n📋 Post-execution panel verification...")
    audit_panel_balance(print_fn=log_print, save_to_file=False)

    # Close panel log
    panel_log.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Environmental-Health Regression Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  B  PM₂.₅ → DALY (OLS, cross-sectional)
  C  Sectoral Emissions → PM₂.₅ (Panel FE)
  D  PM₂.₅ → YLL (OLS, cross-sectional)
  G  Total Emissions → PM₂.₅ (Panel FE, aggregated)
  E  Lagged Total Emissions → PM₂.₅ (Panel FE, GATED)
  J  Quadratic PM₂.₅ → Health (OLS, nonlinear)

Examples:
  poetry run python run.py              # Run all models
  poetry run python run.py --model B    # Run only Model B
  poetry run python run.py --model J    # Run quadratic models
  poetry run python run.py --model G    # Run total emissions model
        """,
    )
    parser.add_argument(
        "--model",
        choices=["B", "C", "D", "G", "E", "J"],
        default=None,
        help="Run specific model. If not specified, runs all models.",
    )

    args = parser.parse_args()

    # Determine which models to run
    if args.model:
        models_to_run = [args.model]
    else:
        models_to_run = ["B", "C", "D", "G", "E", "J"]

    try:
        main(models_to_run)
    finally:
        log_print(f"✅ Pipeline finished. Log: {log_path}")
        sys.stdout = sys_stdout
        log_file.close()
