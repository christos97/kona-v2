"""
data_loader.py – Data Loading and Preprocessing Module
=======================================================

Handles loading, cleaning, and harmonizing datasets from:
- WHO Air Quality (PM2.5 concentrations)
- UNFCCC (sectoral GHG emissions)
- EEA Burden of Disease (DALYs)
- GBD 2021 (YLLs)
"""

from __future__ import annotations
import re
import numpy as np
import pandas as pd
import pycountry
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def normalize_country(name: str) -> str | None:
    """Convert country name to ISO3 code."""
    if not isinstance(name, str) or not name.strip():
        return None
    try:
        return pycountry.countries.lookup(name).alpha_3
    except Exception:
        return name.strip()


def leading_number(x) -> float:
    """Extract first numeric token from mixed strings."""
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.number)):
        return float(x)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(x).replace(",", ""))
    return float(m.group(0)) if m else np.nan


def load_who_pm25() -> pd.DataFrame:
    """
    Load WHO Air Quality data.

    Returns:
        DataFrame with columns: country, year, pm25, iso3
    """
    who = pd.read_csv(DATA_DIR / "who_air_quality.csv").rename(
        columns={"WHO Country Name": "country", "Measurement Year": "year", "PM2.5 (μg/m3)": "pm25"}
    )
    # Aggregate city-level to country-year means
    who_cty = who.groupby(["country", "year"], as_index=False)["pm25"].mean()
    who_cty["iso3"] = who_cty["country"].apply(normalize_country)
    who_cty = who_cty.dropna(subset=["iso3", "pm25"])
    return who_cty


def load_unfccc_sectoral() -> pd.DataFrame:
    """
    Load UNFCCC emissions with sectoral breakdown.

    Extracts key combustion sectors that are PM2.5-relevant:
    - 1.A.1 - Energy Industries (power generation)
    - 1.A.2 - Manufacturing Industries and Construction
    - 1.A.3 - Transport

    Returns:
        DataFrame with columns: country, year, iso3,
                                energy_emissions, industry_emissions, transport_emissions
    """
    unfccc = pd.read_csv(DATA_DIR / "unfccc_totals.csv")

    # Filter for key combustion sectors
    sectors = {
        "1.A.1 - Energy Industries": "energy_emissions",
        "1.A.2 - Manufacturing Industries and Construction": "industry_emissions",
        "1.A.3 - Transport": "transport_emissions",
    }

    # Filter and pivot
    df = unfccc[unfccc["Sector_name"].isin(sectors.keys())].copy()
    df["sector_var"] = df["Sector_name"].map(sectors)

    # Aggregate by country-year-sector
    agg = df.groupby(["Country", "Year", "sector_var"], as_index=False)["emissions"].sum()

    # Pivot to wide format
    pivot = agg.pivot_table(
        index=["Country", "Year"], columns="sector_var", values="emissions", aggfunc="sum"
    ).reset_index()

    pivot = pivot.rename(columns={"Country": "country", "Year": "year"})
    pivot["iso3"] = pivot["country"].apply(normalize_country)

    # Fill missing sectors with NaN (some countries may not have all sectors)
    for col in sectors.values():
        if col not in pivot.columns:
            pivot[col] = np.nan

    return pivot.dropna(subset=["iso3"])


def load_unfccc_totals() -> pd.DataFrame:
    """
    Load UNFCCC total emissions (for reference/comparison).

    Returns:
        DataFrame with columns: country, year, iso3, total_emissions_kt_unfccc
    """
    unfccc = pd.read_csv(DATA_DIR / "unfccc_totals.csv")

    # Filter for total emissions only
    totals = unfccc[unfccc["Sector_name"] == "Total emissions (UNFCCC)"].copy()

    agg = totals.groupby(["Country", "Year"], as_index=False)["emissions"].sum()
    agg = agg.rename(
        columns={"Country": "country", "Year": "year", "emissions": "total_emissions_kt_unfccc"}
    )
    agg["iso3"] = agg["country"].apply(normalize_country)

    return agg.dropna(subset=["iso3"])


def load_eea_burden() -> pd.DataFrame:
    """
    Load EEA Burden of Disease data (DALYs attributable to PM2.5).

    Returns:
        DataFrame with columns: country, year, daly, iso3
    """
    burden = pd.read_csv(DATA_DIR / "eea_burden_disease.csv")

    # Filter for relevant records
    burden = burden[
        (burden["Degree Of Urbanisation"] == "All Areas (incl.unclassified)")
        & (burden["Air Pollutant"] == "PM2.5")
        & (burden["Health Indicator"] == "Disability-Adjusted Life Years (DALY)")
    ]

    # Aggregate by country-year
    burden_cty = (
        burden.groupby(["Country Or Territory", "Year"], as_index=False)["Value"]
        .sum()
        .rename(columns={"Country Or Territory": "country", "Year": "year", "Value": "daly"})
    )
    burden_cty["iso3"] = burden_cty["country"].apply(normalize_country)

    return burden_cty.dropna(subset=["iso3", "daly"])


def load_gbd_yll() -> pd.DataFrame:
    """
    Load GBD 2021 Years of Life Lost (YLL) data.

    Returns:
        DataFrame with columns: country, year, yll_asmr, iso3
    """
    gbd = pd.read_csv(DATA_DIR / "health_gbd2021_yll_bothsex_asmr.csv").rename(
        columns={"location_name": "country"}
    )

    # Find year columns (e.g., "2019", "2010 estimate")
    year_cols = [c for c in gbd.columns if re.match(r"^\d{4}", c)]

    gbd_long = gbd.melt(
        id_vars=["country"], value_vars=year_cols, var_name="year_raw", value_name="yll_asmr"
    )
    gbd_long["year"] = gbd_long["year_raw"].str.extract(r"(\d{4})").astype(float)
    gbd_long["yll_asmr"] = gbd_long["yll_asmr"].apply(leading_number)
    gbd_long["iso3"] = gbd_long["country"].apply(normalize_country)

    return gbd_long[["country", "year", "yll_asmr", "iso3"]].dropna(subset=["iso3", "yll_asmr"])


def merge_nearest_years(
    df_left: pd.DataFrame,
    df_right: pd.DataFrame,
    on_key: str,
    left_year: str,
    right_year: str,
    tolerance: int = 3,
) -> pd.DataFrame:
    """
    Nearest-year join with ±tolerance window.

    For each row in df_left, finds the closest matching year in df_right
    within the tolerance window.
    """
    merged = []
    for _, row in df_left.iterrows():
        subset = df_right[df_right[on_key] == row[on_key]]
        if subset.empty:
            continue
        subset = subset.assign(diff=(subset[right_year] - row[left_year]).abs())
        subset = subset[subset["diff"] <= tolerance]
        if len(subset):
            best = subset.sort_values("diff").iloc[0].to_dict()
            merged.append({**row.to_dict(), **best})

    return pd.DataFrame(merged)
