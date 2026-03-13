import os
from typing import List

import pandas as pd

from config import CFG
from utils import get_json, make_session

WB_BASE = "https://api.worldbank.org/v2"


def fetch_indicator(indicator: str, start_year: int, end_year: int) -> List[dict]:
    session = make_session()
    page = 1
    rows: List[dict] = []
    while True:
        url = f"{WB_BASE}/country/all/indicator/{indicator}"
        params = {
            "format": "json",
            "per_page": 20000,
            "page": page,
            "date": f"{start_year}:{end_year}",
        }
        data = get_json(session, url, params=params)
        if not isinstance(data, list) or len(data) < 2:
            break
        meta, records = data[0], data[1]
        rows.extend(records)
        if page >= int(meta.get("pages", 0)):
            break
        page += 1
    return rows


def normalize(records: List[dict], indicator_code: str) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame.from_records(records)
    df = df[["country", "countryiso3code", "date", "value", "indicator"]]
    df["country_name"] = df["country"].apply(lambda x: x.get("value") if isinstance(x, dict) else None)
    df["indicator_name"] = df["indicator"].apply(lambda x: x.get("value") if isinstance(x, dict) else None)
    df["country_iso3"] = df["countryiso3code"]
    df["year"] = pd.to_numeric(df["date"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["indicator_code"] = indicator_code
    df["source"] = "World Bank"
    df = df.drop(columns=["country", "countryiso3code", "date", "indicator"])
    df = df.dropna(subset=["country_iso3", "year"])
    return df


def main() -> None:
    os.makedirs(CFG.raw_dir, exist_ok=True)
    all_frames = []
    for code in CFG.worldbank_indicators:
        records = fetch_indicator(code, CFG.start_year, CFG.end_year)
        df = normalize(records, code)
        out_path = os.path.join(CFG.raw_dir, f"worldbank_{code}.csv")
        df.to_csv(out_path, index=False)
        all_frames.append(df)

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined.to_csv(os.path.join(CFG.raw_dir, "worldbank_all.csv"), index=False)


if __name__ == "__main__":
    main()
