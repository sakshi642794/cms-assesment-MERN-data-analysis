import os
import re

import pandas as pd

from config import CFG

ISO3_RE = re.compile(r"^[A-Z]{3}$")

INDICATOR_UNITS = {
    "SP.POP.TOTL": "people",
    "NY.GDP.PCAP.CD": "current US$",
    "SH.XPD.CHEX.PC.CD": "current US$",
    "WHOSIS_000001": "years",
    "MDG_0000000001": "per 1,000 live births",
}

FACT_RENAME = {
    "country_iso3": "iso3",
    "country_name": "country",
    "year": "year",
    "indicator_code": "ind_code",
    "indicator_name": "indicator",
    "source": "source",
    "unit": "unit",
    "value": "value",
}

DIM_COUNTRY_RENAME = {
    "country_iso3": "iso3",
    "country_name": "country",
}

DIM_INDICATOR_RENAME = {
    "indicator_code": "ind_code",
    "indicator_name": "indicator",
    "source": "source",
    "unit": "unit",
}


def load_raw() -> pd.DataFrame:
    frames = []
    wb_path = os.path.join(CFG.raw_dir, "worldbank_all.csv")
    who_path = os.path.join(CFG.raw_dir, "who_all.csv")

    if os.path.exists(wb_path):
        frames.append(pd.read_csv(wb_path))
    if os.path.exists(who_path):
        frames.append(pd.read_csv(who_path))

    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    return df


def standardize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Fix formats
    df["country_iso3"] = df["country_iso3"].astype(str).str.upper().str.strip()
    df["country_name"] = df["country_name"].astype(str).str.strip()
    df["indicator_code"] = df["indicator_code"].astype(str).str.strip()
    df["indicator_name"] = df["indicator_name"].astype(str).str.strip()
    df["source"] = df["source"].astype(str).str.strip()

    # Normalize literal "nan" strings to missing
    df["country_name"] = df["country_name"].replace({"": None, "nan": None, "NaN": None})
    df["indicator_name"] = df["indicator_name"].replace({"": None, "nan": None, "NaN": None})

    # Keep valid ISO3 only
    df = df[df["country_iso3"].apply(lambda x: bool(ISO3_RE.match(x)))]

    # Coerce numeric types
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Drop missing or out-of-range
    df = df.dropna(subset=["year", "value"])
    df = df[(df["year"] >= CFG.start_year) & (df["year"] <= CFG.end_year)]

    # Attach indicator units to prevent unit confusion downstream
    df["unit"] = df["indicator_code"].map(INDICATOR_UNITS)

    return df


def build_dimensions(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    dim_country = (
        df[["country_iso3", "country_name"]]
        .dropna(subset=["country_iso3", "country_name"])
        .drop_duplicates()
        .sort_values("country_iso3")
    )
    dim_indicator = (
        df[["indicator_code", "indicator_name", "source", "unit"]]
        .dropna(subset=["indicator_code", "indicator_name"])
        .drop_duplicates()
        .sort_values("indicator_code")
    )
    return dim_country, dim_indicator


def fill_names(fact: pd.DataFrame, dim_country: pd.DataFrame, dim_indicator: pd.DataFrame) -> pd.DataFrame:
    fact = fact.merge(dim_country, on="country_iso3", how="left", suffixes=("", "_dim"))
    fact["country_name"] = fact["country_name"].fillna(fact["country_name_dim"])
    fact = fact.drop(columns=["country_name_dim"])

    fact = fact.merge(dim_indicator, on="indicator_code", how="left", suffixes=("", "_dim"))
    fact["indicator_name"] = fact["indicator_name"].fillna(fact["indicator_name_dim"])
    fact = fact.drop(columns=["indicator_name_dim", "source_dim", "unit_dim"])

    return fact


def main() -> None:
    os.makedirs(CFG.processed_dir, exist_ok=True)
    df = load_raw()
    if df.empty:
        print("No raw data found. Run extract scripts first.")
        return

    df = standardize(df)
    fact = df[[
        "country_iso3",
        "country_name",
        "year",
        "indicator_code",
        "indicator_name",
        "source",
        "unit",
        "value",
    ]].copy()

    # Remove duplicates on natural key
    fact = fact.drop_duplicates(subset=["country_iso3", "year", "indicator_code"])

    # Build dims, then fill missing names from dims
    dim_country, dim_indicator = build_dimensions(fact)
    fact = fill_names(fact, dim_country, dim_indicator)

    # Drop rows that still have missing core labels after fill
    fact = fact.dropna(subset=["country_name", "indicator_name"])

    # Remove any duplicates reintroduced by merges
    fact = fact.drop_duplicates(subset=["country_iso3", "year", "indicator_code"])

    # Rebuild dims after fill for consistency
    dim_country, dim_indicator = build_dimensions(fact)

    # Rename columns to short labels for output
    fact_out = fact.rename(columns=FACT_RENAME)[
        ["iso3", "country", "year", "ind_code", "indicator", "source", "unit", "value"]
    ]
    dim_country_out = dim_country.rename(columns=DIM_COUNTRY_RENAME)[["iso3", "country"]]
    dim_indicator_out = dim_indicator.rename(columns=DIM_INDICATOR_RENAME)[
        ["ind_code", "indicator", "source", "unit"]
    ]

    fact_path = os.path.join(CFG.processed_dir, "fact_country_year_indicator.csv")
    dim_country_out.to_csv(os.path.join(CFG.processed_dir, "dim_country.csv"), index=False)
    dim_indicator_out.to_csv(os.path.join(CFG.processed_dir, "dim_indicator.csv"), index=False)
    fact_out.to_csv(fact_path, index=False)


if __name__ == "__main__":
    main()
