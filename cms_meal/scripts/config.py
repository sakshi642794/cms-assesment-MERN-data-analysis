from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    start_year: int = 2000
    end_year: int = 2023
    worldbank_indicators = {
        "SP.POP.TOTL": "Population, total",
        "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
        "SH.XPD.CHEX.PC.CD": "Current health expenditure per capita (current US$)",
    }
    who_indicators = {
        "WHOSIS_000001": "Life expectancy at birth (years)",
        "MDG_0000000001": "Infant mortality rate (per 1,000 live births)",
    }

    raw_dir = "data/raw"
    processed_dir = "data/processed"
    sqlite_path = "data/processed/cms_meal.db"

CFG = Config()
