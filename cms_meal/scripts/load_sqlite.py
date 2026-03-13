import os
import sqlite3

import pandas as pd

from config import CFG


def main() -> None:
    os.makedirs(CFG.processed_dir, exist_ok=True)
    db_path = CFG.sqlite_path
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    try:
        dim_country = pd.read_csv(os.path.join(CFG.processed_dir, "dim_country.csv"))
        dim_indicator = pd.read_csv(os.path.join(CFG.processed_dir, "dim_indicator.csv"))
        fact = pd.read_csv(os.path.join(CFG.processed_dir, "fact_country_year_indicator.csv"))

        dim_country.to_sql("dim_country", conn, index=False, if_exists="replace")
        dim_indicator.to_sql("dim_indicator", conn, index=False, if_exists="replace")
        fact.to_sql("fact_country_year_indicator", conn, index=False, if_exists="replace")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
