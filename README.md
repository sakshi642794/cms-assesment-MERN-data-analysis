# CMS MEAL Data Associate Assignment

## Overview
This project delivers a small, end-to-end analytics workflow for MEAL decision-making. It integrates public data from the World Bank and WHO Global Health Observatory (GHO), standardizes indicators by country and year, loads a simple analytical model, and prepares data for Power BI dashboards.

## Data sources
- World Bank Open Data API
- WHO Global Health Observatory (GHO) OData API

## Indicators used 
World Bank:
- `SP.POP.TOTL` Population, total
- `NY.GDP.PCAP.CD` GDP per capita (current US$)
- `SH.XPD.CHEX.PC.CD` Current health expenditure per capita (current US$)

WHO GHO:
- `WHOSIS_000001` Life expectancy at birth (years)
- `MDG_0000000001` Infant mortality rate (per 1,000 live births)


## Repository layout
- `scripts/` Extraction, transform, and load steps
- `data/raw/` Raw extracts
- `data/processed/` Cleaned tables and SQLite database
- `sql/` Model, queries, and validation checks
- `dashboard/` Power BI dashboard file
- `slides/` Presentation deck

## Setup
```bash
pip install -r requirements.txt
```

## Run the pipeline
```bash
python scripts/extract_worldbank.py
python scripts/extract_who_gho.py
python scripts/transform_integration.py
python scripts/load_sqlite.py
```

Or run everything in one step:
```bash
python scripts/pipeline.py
```

Outputs:
- Raw CSVs: `data/raw/`
- Processed model tables: `data/processed/`
- SQLite database: `data/processed/cms_meal.db`
- Power BI file: `dashboard/cms dashboard.pbix`

## Data model
Star schema:
- `dim_country`
- `dim_indicator`
- `fact_country_year_indicator`

See `sql/model.sql`, `sql/queries.sql`, and `sql/validation.sql` for examples.

## Assumptions and limitations
- Country-level data only; non-country aggregates are filtered out.
- Missing values are kept as nulls; analysis should handle gaps.
- Indicator metadata may differ across sources; names are standardized where possible.
- Time range defaults to 2000-2023; adjust in `scripts/config.py` as needed.
- WHO API pagination uses `$top=2000` per request.

## insights
- Relationship between GDP per capita and life expectancy by country.
- Population growth trends by country over time.
- Countries with improving life expectancy despite low GDP per capita.

## Dashboard notes
- Primary users: MEAL leads and program teams
- Key KPIs: life expectancy, infant mortality, GDP per capita, health expenditure per capita, population
- Core views: time trends, country comparisons, and indicator correlations

This repository is a proof-of-concept for MEAL analytics and can be extended with additional indicators, geographies, or program data.

