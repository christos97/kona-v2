"""
run.py – Streamlined Environmental-Health Regression Pipeline (3 Models)
========================================================================

Focused analysis with 3 core models:
  B. PM2.5 → DALY (EEA health burden, nearest-year merge ±3)
  C. Sectoral Emissions → PM2.5 (multivariate panel with fixed effects)
  D. PM2.5 → YLL (GBD mortality burden, nearest-year merge ±3)

Usage:
  poetry run python run.py [--model B|C|D]  (default: run all)

Examples:
  poetry run python run.py              # Run all 3 models
  poetry run python run.py --model B    # Run only Model B
  poetry run python run.py --model C    # Run only Model C
  poetry run python run.py --model D    # Run only Model D
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
from src.models import fit_ols, fit_panel_fe, save_model_outputs

# Setup
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

log_path = OUTPUT_DIR / f"run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_file = open(log_path, "w", encoding="utf-8")
sys_stdout = sys.stdout


def log_print(*args, **kwargs):
    """Print to both console and log file."""
    print(*args, **kwargs)
    print(*args, file=log_file, **kwargs)


# =====================================================================
# Main Pipeline
# =====================================================================
def main(models_to_run: list[str]):
    """
    Execute selected models.

    Args:
        models_to_run: List of model identifiers: ['B'], ['C'], ['D'], or ['B', 'C', 'D']
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

    # =====================================================================
    # Model B: PM2.5 → DALY (EEA health burden)
    # =====================================================================
    if "B" in models_to_run:
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
    if "C" in models_to_run:
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

                # Prepare for panel regression (set MultiIndex)
                df_panel = panel_c.set_index(["iso3", "year"]).sort_index()

                # Variables for the model
                y = df_panel["ln_pm25"]
                X = df_panel[["ln_energy", "ln_industry", "ln_transport"]]

                # Fit panel OLS with 2-way fixed effects
                Xc = sm.add_constant(X)
                model_c = PanelOLS(
                    y,
                    Xc,
                    entity_effects=True,
                    time_effects=True,
                )
                result_c = model_c.fit(cov_type="clustered", cluster_entity=True)

                log_print(result_c.summary)

                # Save outputs
                save_model_outputs(result_c, "ModelC_Sectoral_PM25", results_summary, is_panel=True)
                log_print("✓ Model C complete")

        except Exception as e:
            log_print(f"❌ Model C failed: {e}")

    # =====================================================================
    # Model D: PM2.5 → YLL (GBD mortality)
    # =====================================================================
    if "D" in models_to_run:
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
    log_print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Environmental-Health Regression Pipeline (3 Models)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  poetry run python run.py              # Run all 3 models
  poetry run python run.py --model B    # Run only Model B
  poetry run python run.py --model C    # Run only Model C
  poetry run python run.py --model D    # Run only Model D
        """,
    )
    parser.add_argument(
        "--model",
        choices=["B", "C", "D"],
        default=None,
        help="Run specific model(s). If not specified, runs all 3.",
    )

    args = parser.parse_args()

    # Determine which models to run
    if args.model:
        models_to_run = [args.model]
    else:
        models_to_run = ["B", "C", "D"]

    try:
        main(models_to_run)
    finally:
        log_print(f"✅ Pipeline finished. Log: {log_path}")
        sys.stdout = sys_stdout
        log_file.close()
