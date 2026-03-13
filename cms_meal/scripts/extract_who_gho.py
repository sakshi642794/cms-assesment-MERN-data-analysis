import os
from typing import List

import pandas as pd
import requests

from config import CFG

WHO_BASE = "https://ghoapi.azureedge.net/api"


def fetch_indicator(indicator: str, start_year: int, end_year: int) -> List[dict]:
    rows: List[dict] = []
    skip = 0
    top = 2000
    max_rows = 200000

    filter_encoded = f"TimeDim%20ge%20{start_year}%20and%20TimeDim%20le%20{end_year}"
    headers = {"User-Agent": "cms-meal-data-associate/1.0"}

    while True:
        query = f"$top={top}&$skip={skip}&$filter={filter_encoded}"
        url = f"{WHO_BASE}/{indicator}?{query}"
        resp = requests.get(url, headers=headers, timeout=60)
        if resp.status_code == 400 and top > 1000:
            top = 1000
            continue
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("value", []) if isinstance(data, dict) else []
        if not batch:
            break
        rows.extend(batch)
        if len(rows) >= max_rows:
            break
        if len(batch) < top:
            break
        skip += top
    return rows


def normalize(records: List[dict], indicator_code: str) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame.from_records(records)
    df["country_iso3"] = df.get("SpatialDim")
    df["country_name"] = df.get("SpatialDimName")
    df["year"] = pd.to_numeric(df.get("TimeDim"), errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df.get("Value"), errors="coerce")
    df["indicator_code"] = indicator_code
    df["indicator_name"] = df.get("IndicatorName")
    df["source"] = "WHO GHO"

    keep = ["country_iso3", "country_name", "year", "value", "indicator_code", "indicator_name", "source"]
    df = df[keep]
    df = df.dropna(subset=["country_iso3", "year"])
    return df


def main() -> None:
    os.makedirs(CFG.raw_dir, exist_ok=True)
    all_frames = []
    for code in CFG.who_indicators:
        records = fetch_indicator(code, CFG.start_year, CFG.end_year)
        df = normalize(records, code)
        out_path = os.path.join(CFG.raw_dir, f"who_{code}.csv")
        df.to_csv(out_path, index=False)
        all_frames.append(df)

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined.to_csv(os.path.join(CFG.raw_dir, "who_all.csv"), index=False)


if __name__ == "__main__":
    main()
