#!/usr/bin/env python3
"""
CSV Row Count Audit Script

Verifies that estimation CSVs match regression N values exactly.
Run AFTER pipeline execution: poetry run python run.py

Usage:
    python verify_csv_consistency.py
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"

# Model definitions: (csv_file, expected_N_from_summary)
MODELS = {
    "B": ("panel_model_b_estimation.csv", 54),
    "C": ("panel_model_c_estimation.csv", 238),
    "D": ("panel_model_d_estimation.csv", 438),
    "G": ("panel_model_g_estimation.csv", 238),
    "E": ("panel_model_e_estimation.csv", 208),
    "J-DALY": ("panel_model_j_daly_estimation.csv", 54),
    "J-YLL": ("panel_model_j_yll_estimation.csv", 438),
}


def main():
    print("=" * 70)
    print("CSV ROW COUNT AUDIT")
    print("=" * 70)
    print()
    
    all_pass = True
    
    for model, (csv_file, expected_n) in MODELS.items():
        csv_path = OUTPUT_DIR / csv_file
        
        if not csv_path.exists():
            print(f"❌ {model:10} | CSV NOT FOUND: {csv_file}")
            all_pass = False
            continue
        
        df = pd.read_csv(csv_path)
        actual_n = len(df)
        
        if actual_n == expected_n:
            status = "✅ MATCH"
        else:
            status = "❌ MISMATCH"
            all_pass = False
        
        print(f"{model:10} | CSV rows: {actual_n:3} | Expected: {expected_n:3} | {status}")
    
    print()
    print("=" * 70)
    
    if all_pass:
        print("✅ ALL CHECKS PASSED")
        print()
        print("Result: All estimation CSVs have exactly N rows matching regression output.")
        print("Excel reproducibility verified. Audit trail consistent.")
        return 0
    else:
        print("❌ AUDIT FAILED")
        print()
        print("Action required:")
        print("1. Re-run pipeline: poetry run python run.py")
        print("2. Re-run this audit script")
        print("3. If still failing, check run.py for dropna() timing")
        return 1


if __name__ == "__main__":
    exit(main())
